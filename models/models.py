from decimal import Decimal
from email.policy import default
from unicodedata import category
from tortoise import Tortoise, fields
from tortoise.models import Model
from data import config


class User(Model):
    id: int = fields.IntField(pk=True)
    tg_id: int = fields.BigIntField(unique=True)
    username: str = fields.CharField(max_length=255, null=True)

    cart: fields.ReverseRelation["UserCart"]
    profile: fields.OneToOneRelation["Profile"]
    favorites: fields.ReverseRelation["FavoriteProduct"]
    search_data: fields.ReverseRelation["SearchUserData"]
    # orders: fields.ReverseRelation["UserOrder"]


class Profile(Model):
    id: int = fields.IntField(pk=True)
    first_name: str = fields.CharField(max_length=50, null=True)
    last_name: str = fields.CharField(max_length=50, null=True)
    phone_number: str = fields.CharField(max_length=15, null=True)
    postcode: int = fields.IntField(null=True)
    city: str = fields.CharField(max_length=100, null=True)
    address: str = fields.TextField(null=True)
    user: fields.OneToOneRelation = fields.OneToOneField("models.User", related_name="profile")


class SearchUserData(Model):
    id: int = fields.IntField(pk=True)
    min_price: Decimal = fields.DecimalField(null=True, max_digits=1000, decimal_places=2)
    max_price: Decimal = fields.DecimalField(null=True, max_digits=1000, decimal_places=2)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", related_name="search_data")
    attrs = fields.JSONField(null=True)
    search: bool = fields.BooleanField(default=False)
    category_id: int = fields.IntField()


class UserCart(Model):
    id: int = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", related_name="cart")
    product_id: int = fields.IntField()
    quantity: int = fields.IntField(default=1)
    active: bool = fields.BooleanField(default=True)


class FavoriteProduct(Model):
    id: int = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", related_name="favorites")
    product_id: int = fields.IntField()


class UploadPhoto(Model):
    id: int = fields.IntField(pk=True)
    path: str = fields.CharField(max_length=255)
    photo_id: str = fields.CharField(max_length=255)


class ArchiveStringAttrs(Model):
    """Костыль, фиксит ошибку клавиатуры, в callback максимум 32 кирилические буквы влезает, это крайне мало"""

    id: int = fields.IntField(pk=True)
    string: str = fields.CharField(max_length=255, unique=True)


class Test(Model):
    """Костыль, фиксит ошибку клавиатуры, в callback максимум 32 кирилические буквы влезает, это крайне мало"""

    id: int = fields.IntField(pk=True)
    string: str = fields.CharField(max_length=255, unique=True)


# class UserOrder(Model):
#     user: fields.ForeignKeyRelation = fields.ForeignKeyField("models.User", related_name="orders")
#     shipping_option: str = fields.

# Tortoise.init(config.TORTOISE_ORM)
