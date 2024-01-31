from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "first_name" VARCHAR(150),
    "last_name" VARCHAR(150),
    "username" VARCHAR(150) NOT NULL,
    "tg_id" VARCHAR(150) NOT NULL UNIQUE,
    "phone_number" VARCHAR(150),
    "language" VARCHAR(2) NOT NULL  DEFAULT 'ru'
);
CREATE TABLE IF NOT EXISTS "check" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "lg" VARCHAR(150) NOT NULL UNIQUE,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "product" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(150) NOT NULL,
    "count" INT NOT NULL,
    "bill_id" UUID REFERENCES "check" ("id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
