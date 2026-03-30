import discord

class ResetConfirmation(discord.ui.View):
    def __init__(self, bot, interaction, target_user_id=None, reset_server=False):
        super().__init__(timeout=120)
        self.bot = bot
        self.interaction = interaction
        self.target_user_id = target_user_id
        self.reset_server = reset_server
        self.confirmed = False

    async def on_timeout(self):
        try:
            await self.interaction.edit_original_response(content="⏰ Reset cancelled due to timeout.", view=None)
        except:
            pass

    @discord.ui.button(label="Confirm ✅", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("You cannot confirm this reset.", ephemeral=True)
            return

        self.confirmed = True
        if self.reset_server:
            self.interaction.cog.cursor.execute("DELETE FROM collections")
            self.interaction.cog.cursor.execute("DELETE FROM recent_special")
            self.interaction.cog.cursor.execute("DELETE FROM active_packs")
            self.interaction.cog.conn.commit()
            await interaction.response.edit_message(content="✅ Entire server collections have been reset.", view=None)
        else:
            self.interaction.cog.cursor.execute("DELETE FROM collections WHERE user_id = ?", (self.target_user_id,))
            self.interaction.cog.cursor.execute("DELETE FROM recent_special WHERE user_id = ?", (self.target_user_id,))
            self.interaction.cog.cursor.execute("DELETE FROM active_packs WHERE user_id = ?", (self.target_user_id,))
            self.interaction.cog.conn.commit()
            user = self.interaction.guild.get_member(int(self.target_user_id))
            await interaction.response.edit_message(content=f"✅ {user.display_name}'s collection has been reset.", view=None)
        self.stop()

    @discord.ui.button(label="Cancel ❌", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("You cannot cancel this reset.", ephemeral=True)
            return

        await interaction.response.edit_message(content="❌ Reset cancelled.", view=None)
        self.stop()
