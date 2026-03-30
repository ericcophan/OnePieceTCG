# One Piece TCG Discord Bot

A Discord bot that simulates opening One Piece Trading Card Game packs, built with Python and discord.py. Users can open packs, build collections, trade cards, and compete for rare pulls — all within Discord.

---

## Features

- 🎴 **Pack Opening** — Open packs from multiple sets (OP01, OP02, EB01) with weighted pull rates replicating real TCG odds
- 📦 **Multi-Set Support** — Switch between available sets with `/changepack`
- 📋 **Collection Viewer** — Browse your full card collection with paginated embeds
- 🔄 **Card Trading** — Propose peer-to-peer trades with real-time Accept/Decline buttons
- 🎰 **Lottery System** — Daily lottery for a chance at promo cards, manga pulls, or extra pack tokens
- 📊 **Stats Tracking** — View your rarity breakdown, total packs opened, alt arts, manga pulls, and top cards
- 🔍 **Card Lookup** — Look up any card by code for rarity, alt art, and image info
- ⏱️ **Cooldown System** — Pack openings are limited per 12-hour window (8AM / 8PM PST resets)
- 🎁 **Give System** — Give cards directly to other users

---

## Commands

| Command | Description |
|---|---|
| `/openpack` | Open a pack from your active set |
| `/collection` | View your card collection |
| `/stats` | View your pull stats and rarity breakdown |
| `/trade` | Propose a card trade with another user |
| `/give` | Give a card to another user |
| `/changepack` | Switch your active pack set |
| `/activepack` | View your currently active pack |
| `/viewpacks` | See all available packs |
| `/cardinfo` | Look up a card by code (e.g. OP01-001) |
| `/lottery` | Try your luck for special rewards |
| `/commands` | List all available commands |

---

## Tech Stack

- **Language:** Python 3.11+
- **Library:** discord.py (app_commands, cogs)
- **Database:** SQLite via `sqlite3`
- **Architecture:** Modular cog system with a central `CardCog` base
- **Card Data:** JSON files per set with rarity, alt art, and manga flags

---

## Project Structure

```
├── bot.py                  # Entry point, loads all cogs
├── packs/                  # Card data JSON files (OP01, OP02, EB01, etc.)
│   ├── op01.json
│   ├── op02.json
│   └── eb01.json
├── cogs/
│   ├── card_cog.py         # Base cog: DB setup, pack loading, shared helpers
│   └── commands/
│       ├── openpack.py
│       ├── collection.py
│       ├── trade.py
│       ├── stats.py
│       ├── give.py
│       ├── lottery.py
│       ├── activepack.py
│       ├── changepack.py
│       ├── viewpacks.py
│       ├── cardinfo.py
│       └── commandslist.py
├── utils/
│   ├── db.py               # All database operations
│   ├── pack_logic.py       # Weighted pack generation engine
│   ├── pagination.py       # Discord embed pagination views
│   ├── rarity.py           # Rarity color and formatting helpers
│   ├── reset_confirmation.py # Admin reset UI
│   └── simulate_packs.py   # Standalone pack simulation script
├── data/                   # SQLite database (gitignored)
├── .env                    # Discord token (gitignored)
└── .gitignore
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Install dependencies
```bash
pip install discord.py python-dotenv
```

### 3. Create a `.env` file
```
DISCORD_TOKEN=your_token_here
```

### 4. Run the bot
```bash
python bot.py
```

---

## Pull Rate System

Pack generation uses a weighted probability engine that simulates real One Piece TCG odds:

| Rarity | Approximate Rate |
|---|---|
| Leader | ~30% per pack |
| SR | ~25% per pack |
| SEC | ~3% per pack |
| Alt Art | ~8% per pack |
| SP | ~0.7% per pack |
| Alt Leader | ~1.4% per pack |
| Manga | ~0.1% per pack |

Each pack contains 12 cards (7C, 3UC, 2R) with hits replacing the rare or uncommon slots.

---

## Deployment

The bot can be hosted on any platform that supports Python:
- [Railway](https://railway.app)
- [Render](https://render.com)
- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)

---

## License

MIT