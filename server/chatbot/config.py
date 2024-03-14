from os import environ

DATABASE_HOST = environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT = environ.get("DATABASE_PORT", "5432")
DATABASE_NAME = environ.get("DATABASE_NAME", "br")
DATABASE_USER = environ.get("DATABASE_USER", "br")
DATABASE_PASSWORD = environ.get("DATABASE_PASSWORD", "br")
DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

REDIS_HOST = environ.get("REDIS_HOST", "localhost")
REDIS_PORT = environ.get("REDIS_PORT", "6379")
REDIS_PASSWORD = environ.get("REDIS_PASSWORD", "loL311tSCc")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"

CHROMA_HOST = environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = environ.get("CHROMA_PORT", "7777")

ACCESS_TOKEN_EXPIRE_MINUTES = int(environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "360"))
SECRET_KEY = environ.get(
    "SECRET_KEY", 'Wd%+Z(9z-`:u?X!uFo{\Z}<O*X8}_ec&.mr@{"rD_;(wxpa2gVEV%kB\'Gpx"j[$4'
)
ALGORITHM = environ.get("ALGORITHM", "HS256")
