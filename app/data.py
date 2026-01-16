import sqlite3
import os

ABS_PATH = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(ABS_PATH, "data.db")

# conncects to db
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# creates all the tables
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # create tables if it isn't there already
    c.execute("CREATE TABLE IF NOT EXISTS users (name TEXT NOT NULL COLLATE NOCASE, password TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(name))")

    c.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in c.fetchall()]
    if 'created_at' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    c.execute("CREATE TABLE IF NOT EXISTS tierlists (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL COLLATE NOCASE, description TEXT, upvotes INTEGER DEFAULT 0, last_update DATE, creator_name TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS tiers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL COLLATE NOCASE, tierlist_id INTEGER, FOREIGN KEY (tierlist_id) REFERENCES tierlists(id) ON DELETE CASCADE)")
    c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL COLLATE NOCASE, image TEXT, position INTEGER, tier_id INTEGER, FOREIGN KEY (tier_id) REFERENCES tiers(id) ON DELETE CASCADE)")
    c.execute("CREATE TABLE IF NOT EXISTS votes (name TEXT, tierlist_id INTEGER, value INTEGER DEFAULT 0, FOREIGN KEY (tierlist_id) REFERENCES tierlists(id) ON DELETE CASCADE)")
    conn.commit()
    conn.close()

init_db()

# get user for auth
def check_acc(username):
    conn = get_db_connection()
    user = conn.execute("SELECT 1 FROM users WHERE name = ?", (username,)).fetchone()
    conn.close()
    return user

# get passwrod for auth
def check_password(username):
    conn = get_db_connection()
    user = conn.execute("SELECT password FROM users WHERE name = ?", (username,)).fetchone()
    conn.close()
    return user

# add signed in acc to db
def insert_acc(username, password):
    conn = get_db_connection()
    conn.execute("INSERT INTO users (name, password, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)", (username, password))
    conn.commit()
    conn.close()

def get_user_info(username):
    conn = get_db_connection()
    user = conn.execute("SELECT name, created_at FROM users WHERE name = ?", (username,)).fetchone()
    conn.close()
    return user

# get user's tierlist, as the function name states
def get_user_tierlists(username):
    conn = get_db_connection()
    tierlists = conn.execute("SELECT * FROM tierlists WHERE creator_name = ? ORDER BY last_update DESC", (username,)).fetchall()
    conn.close()
    return convert_to_list(tierlists)

# convert tierlists into lists and dictionaries so they are easier to work with in jinja
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
            "last_update": tierlist["last_update"],
            "creator_name": tierlist["creator_name"],
            "tiers": tlist
        })
    conn.close()
    return result

# for search bar to get tierlists with matching titles
def search_tierlist(title):
    conn = get_db_connection()
    tierlists = conn.execute("SELECT * FROM tierlists WHERE title = ?", (title,)).fetchall()
    conn.close()
    return convert_to_list(tierlists)

# get the most recent tierlists
def get_recent_tierlists():
    conn = get_db_connection()
    tierlists = conn.execute("SELECT * FROM tierlists ORDER BY last_update DESC LIMIT 10").fetchall()
    conn.close()
    return convert_to_list(tierlists)

# get the tierlists with the most upvotes
def get_best_tierlists():
    conn = get_db_connection()
    tierlists = conn.execute("SELECT * FROM tierlists ORDER BY upvotes DESC LIMIT 10").fetchall()
    conn.close()
    return convert_to_list(tierlists)

# get tierlist by id
def get_tierlist(id):
    conn = get_db_connection()
    tierlist = conn.execute("SELECT * FROM tierlists WHERE id = ?", (id,)).fetchone()

    if not tierlist:
        conn.close()
        return None
    conn.close()
    return convert_to_list([tierlist])[0]

# get the # of upvotes in tierlist the user is tryna upvote, update the upvote count, and return the new number of upvotes to be displayed
def upvote_tierlist(name, tierlist_id, value):
    conn = get_db_connection()
    upvotes = conn.execute("SELECT upvotes FROM tierlists where id = ?", (tierlist_id,)).fetchone()[0]
    conn.execute("UPDATE tierlists SET upvotes = ?", (upvotes + value))
    conn.execute("INSERT INTO votes (name, tierlist_id, value) VALUES (?, ?, ?)", (name, tierlist_id, value))
    conn.commit()
    conn.close()
    return upvotes + value

# create tier list we'll pass the name, title, desc, and tiers dictionary
def create_tierlist(creator_name, title, description, tiers_dict):
    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "INSERT INTO tierlists (title, description, upvotes, last_update, creator_name) VALUES (?, ?, 0, ?, DATE('now'), ?)",
        (title, description, creator_name)
    )
    tierlist_id = c.lastrowid

    for tier_name in ["S", "A", "B", "C", "D", "F"]:
        c.execute("INSERT INTO tiers (name, tierlist_id) VALUES (?, ?)", (tier_name, tierlist_id))
        tier_id = c.lastrowid

        tier_items = tiers_dict.get(tier_name, [])
        for pos, it in enumerate(tier_items):
            name = (it.get("name") or "").strip()
            image = (it.get("image") or "").strip() or None
            if not name:
                name = "Item"
            c.execute(
                "INSERT INTO items (name, image, position, tier_id) VALUES (?, ?, ?, ?)",
                (name, image, pos, tier_id)
            )

    conn.commit()
    conn.close()
    return tierlist_id
