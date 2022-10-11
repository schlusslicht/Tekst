from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from textrig.config import TextRigConfig, get_config


_cfg: TextRigConfig = get_config()
_client: AsyncIOMotorClient = AsyncIOMotorClient(_cfg.db.get_uri())
_db = _client[_cfg.db.name]


# database object getter for use as a dependency
def get_db() -> Database:

    return _db
