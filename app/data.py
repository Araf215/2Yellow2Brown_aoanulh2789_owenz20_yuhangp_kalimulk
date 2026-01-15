import sqlite3

DB_FILE = "data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # create tables if it isn't there already
    c.execute("CREATE TABLE IF NOT EXISTS users (name TEXT NOT NULL COLLATE NOCASE, password TEXT NOT NULL, UNIQUE(name))")
    c.execute("CREATE TABLE IF NOT EXISTS tierlists (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL COLLATE NOCASE, description TEXT, upvotes INTEGER DEFAULT 0, is_public BOOLEAN, last_update DATE, creator_name TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS tiers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL COLLATE NOCASE, tierlist_id INTEGER, FOREIGN KEY (tierlist_id) REFERENCES tierlists(id) ON DELETE CASCADE)")
    c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL COLLATE NOCASE, image TEXT, position INTEGER, tier_id INTEGER, FOREIGN KEY (tier_id) REFERENCES tiers(id) ON DELETE CASCADE)")
    c.execute("CREATE TABLE IF NOT EXISTS votes (name TEXT, tierlist_id INTEGER, value INTEGER DEFAULT 0, FOREIGN KEY (tierlist_id) REFERENCES tierlists(id) ON DELETE CASCADE))")
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()

def check_acc(username):
    conn = get_db_connection()
    user = conn.execute("SELECT 1 FROM users WHERE name = ?", (username,)).fetchone()
    conn.close()
    return user

def check_password(username):
    conn = get_db_connection()
    user = conn.execute("SELECT password FROM users WHERE name = ?", (username,)).fetchone()
    conn.close()
    return user

def insert_acc(username, password):
    conn = get_db_connection()
    conn.execute("INSERT INTO users (name, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def convert_to_list(tierlists):
    conn = get_db_connection()
    result = []
    for tierlist in tierlists:
        tiers = conn.execute("SELECT * FROM tiers WHERE tierlist_id = ? ORDER BY id", (tierlist['id'],)).fetchall()
        tlist = []
        for tier in tiers:
            items = conn.execute("SELECT * FROM items WHERE tier_id = ? ORDER BY id", (tier['id'],)).fetchall()
            tlist.append({
                "id": tier["id"],
                "name": tier["name"],
                "items": [{
                        "id": item["id"],
                        "name": item["name"],
                        "image": item["image"],
                        "position": item["position"]
                    } for item in items
                ]
            })
        result.append({
            "id": tierlist["id"],
            "title": tierlist["title"],
            "description": tierlist["description"],
            "upvotes": tierlist["upvotes"],
            "is_public": tierlist["is_public"],
            "last_update": tierlist["last_update"],
            "creator_name": tierlist["creator_name"],
            "tiers": tlist
        })
    conn.close()
    return result

def search_tierlist(title):
    conn = get_db_connection()
    tierlists = conn.execute("SELECT * FROM tierlists WHERE title = ?", (title,)).fetchall()
    conn.close()
    return convert_to_list(tierlists)

def get_recent_tierlists():
    conn = get_db_connection()
    tierlists = conn.execute("SELECT * FROM tierlists ORDER BY last_update DESC LIMIT 10").fetchall()
    conn.close()
    return convert_to_list(tierlists)

def get_best_tierlists():
    conn = get_db_connection()
    tierlists = conn.execute("SELECT * FROM tierlists ORDER BY upvotes DESC LIMIT 10").fetchall()
    conn.close()
    return convert_to_list(tierlists)

def get_tierlist(id):
    conn = get_db_connection()
    tierlist = conn.execute("SELECT * FROM tierlists WHERE id = ?", (id,)).fetchone()
    
    if not tierlist:
        conn.close()
        return None
    conn.close()
    return convert_to_list(tierlist)[0]
