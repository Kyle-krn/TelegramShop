from decimal import Decimal
from email.policy import default
from tortoise import fields
from tortoise.models import Model

class User(Model):
    id: int = fields.IntField(pk=True)
    tg_id: int = fields.BigIntField(unique=True)
    username: str = fields.CharField(max_length=255, null=True)
    # first_name: str = fields.CharField(null=True)
    # last_name: str = fields.CharField(null=True)
    # profile: fields.OneToOneRelation = fields.OneToOneField(model_name="models.Profile", related_name="user", on_delete="CASCADE")
    cart: fields.ReverseRelation["UserCart"]
    profile: fields.ReverseRelation["Profile"]
    favorites: fields.ReverseRelation["FavoriteProduct"]
    search_data: fields.ReverseRelation["SearchUserData"]


class Profile(Model):
    id: int = fields.IntField(pk=True)
    first_name: str = fields.CharField(max_length=50, null=True)
    last_name: str = fields.CharField(max_length=50, null=True)
    phone_number: str = fields.CharField(max_length=15, null=True)
    postcode: int = fields.IntField(null=True)
    city: str = fields.CharField(max_length=100, null=True)
    address: str = fields.TextField(null=True)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", related_name="profile")
    # user: fields.OneToOneRelation["User"]


class SearchUserData(Model):
    id: int = fields.IntField(pk=True)
    min_price: Decimal = fields.DecimalField(null=True, max_digits=1000, decimal_places=2)
    max_price: Decimal = fields.DecimalField(null=True, max_digits=1000, decimal_places=2)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", related_name="search_data")
    attrs = fields.JSONField(null=True)

class UserCart(Model):
    id: int = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", related_name="cart")
    product_id: int = fields.IntField()
    quantity: int = fields.IntField(default=1)

class FavoriteProduct(Model):
    id: int = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", related_name="favorites")
    product_id: int = fields.IntField()

class UploadPhoto(Model):
    id: int = fields.IntField(pk=True)
    path: str = fields.CharField(max_length=255)
    photo_id: str = fields.CharField(max_length=255)



