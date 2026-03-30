import discord
from discord import app_commands
from discord.ext import commands
import os, json, random
from utils.db import add_card
from utils.pagination import CardPagination

SECRET_FOLDER = os.path.join(os.path.dirname(__file__), "../../secretpacks")

def load_secret_pack(filename):
    """Load a JSON file from secretpacks safely."""
    file_path = os.path.join(SECRET_FOLDER, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_random_card(cards):
    return random.choice(cards)

class Lottery(commands.Cog):
    """Lottery command for special One Piece rewards."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="lottery",
        description="Try your luck in the One Piece lottery!"
    )
    async def lottery(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        # Get CardCog for database operations
        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message(
                "⚠️ CardCog not loaded. Please reload the bot.",
                ephemeral=True
            )
            return

        # Determine reward
        roll = random.random()
        if roll < 0.0001:  # 0.01%
            reward = "manga_god_pack"
        elif roll < 0.001:  # 0.1%
            reward = "single_manga"
        elif roll < 0.301:  # 30%
            reward = "extra_pack"
        elif roll < 0.601:  # next 30%
            reward = "promo_card"
        else:
            reward = "nothing"

        # Handle each reward
        if reward == "promo_card":
            promo_cards = load_secret_pack("promo.json")
            card = pick_random_card(promo_cards)
            add_card(card_cog.conn, card_cog.cursor, user_id, card["name"])
            await interaction.response.send_message(f"🎉 You won a promo card: **{card['name']}**!", ephemeral=True)

        elif reward == "single_manga":
            manga_cards = load_secret_pack("manga.json")
            card = pick_random_card(manga_cards)
            add_card(card_cog.conn, card_cog.cursor, user_id, card["name"])
            await interaction.response.send_message(f"📖 You won a manga card: **{card['name']}**!", ephemeral=True)

        elif reward == "manga_god_pack":
            manga_cards = load_secret_pack("manga.json")
            pack = random.sample(manga_cards, 12)
            for card in pack:
                add_card(card_cog.conn, card_cog.cursor, user_id, card["name"])
            # Optional: use pagination to show all 12 cards
            pagination = CardPagination(interaction, pack)
            await pagination.update_message()
            await interaction.followup.send(f"🌟 MANGA GOD PACK! You got 12 random manga cards!", ephemeral=True)

        elif reward == "extra_pack":
            # Increment extra token
            from utils.db import add_extra_token  # make sure to import it
            add_extra_token(card_cog.conn, card_cog.cursor, user_id)
            await interaction.response.send_message(
                "🛒 Lucky you! You got an **extra pack token**! Use it in `/openpack`.",
                ephemeral=True
            )

        elif reward == "extra_pack":
            # Example: increment a special token/counter for extra packs
            await interaction.response.send_message("🛒 Lucky you! You got an **extra pack token**!", ephemeral=True)

        else:
            await interaction.response.send_message("😢 Sorry, you didn't win anything this time.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Lottery(bot))
