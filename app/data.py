# Aoanul Hoque (PM), Kalimul Kaif, Owen Zeng, Yuhang Pan
# 2Y2B TierList Creator by 2Yellow2Brown
# SoftDev
# P02: Makers Makin' It, Act I
# Jan 2026

import sqlite3

DB_FILE="data.db"

db = sqlite3.connect(DB_FILE)
c = db.cursor()

#create tables if it isn't there already
c.execute("CREATE TABLE IF NOT EXISTS users (name TEXT NOT NULL COLLATE NOCASE, password TEXT NOT NULL, UNIQUE(name))")
c.execute("CREATE TABLE IF NOT EXISTS tierlists (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL COLLATE NOCASE, description TEXT, is_public BOOLEAN, last_update DATE, creator_name TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS tiers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL COLLATE NOCASE, tierlist_id INTEGER, FOREIGN KEY (tierlist_id) REFERENCES tierlists(id) ON DELETE CASCADE)")
c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL COLLATE NOCASE, image TEXT, position INTEGER, tier_id INTEGER, FOREIGN KEY (tier_id) REFERENCES tiers(id) ON DELETE CASCADE)")

def check_acc(username):
    return c.execute("SELECT 1 FROM users WHERE name = ?", (username,)).fetchone()

def check_password(username):
    return c.execute("SELECT password FROM users WHERE name = ?", (username,)).fetchone()

def insert_acc(username, password):
    c.execute("INSERT INTO users (name, password) VALUES (?, ?)", (username, password))

def get_recent_tierlists():
    result = []
    tierlists = c.execute("SELECT * FROM tierlists ORDER BY last_update DESC LIMIT 10").fetchall()
    for tierlist in tierlists:
        tiers = c.execute("SELECT * FROM tiers where tierlist_id = ? ORDER BY id", (tierlist['id'])).fetchall()
        tlist = []
        for tier in tiers:
            items = c.execute("SELECT * FROM items where tier_id = ? ORDER BY id", (tier['id'])).fetchall()
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
        "is_public": tierlist["is_public"],
        "last_update": tierlist["last_update"],
        "creator_name": tierlist["creator_name"],
        "tiers": tlist
    })
    return result
