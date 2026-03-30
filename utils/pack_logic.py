import random

PACK_FOLDER = "packs"       # folder where your pack JSONs live
DEFAULT_PACK = "op01"       # default pack code
PACK_SIZE = 12
UC_COUNT = 3
R_COUNT = 2

# hit rarities (standard, alt, etc.)
HIT_RARITIES = {"SR", "SEC", "TR", "SP"}

# Weighted chances (approximate per pack)
PROB_RATES = {
    "leader": 0.30,          # ~30% chance for leader
    "sr": 0.25,              # ~25% chance for SR
    "sec": 0.028,            # ~3% chance
    "alt_art": 0.08,         # ~8% chance for any alt (non-leader)
    "sp": 0.007,             # ~0.7% chance
    "alt_leader": 0.014,     # ~1.4% chance
    "manga": 0.001,          # ~0.1% chance
}


def is_hit(card):
    """True if this is any special card (SR/SEC/TR/SP, alt, manga, etc.)."""
    return (
        card.get("rarity") in HIT_RARITIES
        or card.get("alt", 0) == 1
        or card.get("manga", 0) == 1
    )


def weighted_choice(weight_dict):
    """Pick one key based on its probability weight."""
    roll = random.random()
    cumulative = 0
    for key, weight in weight_dict.items():
        cumulative += weight
        if roll < cumulative:
            return key
    return None


def _sample_unique(pool, k, used_names):
    available = [c for c in pool if c["name"] not in used_names]
    if len(available) <= k:
        return available.copy()
    return random.sample(available, k)


def generate_pack(cards):
    """Generate a realistic pack using weighted probabilities."""
    pool = cards.copy()
    random.shuffle(pool)

    commons_pool = [c for c in pool if c.get("rarity") == "C" and not is_hit(c)]
    uncommons_pool = [c for c in pool if c.get("rarity") == "UC" and not is_hit(c)]
    rares_pool = [c for c in pool if c.get("rarity") == "R" and not is_hit(c)]
    leaders_pool = [c for c in pool if c.get("rarity") == "L" and not is_hit(c)]
    hits_pool = [c for c in pool if is_hit(c)]

    used = set()
    pack_commons, pack_uncommons, pack_rares = [], [], []
    chosen_leader, chosen_hit = None, None

    # --- Weighted leader selection ---
    if leaders_pool and random.random() < PROB_RATES["leader"]:
        chosen_leader = random.choice(leaders_pool)
        used.add(chosen_leader["name"])

    # --- Weighted hit selection (only if no leader) ---
    if not chosen_leader:
        hit_type = weighted_choice({
            "manga": PROB_RATES["manga"],
            "alt_leader": PROB_RATES["alt_leader"],
            "sp": PROB_RATES["sp"],
            "sec": PROB_RATES["sec"],
            "alt_art": PROB_RATES["alt_art"],
            "sr": PROB_RATES["sr"],
        })
        if hit_type and hits_pool:
            # filter hits by the chosen type
            if hit_type == "manga":
                hit_candidates = [c for c in hits_pool if c.get("manga", 0) == 1]
            elif hit_type == "alt_leader":
                hit_candidates = [c for c in hits_pool if c.get("rarity") == "L" and c.get("alt", 1) == 1]
            elif hit_type == "alt_art":
                hit_candidates = [c for c in hits_pool if c.get("alt", 1) == 1 and c.get("rarity") != "L"]
            elif hit_type == "sp":
                hit_candidates = [c for c in hits_pool if c.get("rarity") == "SP"]
            elif hit_type == "sec":
                hit_candidates = [c for c in hits_pool if c.get("rarity") == "SEC"]
            elif hit_type == "sr":
                hit_candidates = [c for c in hits_pool if c.get("rarity") == "SR"]
            else:
                hit_candidates = []

            if hit_candidates:
                chosen_hit = random.choice(hit_candidates)
                used.add(chosen_hit["name"])

    # --- Fill Uncommons ---
    uc_needed = UC_COUNT - (1 if chosen_leader else 0)
    pack_uncommons = _sample_unique(uncommons_pool, uc_needed, used)
    used.update([c["name"] for c in pack_uncommons])

    # Leader replaces one UC slot (comes after UC)
    if chosen_leader:
        pack_uncommons.append(chosen_leader)

    # --- Fill Rares ---
    if chosen_leader:
        # 2 Rares after leader
        pack_rares = _sample_unique(rares_pool, R_COUNT, used)
        used.update([c["name"] for c in pack_rares])
    else:
        # Hit replaces 1 rare slot
        rare_needed = R_COUNT - (1 if chosen_hit else 0)
        pack_rares = _sample_unique(rares_pool, rare_needed, used)
        used.update([c["name"] for c in pack_rares])

    # --- Fill Commons ---
    commons_needed = PACK_SIZE - (len(pack_uncommons) + len(pack_rares) + (1 if chosen_hit else 0))
    pack_commons = _sample_unique(commons_pool, commons_needed, used)

    # --- Final ordering ---
    final = []
    final.extend(pack_commons)
    final.extend(pack_uncommons)
    final.extend(pack_rares)
    if chosen_hit:
        final.append(chosen_hit)

    # Trim/fill safety
    return final[:PACK_SIZE]
