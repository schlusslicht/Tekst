from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import Eq, In, Not
from fastapi import APIRouter, Path, Query, status

from tekst import errors
from tekst.auth import OptionalUserDep, UserDep
from tekst.models.content import ContentBaseDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument
from tekst.resources import (
    AnyContentCreateBody,
    AnyContentDocument,
    AnyContentReadBody,
    AnyContentUpdateBody,
    resource_types_mgr,
)
from tekst.utils.html import sanitize_model_html


# initialize content router
router = APIRouter(
    prefix="/contents",
    tags=["contents"],
)


@router.post(
    "",
    response_model=AnyContentReadBody,
    status_code=status.HTTP_201_CREATED,
    responses=errors.responses(
        [
            errors.E_403_FORBIDDEN,
            errors.E_409_CONTENT_CONFLICT,
        ]
    ),
)
async def create_content(
    content: AnyContentCreateBody,
    user: UserDep,
) -> AnyContentDocument:
    # check if the resource this content belongs to is writable by user
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == content.resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    )
    if not resource:
        raise errors.E_403_FORBIDDEN
    # check for duplicates
    if await ContentBaseDocument.find_one(
        ContentBaseDocument.resource_id == content.resource_id,
        ContentBaseDocument.location_id == content.location_id,
        with_children=True,
    ).exists():
        raise errors.E_409_CONTENT_CONFLICT

    # if the content has a "html" field, sanitize it
    content = sanitize_model_html(content)

    # call the resource's and text's hooks for changed contents
    await resource.contents_changed_hook()
    await (await TextDocument.get(resource.text_id)).contents_changed_hook()

    # create the content document and return it
    return (
        await resource_types_mgr.get(content.resource_type)
        .content_model()
        .document_model()
        .model_from(content)
        .create()
    )


@router.get(
    "/{id}",
    response_model=AnyContentReadBody,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_CONTENT_NOT_FOUND,
        ]
    ),
)
async def get_content(
    content_id: Annotated[PydanticObjectId, Path(alias="id")], user: OptionalUserDep
) -> AnyContentDocument:
    """A generic route for retrieving a content by ID from the database"""
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    # check if the resource this content belongs to is readable by user
    resource_read_allowed = content_doc and (
        await ResourceBaseDocument.find_one(
            ResourceBaseDocument.id == content_doc.resource_id,
            await ResourceBaseDocument.access_conditions_read(user),
            with_children=True,
        ).exists()
    )
    if not content_doc or not resource_read_allowed:
        raise errors.E_404_CONTENT_NOT_FOUND
    return content_doc


@router.patch(
    "/{id}",
    response_model=AnyContentReadBody,
    status_code=status.HTTP_200_OK,
    responses=errors.responses(
        [
            errors.E_404_CONTENT_NOT_FOUND,
            errors.E_400_CONTENT_ID_MISMATCH,
            errors.E_400_CONTENT_TYPE_MISMATCH,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def update_content(
    content_id: Annotated[PydanticObjectId, Path(alias="id")],
    updates: AnyContentUpdateBody,
    user: UserDep,
) -> AnyContentDocument:
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    if not content_doc:
        raise errors.E_404_CONTENT_NOT_FOUND
    # check if content's resource ID matches updates' resource ID (if any)
    if updates.resource_id and content_doc.resource_id != updates.resource_id:
        raise errors.E_400_CONTENT_ID_MISMATCH
    # check if content's resource type matches updates' resource type
    if updates.resource_type != content_doc.resource_type:
        raise errors.E_400_CONTENT_TYPE_MISMATCH
    # check if the resource this content belongs to is writable by user
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == content_doc.resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    )
    if not resource:
        raise errors.E_403_FORBIDDEN

    # if the updated content has a "html" field, sanitize it
    updates = sanitize_model_html(updates)

    # call the resource's and text's hooks for changed contents
    await resource.contents_changed_hook()
    await (await TextDocument.get(resource.text_id)).contents_changed_hook()

    # apply updates, return the updated document
    return await content_doc.apply_updates(
        updates, exclude={"id", "resource_id", "location_id", "resource_type"}
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=errors.responses(
        [
            errors.E_404_CONTENT_NOT_FOUND,
            errors.E_403_FORBIDDEN,
        ]
    ),
)
async def delete_content(
    user: UserDep,
    content_id: Annotated[PydanticObjectId, Path(alias="id")],
) -> None:
    content_doc = await ContentBaseDocument.get(content_id, with_children=True)
    if not content_doc:
        raise errors.E_404_CONTENT_NOT_FOUND
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == content_doc.resource_id,
        await ResourceBaseDocument.access_conditions_write(user),
        with_children=True,
    )
    if not resource:
        raise errors.E_403_FORBIDDEN

    # call the resource's and text's hooks for changed contents
    await resource.contents_changed_hook()
    await (await TextDocument.get(resource.text_id)).contents_changed_hook()

    # all fine, delete content
    await content_doc.delete()


@router.get(
    "",
    response_model=list[AnyContentReadBody],
    status_code=status.HTTP_200_OK,
)
async def find_contents(
    user: OptionalUserDep,
    resource_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="res",
            description="ID (or list of IDs) of resource(s) to return content data for",
        ),
    ] = [],
    location_ids: Annotated[
        list[PydanticObjectId],
        Query(
            alias="location",
            description="ID (or list of IDs) of location(s) to return content data for",
        ),
    ] = [],
    limit: Annotated[int, Query(description="Return at most <limit> items")] = 4096,
) -> list[AnyContentDocument]:
    """
    Returns a list of all resource contents matching the given criteria.

    Respects restricted resources and inactive texts.
    As the resulting list may contain contents of different types, the
    returned content objects cannot be typed to their precise resource content type.
    """

    # preprocess resource_ids to add IDs of original resources in case we have versions
    if resource_ids:
        resource_ids.append(
            [
                res.original_id
                for res in await ResourceBaseDocument.find(
                    In(ResourceBaseDocument.id, resource_ids),
                    Not(Eq(ResourceBaseDocument.original_id, None)),
                    with_children=True,
                ).to_list()
            ]
        )

    # get readable resources as a subset of the requested ones (might be all resources)
    readable_resources = await ResourceBaseDocument.find(
        In(ResourceBaseDocument.id, resource_ids) if resource_ids else {},
        await ResourceBaseDocument.access_conditions_read(user),
        with_children=True,
    ).to_list()

    # get contents matching the given criteria
    return (
        await ContentBaseDocument.find(
            In(ContentBaseDocument.resource_id, resource_ids) if resource_ids else {},
            In(ContentBaseDocument.location_id, location_ids) if location_ids else {},
            In(
                ContentBaseDocument.resource_id,
                [resource.id for resource in readable_resources],
            ),
            with_children=True,
        )
        .limit(limit)
        .to_list()
    )
