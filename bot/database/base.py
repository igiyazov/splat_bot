import uuid

from tortoise import fields, models

class BaseModel(models.Model):
    id = fields.UUIDField(pk=True, editable=False, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        pass

