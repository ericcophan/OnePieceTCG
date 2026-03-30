import discord
from discord import app_commands
from discord.ext import commands


class ActivePack(commands.Cog):
    """Shows the user's currently active One Piece TCG pack."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="activepack", description="View your currently active One Piece TCG pack")
    async def activepack(self, interaction: discord.Interaction):
        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message("⚠️ CardCog not loaded. Please reload the bot.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        _, active_pack = card_cog.load_active_pack(user_id)

        if not active_pack:
            await interaction.response.send_message("You don’t have an active pack selected. Use /changepack to pick one.")
        else:
            await interaction.response.send_message(f"Your active pack is: **{active_pack}**")


async def setup(bot: commands.Bot):
    await bot.add_cog(ActivePack(bot))
