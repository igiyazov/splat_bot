from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "exceptionmodel" ADD "user_tg" VARCHAR(150);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "exceptionmodel" DROP COLUMN "user_tg";"""
