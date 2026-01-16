from data import get_db_connection, init_db

def create_users():
    conn = get_db_connection()
    users = [
        ('my goat', '1'),
        ('yuhang', '1'),
        ('owen', '1'),
        ('araf', '1'),
        ('kalimul', '1')
    ]
    for username, password in users:
        conn.execute("INSERT OR IGNORE INTO users (name, password, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)", (username, password))
    conn.commit()
    conn.close()

def create_tierlists():
    conn = get_db_connection()
    tierlists = [
        {
            "title": "Best Programming Languages",
            "description": "Rank the programming languages by coolness",
            "creator": "my goat",
            "upvotes": 67
        },
        {
            "title": "Best Anime Openings",
            "description": "Pure vibes",
            "creator": "my goat",
            "upvotes": 41
        }
    ]
    ids = []
    for t in tierlists:
        cur = conn.execute("INSERT INTO tierlists (title, description, upvotes, last_update, creator_name) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)", (
            t["title"],
            t["description"],
            t["upvotes"],
            t["creator"]
        ))
        ids.append(cur.lastrowid)
    conn.commit()
    conn.close()
    return ids

def create_tiers(tierlist_id):
    conn = get_db_connection()
    tiers = ["S", "A", "B", "C", "D", "F"]
    tier_ids = []
    for name in tiers:
        cur = conn.execute("INSERT INTO tiers (name, tierlist_id) VALUES (?, ?)", (name, tierlist_id))
        tier_ids.append(cur.lastrowid)
    conn.commit()
    conn.close()
    return tier_ids

def create_items(tier_id, items):
    conn = get_db_connection()
    for position, name in enumerate(items):
        conn.execute("INSERT INTO items (name, image, position, tier_id) VALUES (?, ?, ?, ?)", (name, None, position, tier_id))
    conn.commit()
    conn.close()

def populate_tables():
    init_db()

    create_users()

    tierlist_ids = create_tierlists()

    # Programming Languages Tierlist
    programming_tiers = create_tiers(tierlist_ids[0])
    create_items(programming_tiers[0], ["Python", "C++", "Java", "my goat's language"])
    create_items(programming_tiers[1], ["JavaScript", "Go"])
    create_items(programming_tiers[2], ["Ruby"])
    create_items(programming_tiers[3], ["PHP"])
    create_items(programming_tiers[4], ["Rust"])
    create_items(programming_tiers[5], ["Lua"])

    # Anime OP Tierlist
    anime_tiers = create_tiers(tierlist_ids[1])
    create_items(anime_tiers[0], ["Gurenge", "Kick Back", "Iris Out"])
    create_items(anime_tiers[1], ["Unravel"])
    create_items(anime_tiers[2], ["Blue Bird"])
    create_items(anime_tiers[5], ["None"])

populate_tables()