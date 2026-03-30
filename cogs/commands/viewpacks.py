import os
import discord
from discord import app_commands
from discord.ext import commands

PACK_FOLDER = "packs"


class ViewPacks(commands.Cog):
    """Shows all available One Piece TCG packs and highlights the user's active pack."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="viewpacks", description="View all available One Piece TCG packs")
    async def viewpacks(self, interaction: discord.Interaction):
        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message("⚠️ CardCog not loaded. Please reload the bot.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        _, active_pack = card_cog.load_active_pack(user_id)
        active_pack = active_pack.upper() if active_pack else "OP01"

        # List all packs in the folder
        pack_files = [f for f in os.listdir(PACK_FOLDER) if f.endswith(".json")]
        if not pack_files:
            await interaction.response.send_message("⚠️ No packs are currently available.")
            return

        pack_codes = sorted([os.path.splitext(f)[0].upper() for f in pack_files])

        # Highlight active pack
        pack_lines = []
        for p in pack_codes:
            if p == active_pack:
                pack_lines.append(f"• **{p}** ✅")  # mark active pack
            else:
                pack_lines.append(f"• {p}")

        embed = discord.Embed(
            title="📦 Available One Piece TCG Packs",
            description="\n".join(pack_lines),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Use /changepack <pack_code> to switch packs")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ViewPacks(bot))
