from tortoise import fields, models

from database.base import BaseModel


class User(BaseModel):
    first_name = fields.CharField(max_length=150, null=True)
    last_name = fields.CharField(max_length=150, null=True)
    username = fields.CharField(max_length=150)
    tg_id = fields.CharField(max_length=150, unique=True)
    phone_number = fields.CharField(max_length=150, null=True)
    language = fields.CharField(max_length=2, default='ru')


class Media(BaseModel):
    path = fields.CharField(max_length=350, null=True)


class Check(BaseModel):
    user = fields.ForeignKeyField(
        'models.User', related_name='checks', null=True, on_delete=fields.SET_NULL, default=None, to_field="id"
    )
    lg = fields.CharField(max_length=150, unique=True, null=True)
    media = fields.ForeignKeyField('models.Media', related_name='media', null=True, on_delete=fields.SET_NULL)


class Product(BaseModel):
    name = fields.CharField(max_length=150)
    count = fields.IntField()
    bill = fields.ForeignKeyField(
        'models.Check', related_name='products', null=True, on_delete=fields.SET_NULL, default=None
    )
