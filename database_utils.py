import logging

import aiosqlite

DATABASE_PATH = 'db.sqlite3'
logger = logging.getLogger(__name__)


# Dependency for database connection
async def get_db():
    db = await aiosqlite.connect(DATABASE_PATH)
    try:
        yield db
    finally:
        await db.close()


async def bootstrap_database():
    try:
        db = await aiosqlite.connect(DATABASE_PATH)
        async with db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS vending_machines (
                    id uuid primary key,
                    name text,
                    lat real,
                    lng real,
                    created_at text,
                    updated_at text
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id uuid primary key,
                    name text,
                    description text,
                    price real,
                    size number,
                    temperature text
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS vending_item_link (
                    id uuid primary key,
                    vending_machine_id uuid references vending_machines(id),
                    product_id uuid references products(id)
                )
            ''')
    except Exception as e:
        logger.error(f"Error bootstrapping database: {e}")
        raise
