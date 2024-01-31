from datetime import datetime

from fastapi_admin.models import AbstractAdmin
from tortoise import fields, models

from app.database.base import BaseModel


class Admin(AbstractAdmin):
    email = fields.CharField(max_length=200, default='')
    last_login = fields.DatetimeField(description='Last Login', default=datetime.now)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk}#{self.username}'

class User(BaseModel):
    first_name = fields.CharField(max_length=150)
    last_name = fields.CharField(max_length=150)
    username = fields.CharField(max_length=150)
    tg_id = fields.CharField(max_length=150)


class Check(BaseModel):
    user = fields.ForeignKeyField(
        'models.User', related_name='checks', null=True, on_delete=fields.SET_NULL, default=None, to_field="id"
    )
    lg = fields.CharField(max_length=150, unique=True)


class Product(BaseModel):
    name = fields.CharField(max_length=150)
    count = fields.IntField()
    bill = fields.ForeignKeyField(
        'models.Check', related_name='products', null=True, on_delete=fields.SET_NULL, default=None
    )
