import os
import ssl
from urllib.parse import quote_plus
import asyncpg
from dotenv import load_dotenv

load_dotenv()

class database:
    def __init__(self, db_url: str | None = None):
        if db_url is None:
            user = quote_plus(os.getenv("DB_USER", "postgres"))
            password = quote_plus(os.getenv("DB_PASSWORD", "postgres"))
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            name = os.getenv("DB_NAME", "postgres")
            self.db_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
        else:
            self.db_url = db_url

        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        # Configuração do SSL para conexão com banco Supabase
        ssl_ctx = None
        if "supabase" in self.db_url:
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

        self.pool = await asyncpg.create_pool(
            self.db_url,
            min_size=1,
            max_size=5,
            ssl=ssl_ctx
        )

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None