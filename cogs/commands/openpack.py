import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utils.pagination import CardPagination
from utils.db import add_card, update_recent_special, increment_openpack, get_openpack_status

from utils.pack_logic import generate_pack

PACK_SIZE = 12
PACK_LIMIT = 3
PST = ZoneInfo("America/Los_Angeles")


class OpenPack(commands.Cog):
    """Command to open a One Piece TCG pack, now supports extra tokens."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="openpack",
        description="Open a One Piece TCG card pack from your selected set"
    )
    async def openpack(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        # Get the CardCog instance
        card_cog = interaction.client.get_cog("CardCog")
        if not card_cog:
            await interaction.response.send_message(
                "⚠️ CardCog not loaded. Please reload the bot.",
                ephemeral=True
            )
            return

        now = datetime.now(PST)

        # Determine current reset window (8AM–8PM or 8PM–8AM)
        eight_am = now.replace(hour=8, minute=0, second=0, microsecond=0)
        eight_pm = now.replace(hour=20, minute=0, second=0, microsecond=0)
        if now < eight_am:
            current_reset = eight_pm - timedelta(days=1)
            next_reset = eight_am
        elif now < eight_pm:
            current_reset = eight_am
            next_reset = eight_pm
        else:
            current_reset = eight_pm
            next_reset = eight_am + timedelta(days=1)

        cursor = card_cog.cursor

        # Check for extra tokens
        cursor.execute("SELECT extra_tokens FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        extra_tokens = result[0] if result else 0

        if extra_tokens > 0:
            cursor.execute(
                "UPDATE users SET extra_tokens = extra_tokens - 1 WHERE user_id = ?",
                (user_id,)
            )
            card_cog.conn.commit()
            used_extra = True
            opened_packs = 0  # ignore normal pack limit when using extra token
        else:
            used_extra = False
            # Fetch user's pack status
            opened_packs, last_reset = get_openpack_status(cursor, user_id)
            if not last_reset or last_reset < current_reset:
                opened_packs = 0

            # Uncommented check for daily limit is handled here if needed
            # if opened_packs >= PACK_LIMIT:
            #     time_until_reset = next_reset - now
            #     hours, minutes = divmod(int(time_until_reset.total_seconds() // 60), 60)
            #
            #     await interaction.response.send_message(
            #         f"🛒 **Oops! Sorry, but the store ran out of stock!**\n"
            #         f"Please hold while we run and get more! 🏃‍♂️💨\n\n"
            #         f"🕗 You can open packs again in **{hours}h {minutes}m**.",
            #         ephemeral=True
            #     )
            #     return

            # Increment user's open count
            opened_packs, _ = increment_openpack(card_cog.conn, cursor, user_id)

        # Load user's active pack
        cards, pack_code = card_cog.load_active_pack(user_id)
        pack = generate_pack(cards)

        # Add cards to DB
        for card in pack:
            add_card(card_cog.conn, cursor, user_id, card["name"])
            if card.get("alt", 0) or card.get("manga", 0):
                update_recent_special(card_cog.conn, cursor, user_id, card)

        packs_left = max(0, PACK_LIMIT - opened_packs)

        # Send pack with pagination
        await interaction.response.defer()
        pagination = CardPagination(interaction, pack)
        await pagination.update_message()

        token_msg = " (used an extra pack token!)" if used_extra else ""
        await interaction.followup.send(
            f"🎴 You opened a pack from **{pack_code.upper()}**!{token_msg}\n"
            f"📦 Packs left this session: **{packs_left}**",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(OpenPack(bot))
