from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "exceptionmodel" ADD "media_id" UUID;
        ALTER TABLE "exceptionmodel" ADD CONSTRAINT "fk_exceptio_media_ec50ac77" FOREIGN KEY ("media_id") REFERENCES "media" ("id") ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "exceptionmodel" DROP CONSTRAINT "fk_exceptio_media_ec50ac77";
        ALTER TABLE "exceptionmodel" DROP COLUMN "media_id";"""
