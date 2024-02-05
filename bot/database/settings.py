import logging

from tortoise import Tortoise

DEBUG = False

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# DATABASE_URL = "postgres://postgres:postgres@postgres/bot"
# DATABASE_URL = "postgres://postgres:postgres@localhost/bot"
# DATABASE_URL = "postgres://doadmin:AVNS_ItZsZZbGehhcbgnddVP@db-postgresql-blr1-66051-do-user-15736215-0.c.db.ondigitalocean.com:25060/defaultdb"

if DEBUG:
    DATABASE_URL = "postgres://postgres:postgres@localhost/bot"
    DB_URL = "postgresql://postgres:postgres@localhost/bot"
else:
    DATABASE_URL = "postgres://doadmin:AVNS_ItZsZZbGehhcbgnddVP@db-postgresql-blr1-66051-do-user-15736215-0.c.db.ondigitalocean.com:25060/defaultdb"
    DB_URL = "postgresql://doadmin:AVNS_bpGNVDCMhWoYXlr8g4u@db-postgresql-blr1-55795-persistence-do-user-15736215-0.c.db.ondigitalocean.com:25060/defaultdb"


TORTOISE_MODELS_LIST = ['database.models', 'aerich.models']
TORTOISE_ORM = {
    'connections': {'default': DATABASE_URL},
    'apps': {
        'models': {
            'models': TORTOISE_MODELS_LIST,
            'default_connection': 'default',
        },
    },
}


async def init_db():
    logger.info('Connecting to Postgres')
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={'models': TORTOISE_MODELS_LIST},
    )
    # await Tortoise.generate_schemas()
