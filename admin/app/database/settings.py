import logging

from tortoise import Tortoise


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

DATABASE_URL = "postgres://postgres:postgres@postgres/bot"

TORTOISE_MODELS_LIST = ['app.database.models',]
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
    await Tortoise.generate_schemas()
