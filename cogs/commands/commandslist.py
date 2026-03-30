import discord
from discord import app_commands
from discord.ext import commands

class CommandsList(commands.Cog):
    """List all available commands."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="commands", description="List all available commands")
    async def list_commands(self, interaction: discord.Interaction):
        commands_list = await self.bot.tree.fetch_commands()
        lines = [f"/{c.name} - {c.description}" for c in commands_list]
        await interaction.response.send_message("\n".join(lines) if lines else "No commands available.")


async def setup(bot: commands.Bot):
    await bot.add_cog(CommandsList(bot))
