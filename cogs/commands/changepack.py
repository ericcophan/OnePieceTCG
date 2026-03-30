import discord
from discord import app_commands
from discord.ext import commands


class ChangePack(commands.Cog):
    """Allows users to change their active One Piece TCG pack."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="changepack", description="Change your currently active One Piece TCG pack")
    @app_commands.describe(pack="Enter the pack name (e.g., OP01, OP02, etc.)")
    async def changepack(self, interaction: discord.Interaction, pack: str):
        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message("⚠️ CardCog not loaded. Please reload the bot.", ephemeral=True)
            return

        user_id = str(interaction.user.id)

        # Make sure the pack exists in your data folder or JSONs
        valid_packs = card_cog.get_available_packs()
        if pack not in valid_packs:
            await interaction.response.send_message(
                f"❌ Invalid pack name. Available packs: {', '.join(valid_packs)}",
                ephemeral=True
            )
            return

        # Update user's active pack
        card_cog.set_active_pack(user_id, pack)
        await interaction.response.send_message(f"✅ Active pack changed to **{pack}**")


async def setup(bot: commands.Bot):
    await bot.add_cog(ChangePack(bot))
