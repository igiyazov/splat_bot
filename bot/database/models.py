from enum import Enum

from tortoise import fields, models

from database.base import BaseModel


class User(BaseModel):
    first_name = fields.CharField(max_length=150, null=True)
    last_name = fields.CharField(max_length=150, null=True)
    username = fields.CharField(max_length=150, null=True)
    tg_id = fields.CharField(max_length=150, unique=True)
    phone_number = fields.CharField(max_length=150, null=True)
    language = fields.CharField(max_length=2, default='ru')
    is_instruction_sended = fields.BooleanField(default=False)


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


class ExceptionModel(BaseModel):
    class ErrorTypes(Enum):
        OFD = 'ofd'

    user = fields.ForeignKeyField(
        'models.User', related_name='exceptions', null=True, on_delete=fields.SET_NULL, default=None, to_field="id"
    )
    user_tg = fields.CharField(max_length=150, null=True)
    user_language = fields.CharField(max_length=2, default='ru')
    type = fields.CharEnumField(enum_type=ErrorTypes, default=ErrorTypes.OFD, max_length=20)
    path = fields.CharField(max_length=350, null=True)
    media = fields.ForeignKeyField('models.Media', related_name='exception', null=True, on_delete=fields.SET_NULL)
    success = fields.BooleanField(default=False)
    solved = fields.BooleanField(default=False)
    result = fields.CharField(max_length=150, null=True)
