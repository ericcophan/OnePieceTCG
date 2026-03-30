import discord

def format_rarity(rarity, alt, manga):
    rarity_text = rarity or "N/A"
    alt_text = "✨ Alternate Art ✨" if alt == 1 else ""
    manga_text = "🔥 Manga 🔥" if manga == 1 else ""

    details = f"**Rarity:** {rarity_text}"
    if alt_text:
        details += f"\n{alt_text}"
    if manga_text:
        details += f"\n{manga_text}"

    return details


def get_rarity_color(rarity, manga):
    if manga == 1:
        return discord.Color.bright_red()

    colors = {
        "C": discord.Color.light_grey(),
        "UC": discord.Color.greyple(),
        "R": discord.Color.blue(),
        "L": discord.Color.dark_blue(),
        "SR": discord.Color.purple(),
        "SEC": discord.Color.gold(),
        "TR": discord.Color.teal(),
        "SP": discord.Color.pink(),
    }

    return colors.get(rarity, discord.Color.default())
