from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from collections import Counter
from utils.reset_confirmation import ResetConfirmation
from utils.pagination import CardPagination, CollectionPagination
from utils.db import (
    get_connection,
    add_card,
    get_collection,
    update_recent_special,
    get_recent_special
)
from utils.pack_logic import generate_pack
import os
import json
import sqlite3
from utils.db import get_connection

PACK_SIZE = 12
DEFAULT_PACK = "op01"
PACK_FOLDER = "packs"

# ---------------------------------------------------------
# CardCog
# ---------------------------------------------------------
class CardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn, self.cursor = get_connection()
        self.setup_database()

    def setup_database(self):
        """Create tables and columns if they don't exist."""
        # Table creation
        tables = {
            "active_packs": """
                CREATE TABLE IF NOT EXISTS active_packs (
                    user_id TEXT PRIMARY KEY,
                    pack_code TEXT
                )
            """,
            "openpack_cooldowns": """
                CREATE TABLE IF NOT EXISTS openpack_cooldowns (
                    user_id TEXT PRIMARY KEY,
                    packs_opened INTEGER DEFAULT 0,
                    last_reset TIMESTAMP
                )
            """,
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY
                )
            """
        }

        for name, sql in tables.items():
            self.cursor.execute(sql)

        # Column creation (safely)
        columns = {
            "users": {
                "extra_tokens": "INTEGER DEFAULT 0"
            }
        }

        for table, cols in columns.items():
            for col_name, col_type in cols.items():
                try:
                    self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    # Column already exists
                    pass

        self.conn.commit()

    # ---------------------------------------------------------
    # Helper: load active pack JSON for a user
    # ---------------------------------------------------------
    def load_active_pack(self, user_id: str):
        self.cursor.execute("SELECT pack_code FROM active_packs WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        pack_code = row[0] if row else DEFAULT_PACK

        pack_path = os.path.join(PACK_FOLDER, f"{pack_code}.json")
        if not os.path.exists(pack_path):
            pack_path = os.path.join(PACK_FOLDER, f"{DEFAULT_PACK}.json")

        with open(pack_path, "r", encoding="utf-8") as f:
            cards = json.load(f)

        return cards, pack_code
    
    def get_available_packs(self):
        """Return a list of available packs (excluding secret ones)."""
        packs_dir = "packs"
        packs = []
        for filename in os.listdir(packs_dir):
            if filename.endswith(".json"):
                pack_name = filename.replace(".json", "")
                packs.append(pack_name)
        return sorted(packs)

    def set_active_pack(self, user_id, pack_code):
        """Set or update the active pack for a user."""
        self.cursor.execute("""
            INSERT INTO active_packs (user_id, pack_code)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET pack_code = excluded.pack_code
        """, (user_id, pack_code))
        self.conn.commit()


# ---------------------------------------------------------
# Cog setup
# ---------------------------------------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(CardCog(bot))
