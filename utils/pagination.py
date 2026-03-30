import discord
from .rarity import get_rarity_color

class CardPagination(discord.ui.View):
    # Existing card pagination (for openpack)
    def __init__(self, interaction: discord.Interaction, cards):
        super().__init__(timeout=120)
        self.cards = cards
        self.index = 0
        self.interaction = interaction
        self.message = None

    async def update_message(self):
        card = self.cards[self.index]

        # Build info line
        info_line = f"**Info:** {card.get('code', 'N/A')}"
        rarity_line = f"**Rarity:** {card.get('rarity', '')}"

        # Special markers
        special_lines = []
        if card.get("alt", 0):
            special_lines.append("⭐ Alternate Art ⭐")
        if card.get("manga", 0):
            special_lines.append("🔥 Manga 🔥")

        # Combine all without extra blank lines
        description = f"{info_line}\n{rarity_line}"
        if special_lines:
            description += "\n" + "\n".join(special_lines)

        if "quantity" in card:
            description += f"\nQuantity: {card['quantity']}"

        embed = discord.Embed(
            title=card["name"],
            description=description,
            color=get_rarity_color(card.get("rarity", ""), card.get("manga", 0))
        )

        embed.set_image(url=card["image"])
        embed.set_footer(text=f"Card {self.index + 1} of {len(self.cards)}")

        if self.message:
            await self.message.edit(embed=embed, view=self)
        else:
            self.message = await self.interaction.followup.send(embed=embed, view=self, wait=True)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index - 1) % len(self.cards)
        await self.update_message()
        await interaction.response.defer()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index + 1) % len(self.cards)
        await self.update_message()
        await interaction.response.defer()


# ---------------------------------------------------------
# Collection pagination (table-like, 12 lines per page)
# ---------------------------------------------------------
class CollectionPagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, collection_rows, per_page=12):
        super().__init__(timeout=120)
        self.interaction = interaction
        self.collection_rows = collection_rows  # list of tuples: (name, code, rarity, alt, manga, qty)
        self.per_page = per_page
        self.page = 0
        self.message = None
        self.total_pages = (len(collection_rows) - 1) // per_page + 1

    def format_page(self):
        start = self.page * self.per_page
        end = start + self.per_page
        # Filter out unknown/blank names
        page_rows = [
            (name, code, rarity, alt, manga, qty)
            for name, code, rarity, alt, manga, qty in self.collection_rows[start:end]
            if name and name.strip() and name.lower() != "unknown"
        ]

        if not page_rows:
            return "No cards to display on this page."

        # Table header
        lines = [
            "Name                      | Code      | Rarity | Alt | Manga | Qty",
            "--------------------------|-----------|--------|-----|-------|----"
        ]

        for name, code, rarity, alt, manga, qty in page_rows:
            display_name = name if len(name) <= 25 else name[:22] + "..."
            
            # Use * for Alt and Manga
            alt_marker = "*" if alt else " "
            manga_marker = "*" if manga else " "
            
            # Format row
            lines.append(f"{display_name:<25} | {code:<9} | {rarity:<6} | {alt_marker:^3} | {manga_marker:^5} | {qty:<3}")

        lines.append(f"\nPage {self.page + 1}/{self.total_pages}")
        return "```\n" + "\n".join(lines) + "\n```"



    async def update_message(self):
        content = self.format_page()
        if self.message is None:
            if self.interaction.response.is_done():
                self.message = await self.interaction.followup.send(content=content, view=self, wait=True)
            else:
                self.message = await self.interaction.response.send_message(content=content, view=self)
        else:
            await self.message.edit(content=content, view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page - 1) % self.total_pages
        await self.update_message()
        await interaction.response.defer()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page + 1) % self.total_pages
        await self.update_message()
        await interaction.response.defer()
