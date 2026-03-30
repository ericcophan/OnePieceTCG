import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from utils.db import get_collection, add_card, update_recent_special

class Trade(commands.Cog):
    """Propose trades between users."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="trade", description="Propose a trade with another user")
    @app_commands.describe(
        to_user="User to trade with",
        offered_card="Card you are offering (exact name)",
        requested_card="Card you want (exact name)"
    )
    async def trade(self, interaction: discord.Interaction, to_user: discord.Member, offered_card: str, requested_card: str):
        from_user = str(interaction.user.id)
        to_user_id = str(to_user.id)

        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message("⚠️ CardCog not loaded. Please reload the bot.", ephemeral=True)
            return

        cards, _ = card_cog.load_active_pack(from_user)
        card_map = {c["name"]: c for c in cards}

        rows_from = get_collection(card_cog.cursor, from_user)
        rows_to = get_collection(card_cog.cursor, to_user_id)

        if not any(c_name.lower() == offered_card.lower() for c_name, qty in rows_from):
            await interaction.response.send_message(f"You do not own `{offered_card}`.", ephemeral=True)
            return
        if not any(c_name.lower() == requested_card.lower() for c_name, qty in rows_to):
            await interaction.response.send_message(f"{to_user.display_name} does not own `{requested_card}`.", ephemeral=True)
            return

        offered_card_data = card_map.get(offered_card)
        requested_card_data = card_map.get(requested_card)

        embed = discord.Embed(
            title=f"Trade Proposal",
            description=f"{interaction.user.display_name} wants to trade with {to_user.display_name}",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name=f"{interaction.user.display_name}'s Offer",
            value=f"{offered_card_data['name']} ({offered_card_data.get('code','N/A')})\n"
                  f"Rarity: {offered_card_data.get('rarity','Unknown')}\n"
                  f"Alt: {'*' if offered_card_data.get('alt',0) else 'None'}\n"
                  f"Manga: {'*' if offered_card_data.get('manga',0) else 'None'}",
            inline=True
        )
        embed.add_field(
            name=f"{to_user.display_name}'s Card",
            value=f"{requested_card_data['name']} ({requested_card_data.get('code','N/A')})\n"
                  f"Rarity: {requested_card_data.get('rarity','Unknown')}\n"
                  f"Alt: {'*' if requested_card_data.get('alt',0) else 'None'}\n"
                  f"Manga: {'*' if requested_card_data.get('manga',0) else 'None'}",
            inline=True
        )

        if offered_card_data.get("image"):
            embed.set_thumbnail(url=offered_card_data["image"])
        if requested_card_data.get("image"):
            embed.set_image(url=requested_card_data["image"])

        class TradeView(View):
            def __init__(self):
                super().__init__(timeout=120)
                self.result = None

            @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green)
            async def accept(self, button: Button, i: discord.Interaction):
                if i.user.id != int(to_user_id):
                    await i.response.send_message("This trade isn't for you!", ephemeral=True)
                    return
                self.result = True
                self.stop()
                await i.response.defer()

            @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.red)
            async def decline(self, button: Button, i: discord.Interaction):
                if i.user.id != int(to_user_id):
                    await i.response.send_message("This trade isn't for you!", ephemeral=True)
                    return
                self.result = False
                self.stop()
                await i.response.defer()

        view = TradeView()
        await interaction.response.send_message(
            f"{to_user.mention}, do you accept this trade? You have 2 minutes to respond.",
            embed=embed,
            view=view
        )
        await view.wait()

        if view.result is True:
            # Swap cards
            add_card(card_cog.conn, card_cog.cursor, from_user, requested_card)
            add_card(card_cog.conn, card_cog.cursor, to_user_id, offered_card)
            card_cog.cursor.execute(
                "UPDATE collections SET quantity = quantity - 1 WHERE user_id=? AND card_name=? AND quantity > 0",
                (from_user, offered_card)
            )
            card_cog.cursor.execute(
                "UPDATE collections SET quantity = quantity - 1 WHERE user_id=? AND card_name=? AND quantity > 0",
                (to_user_id, requested_card)
            )
            card_cog.conn.commit()

            if offered_card_data.get("alt",0) or offered_card_data.get("manga",0):
                update_recent_special(card_cog.conn, card_cog.cursor, to_user_id, offered_card_data)
            if requested_card_data.get("alt",0) or requested_card_data.get("manga",0):
                update_recent_special(card_cog.conn, card_cog.cursor, from_user, requested_card_data)

            await interaction.followup.send(f"✅ Trade completed: `{offered_card}` ↔ `{requested_card}`")
        else:
            await interaction.followup.send(f"❌ {to_user.display_name} declined the trade or did not respond in time.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Trade(bot))
