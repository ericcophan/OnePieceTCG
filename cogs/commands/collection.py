import discord
from discord import app_commands
from discord.ext import commands

from utils.pagination import CardPagination, CollectionPagination
from utils.db import get_collection 

class Collection(commands.Cog):
    """Handles viewing the user's One Piece TCG collection."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="collection", description="View your One Piece TCG collection")
    async def collection(self, interaction: discord.Interaction):
        # Get CardCog (to access active pack, DB connection, etc.)
        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message("⚠️ CardCog not loaded. Please reload the bot.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        cards, _ = card_cog.load_active_pack(user_id)
        card_map = {c["name"]: c for c in cards}

        # ✅ Use CardCog’s cursor to query user’s collection
        rows = get_collection(card_cog.cursor, user_id)

        if not rows:
            await interaction.response.send_message(f"{interaction.user.mention}, your collection is empty!")
            return

        # Build data for pagination
        collection_rows = []
        for card_name, qty in rows:
            cd = card_map.get(card_name, {})
            collection_rows.append((
                card_name,
                cd.get("code", ""),
                cd.get("rarity", "Unknown"),
                cd.get("alt", 0),
                cd.get("manga", 0),
                qty
            ))

        pagination = CollectionPagination(interaction, collection_rows)
        await pagination.update_message()


async def setup(bot: commands.Bot):
    await bot.add_cog(Collection(bot))
