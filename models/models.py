from tortoise import fields
from tortoise.models import Model

class User(Model):
    id: int = fields.IntField(pk=True)
    tg_id: int = fields.BigIntField(unique=True)
    username: str = fields.CharField(max_length=255, null=True)
    # first_name: str = fields.CharField(null=True)
    # last_name: str = fields.CharField(null=True)
    profile: fields.OneToOneRelation = fields.OneToOneField(model_name="models.Profile", related_name="user", on_delete="CASCADE")


class Profile(Model):
    id: int = fields.IntField(pk=True)
    first_name: str = fields.CharField(max_length=50, null=True)
    last_name: str = fields.CharField(max_length=50, null=True)
    phone_number: str = fields.CharField(max_length=15, null=True)
    postcode: int = fields.IntField(null=True)
    city: str = fields.CharField(max_length=100, null=True)
    address: str = fields.TextField(null=True)
    user: fields.OneToOneRelation["User"]

