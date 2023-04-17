from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
# IP = env.str("ip") # Тоже str, но для айпи адреса хоста
API_URL = env.str("API_URL")
API_TOKEN = env.str("API_TOKEN")
PAYMENTS_PROVIDER_TOKEN = env.str("PAYMENTS_PROVIDER_TOKEN")
USER_POSTGRES = env.str("USER_POSTGRES")
PASSWORD_POSTGRES = env.str("PASSWORD_POSTGRES")
HOST_POSTGRES = env.str("HOST_POSTGRES")
PORT_POSTGRES = env.int("PORT_POSTGRES")
DATABASE_POSTGRES = env.str("DATABASE_POSTGRES")

POSTGRES_URI = \
    f"postgres://{USER_POSTGRES}:{PASSWORD_POSTGRES}@{HOST_POSTGRES}:{PORT_POSTGRES}/{DATABASE_POSTGRES}"

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": ["models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "UTC",
}
