from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "exceptionmodel" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "type" VARCHAR(20) NOT NULL  DEFAULT 'ofd',
    "path" VARCHAR(350),
    "success" BOOL NOT NULL  DEFAULT False,
    "solved" BOOL NOT NULL  DEFAULT False,
    "result" VARCHAR(150),
    "user_id" UUID REFERENCES "user" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "exceptionmodel"."type" IS 'OFD: ofd';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "exceptionmodel";"""
