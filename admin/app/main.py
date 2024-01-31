import os
from typing import Union

import aioredis
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider

from app.database.models import Admin

from app.database.settings import init_db

login_provider = UsernamePasswordProvider(
    admin_model=Admin,
    login_logo_url="https://preview.tabler.io/static/logo.svg"
)


app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'admin_templates')

@app.on_event("startup")
async def startup():
    redis = await aioredis.from_url(os.getenv('REDIS_URL', "redis://localhost:6379/0"), encoding="utf-8", decode_responses=True)
    await admin_app.configure(
        logo_url="https://preview.tabler.io/static/logo-white.svg",
        template_folders=[TEMPLATES_DIR],
        providers=[login_provider],
        redis=redis,
    )

    await init_db()

from fastapi_admin.app import app
from fastapi_admin.resources import Link


@app.register
class Home(Link):
    label = "Home"
    icon = "fas fa-home"
    url = "/admin"


app.mount("/admin", admin_app)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}