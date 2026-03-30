import random
from collections import Counter

# --- PACK CONFIGURATION ---
CARDS_PER_PACK = 12
COMMONS_PER_PACK = 7
UNCOMMONS_PER_PACK = 3
RARES_PER_PACK = 2

# Leaders replace uncommons; SR/SEC/TR/Alt/Manga replace rares.

# --- PROBABILITY RATES (based on 3456 cards baseline) ---
PROB_RATES = {
    "Leader": 8 / 288,             # 1 per 36 packs
    "SR": 7 / 288,                 # ~1 per 41 cards
    "SEC": 8 / 3456,               # ~1 per 432 cards
    "AltArt": 24 / 3456,           # ~1 per 144 cards
    "SP": 2 / 3456,                # ~1 per 1728 cards
    "AltLeader": 4 / 3456,         # ~1 per 864 cards
    "Manga": 1 / ((10368 + 13824) / 2),  # 1 per ~12,096 cards
}

# --- Base rarities (fillers) ---
RARITY_POOL = ["C", "UC", "R"]

# --- Hit rarities (can replace R or UC) ---
HIT_POOL = ["L", "SR", "SEC", "AltArt", "SP", "AltLeader", "Manga"]

def choose_hit():
    """Choose one hit based on probability rates."""
    roll = random.random()
    cumulative = 0
    for rarity, prob in PROB_RATES.items():
        cumulative += prob
        if roll < cumulative:
            return rarity
    return None  # No hit

def generate_pack():
    """Generate a single pack with rarity rules."""
    pack = []
    hit = choose_hit()

    # Default pack: 7C, 3UC, 2R
    commons = ["C"] * COMMONS_PER_PACK
    uncommons = ["UC"] * UNCOMMONS_PER_PACK
    rares = ["R"] * RARES_PER_PACK

    # Replace uncommons with Leader if rolled
    if hit == "Leader" or hit == "AltLeader":
        uncommons[-1] = hit  # Replace last UC
    # Replace one rare if hit type is special
    elif hit in ["SR", "SEC", "AltArt", "SP", "Manga"]:
        rares[-1] = hit

    # Pack structure — hits always at the back
    pack = commons + uncommons + rares
    return pack

def simulate_packs(num_packs=1000):
    """Simulate multiple packs and count occurrences."""
    all_packs = []
    rarity_counts = Counter()

    for _ in range(num_packs):
        pack = generate_pack()
        all_packs.append(pack)
        rarity_counts.update(pack)

    return all_packs, rarity_counts


# --- Run simulation ---
if __name__ == "__main__":
    num_packs = 10000
    packs, counts = simulate_packs(num_packs)

    total_cards = num_packs * CARDS_PER_PACK
    print(f"Simulated {num_packs} packs ({total_cards} cards)\n")

    for rarity, count in counts.items():
        print(f"{rarity}: {count} cards ({(count / total_cards) * 100:.3f}%)")

    # Quick breakdown by pack
    print("\nExample pack:")
    print(packs[random.randint(0, len(packs) - 1)])
