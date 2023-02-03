import os

# from beanie import PydanticObjectId
from textrig import logging


# import re

# from textrig.db import _ID_KEY_PATTERN


def test_logging_setup_without_errors():
    logging.setup_logging()
    logging.log.info("foo bar")
    os.environ["SERVER_SOFTWARE"] = "gunicorn"
    logging.setup_logging()
    logging.log.info("foo bar")


# def test_id_key_pattern():
#     assert bool(re.match(_ID_KEY_PATTERN, "id"))
#     assert bool(re.match(_ID_KEY_PATTERN, "_id"))
#     assert bool(re.match(_ID_KEY_PATTERN, "parentId"))
#     assert bool(re.match(_ID_KEY_PATTERN, "parentId"))
#     assert not bool(re.match(_ID_KEY_PATTERN, "parentIde"))
#     assert not bool(re.match(_ID_KEY_PATTERN, "parent_id_foo"))


# def test_for_mongo_request():
#     req = {
#         "id": "637b94cb6bc85f7410a49bc9",
#         "_id": "637b94cb6bc85f7410a49bc9",
#         "parentId": "637b94cb6bc85f7410a49bc9",
#         "nested": {"_id": "637b94cb6bc85f7410a49bc9"},
#     }
#     req = for_mongo(req)
#     assert type(req.get("_id")) == PyObjectId
#     assert "parentId" in req
#     assert type(req.get("parentId")) == PyObjectId
#     assert type(req.get("nested").get("_id")) == PyObjectId
