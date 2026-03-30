import discord
from discord import app_commands
from discord.ext import commands
from collections import Counter
from utils.db import get_collection, get_recent_special

PACK_SIZE = 12

class Stats(commands.Cog):
    """View user card opening stats."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stats", description="View your card opening stats")
    async def stats(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message("⚠️ CardCog not loaded. Please reload the bot.", ephemeral=True)
            return

        cards, _ = card_cog.load_active_pack(user_id)
        card_map = {c["name"]: c for c in cards}
        rows = get_collection(card_cog.cursor, user_id)

        if not rows:
            await interaction.response.send_message(f"{interaction.user.mention}, your collection is empty!")
            return

        rarity_counts = Counter()
        alt_count = 0
        manga_count = 0
        total_cards = 0

        for card_name, qty in rows:
            total_cards += qty
            cd = card_map.get(card_name, {})
            rarity_counts[cd.get("rarity", "Unknown")] += qty
            if cd.get("alt", 0): alt_count += qty
            if cd.get("manga", 0): manga_count += qty

        total_packs = total_cards // PACK_SIZE
        unique_cards = len(rows)

        # Rarity breakdown
        rarity_order = ["C", "UC", "R", "L", "SR", "SEC", "TR", "SP"]
        breakdown_lines = [f"**{r}**: {rarity_counts[r]}" for r in rarity_order if rarity_counts.get(r)]

        # Top 5 most-owned cards
        top5 = sorted(rows, key=lambda x: x[1], reverse=True)[:5]
        top_lines = []
        for name, qty in top5:
            cd = card_map.get(name, {})
            code = f" ({cd.get('code','')})" if cd.get("code") else ""
            top_lines.append(f"{name}{code} x{qty}")

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Stats",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Packs opened", value=str(total_packs), inline=True)
        embed.add_field(name="Total cards", value=str(total_cards), inline=True)
        embed.add_field(name="Unique cards", value=str(unique_cards), inline=True)
        embed.add_field(name="Alt arts", value=str(alt_count), inline=True)
        embed.add_field(name="Manga", value=str(manga_count), inline=True)
        embed.add_field(name="Rarity breakdown", value="\n".join(breakdown_lines) or "None", inline=False)
        embed.add_field(name="Top cards", value="\n".join(top_lines) or "None", inline=False)

        # Most recent special hit
        recent_hit = get_recent_special(card_cog.cursor, user_id)
        if recent_hit:
            name, code, image, card_type = recent_hit
            embed.set_footer(text=f"Most recent hit: {name} ({card_type})", icon_url=image)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
