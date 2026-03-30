import sqlite3
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

PST = ZoneInfo("America/Los_Angeles")
DB_PATH = "data/collections.db"

# ---------------------------------------------------------
# Get connection and ensure all tables exist
# ---------------------------------------------------------
def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Main collections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collections (
            user_id TEXT,
            card_name TEXT,
            quantity INTEGER,
            PRIMARY KEY (user_id, card_name)
        )
    """)

    # Table for most recent special pulls (alt/manga)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recent_special (
            user_id TEXT PRIMARY KEY,
            card_name TEXT,
            card_code TEXT,
            card_image TEXT,
            card_type TEXT
        )
    """)

    # Table for trades
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user TEXT,
            to_user TEXT,
            offered_card TEXT,
            requested_card TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)

    # Table for user settings (active pack)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id TEXT PRIMARY KEY,
            active_pack TEXT DEFAULT 'OP01'
        )
    """)

    # Table for managing open pack limits
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS openpack_cooldowns (
            user_id TEXT PRIMARY KEY,
            packs_opened INTEGER DEFAULT 0,
            last_reset TIMESTAMP
        )
    """)

    conn.commit()
    return conn, cursor


# ---------------------------------------------------------
# Add a card to the collection
# ---------------------------------------------------------
def add_card(conn, cursor, user_id, card_name):
    cursor.execute("""
        INSERT INTO collections (user_id, card_name, quantity)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, card_name)
        DO UPDATE SET quantity = quantity + 1
    """, (user_id, card_name))
    conn.commit()


# ---------------------------------------------------------
# Get all cards in a user's collection
# ---------------------------------------------------------
def get_collection(cursor, user_id):
    cursor.execute("SELECT card_name, quantity FROM collections WHERE user_id = ?", (user_id,))
    return cursor.fetchall()


# ---------------------------------------------------------
# Update or insert user's most recent special (alt/manga) pull
# ---------------------------------------------------------
def update_recent_special(conn, cursor, user_id, card):
    cursor.execute("""
        INSERT INTO recent_special (user_id, card_name, card_code, card_image, card_type)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET card_name=excluded.card_name,
                      card_code=excluded.card_code,
                      card_image=excluded.card_image,
                      card_type=excluded.card_type
    """, (
        user_id,
        card["name"],
        card.get("code", ""),
        card.get("image", ""),
        "Manga" if card.get("manga", 0) else "Alt Art"
    ))
    conn.commit()


# ---------------------------------------------------------
# Fetch the user's most recent special (alt/manga) pull
# ---------------------------------------------------------
def get_recent_special(cursor, user_id):
    cursor.execute("SELECT card_name, card_code, card_image, card_type FROM recent_special WHERE user_id = ?", (user_id,))
    return cursor.fetchone()


# ---------------------------------------------------------
# Trades
# ---------------------------------------------------------
def add_trade(conn, cursor, from_user, to_user, offered_card, requested_card):
    cursor.execute("""
        INSERT INTO trades (from_user, to_user, offered_card, requested_card)
        VALUES (?, ?, ?, ?)
    """, (from_user, to_user, offered_card, requested_card))
    conn.commit()

def get_pending_trades(cursor, user_id):
    cursor.execute("SELECT id, from_user, offered_card, requested_card FROM trades WHERE to_user=? AND status='pending'", (user_id,))
    return cursor.fetchall()

def complete_trade(conn, cursor, trade_id):
    cursor.execute("UPDATE trades SET status='completed' WHERE id=?", (trade_id,))
    conn.commit()


# ---------------------------------------------------------
# Active Pack Handling
# ---------------------------------------------------------
def get_active_pack(cursor, user_id):
    cursor.execute("SELECT active_pack FROM user_settings WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else "OP01"

def set_active_pack(conn, cursor, user_id, pack_name):
    cursor.execute("""
        INSERT INTO user_settings (user_id, active_pack)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET active_pack = excluded.active_pack
    """, (user_id, pack_name))
    conn.commit()


# ---------------------------------------------------------
# Open Pack Cooldown (3 per 12-hour window)
# ---------------------------------------------------------
def get_openpack_status(cursor, user_id):
    cursor.execute("SELECT packs_opened, last_reset FROM openpack_cooldowns WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        packs_opened, last_reset = row
        if last_reset:
            last_reset = datetime.fromisoformat(last_reset)
        return packs_opened or 0, last_reset
    return 0, None


def get_current_reset_window():
    """Return the start of the current global reset window (8AM or 8PM PST)."""
    now = datetime.now(PST)
    eight_am = now.replace(hour=8, minute=0, second=0, microsecond=0)
    eight_pm = now.replace(hour=20, minute=0, second=0, microsecond=0)

    if now < eight_am:
        # Before 8AM → last window started at 8PM yesterday
        return eight_pm - timedelta(hours=12)
    elif now < eight_pm:
        # Between 8AM and 8PM
        return eight_am
    else:
        # After 8PM
        return eight_pm


def increment_openpack(conn, cursor, user_id, reset=False):
    """Increment user's open count or reset it during a new global window."""
    packs_opened, last_reset = get_openpack_status(cursor, user_id)
    now = datetime.now(PST)
    current_window = get_current_reset_window()

    if reset:
        packs_opened = 0
    elif not last_reset or last_reset < current_window:
        packs_opened = 0

    packs_opened += 1

    cursor.execute("""
        INSERT INTO openpack_cooldowns (user_id, packs_opened, last_reset)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET packs_opened=?, last_reset=?
    """, (user_id, packs_opened, now.isoformat(), packs_opened, now.isoformat()))
    conn.commit()

    return packs_opened, current_window

def add_extra_token(conn, cursor, user_id, amount: int = 1):
    """Add extra tokens to a user, creating the user row if needed."""
    # Make sure the user exists
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    # Increment extra_tokens
    cursor.execute(
        "UPDATE users SET extra_tokens = extra_tokens + ? WHERE user_id = ?",
        (amount, user_id)
    )
    conn.commit()

def get_extra_tokens(cursor, user_id):
    cursor.execute("SELECT extra_tokens FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def use_extra_token(conn, cursor, user_id):
    tokens = get_extra_tokens(cursor, user_id)
    if tokens <= 0:
        return False
    cursor.execute(
        "UPDATE users SET extra_tokens = extra_tokens - 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    return True
