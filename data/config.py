from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста
API_URL = env.str("API_URL")
API_TOKEN = env.str("API_TOKEN")

USER = 'telegram_user'
PASSWORD = 'remdigga96'
HOST = '0.0.0.0'
PORT = 5432
DATABASE = 'telegram_shop'

POSTGRES_URI = f"postgres://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": ["models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "UTC"
}