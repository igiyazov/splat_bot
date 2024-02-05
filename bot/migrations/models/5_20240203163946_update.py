from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "exceptionmodel" ADD "user_language" VARCHAR(2) NOT NULL  DEFAULT 'ru';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "exceptionmodel" DROP COLUMN "user_language";"""
