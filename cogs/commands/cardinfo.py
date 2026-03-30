import discord
from discord import app_commands
from discord.ext import commands

class CardInfo(commands.Cog):
    """Get info about a specific One Piece TCG card."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cardinfo", description="Get info about a One Piece TCG card by code")
    @app_commands.describe(code="The code of the card to look up (e.g., OP01-001)")
    async def cardinfo(self, interaction: discord.Interaction, code: str):
        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message("⚠️ CardCog not loaded. Please reload the bot.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        cards, _ = card_cog.load_active_pack(user_id)
        code = code.strip().upper()
        card_data = next((c for c in cards if c.get("code","").upper() == code), None)

        if not card_data:
            await interaction.response.send_message(f"No card found with code `{code}`.")
            return

        embed = discord.Embed(
            title=card_data.get("name","Unknown Card"),
            color=discord.Color.blurple()
        )
        embed.add_field(name="Code", value=card_data.get("code","N/A"), inline=True)
        embed.add_field(name="Rarity", value=card_data.get("rarity","Unknown"), inline=True)
        embed.add_field(name="Alt Art", value="*" if card_data.get("alt",0) else "None", inline=True)
        embed.add_field(name="Manga", value="*" if card_data.get("manga",0) else "None", inline=True)
        if card_data.get("image"):
            embed.set_image(url=card_data["image"])

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CardInfo(bot))
