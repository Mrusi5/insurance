
from tortoise import Tortoise

async def init_db():
    await Tortoise.init(
        db_url="postgres://postgres:password@db_postgres:5432/postgres",
        modules={"models": ["src.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_asyncio_connections()