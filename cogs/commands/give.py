import discord
from discord import app_commands
from discord.ext import commands
from utils.db import get_collection, add_card, update_recent_special

class Give(commands.Cog):
    """Give a specific card and quantity to another user."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="give", description="Give a specific card and quantity to another user")
    @app_commands.describe(
        to_user="The user to give cards to",
        card_name="The name of the card to give (exact name)",
        quantity="How many copies to give"
    )
    async def give(self, interaction: discord.Interaction, to_user: discord.Member, card_name: str, quantity: int):
        from_user = str(interaction.user.id)
        to_user_id = str(to_user.id)

        if to_user_id == from_user:
            await interaction.response.send_message("You can't give cards to yourself.", ephemeral=True)
            return
        if quantity <= 0:
            await interaction.response.send_message("Quantity must be at least 1.", ephemeral=True)
            return

        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message("⚠️ CardCog not loaded. Please reload the bot.", ephemeral=True)
            return

        rows = get_collection(card_cog.cursor, from_user)
        owned = next((qty for c_name, qty in rows if c_name.lower() == card_name.lower()), 0)
        if owned < quantity:
            await interaction.response.send_message(f"You don't have enough copies of `{card_name}`. You own {owned}.", ephemeral=True)
            return

        cards, _ = card_cog.load_active_pack(from_user)
        card_map = {c["name"]: c for c in cards}
        card_data = card_map.get(card_name)
        if not card_data:
            await interaction.response.send_message(f"Card `{card_name}` not found.", ephemeral=True)
            return

        # Deduct from sender
        card_cog.cursor.execute(
            "UPDATE collections SET quantity = quantity - ? WHERE user_id=? AND card_name=? AND quantity >= ?",
            (quantity, from_user, card_name, quantity)
        )
        card_cog.cursor.execute(
            "DELETE FROM collections WHERE user_id=? AND card_name=? AND quantity <= 0",
            (from_user, card_name)
        )

        # Add to receiver
        card_cog.cursor.execute("""
            INSERT INTO collections (user_id, card_name, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, card_name) DO UPDATE SET quantity = quantity + excluded.quantity
        """, (to_user_id, card_name, quantity))
        card_cog.conn.commit()

        if card_data.get("alt", 0) or card_data.get("manga", 0):
            update_recent_special(card_cog.conn, card_cog.cursor, to_user_id, card_data)

        await interaction.response.send_message(f"🎁 {interaction.user.mention} gave **{quantity}x {card_name}** to {to_user.mention}!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Give(bot))
