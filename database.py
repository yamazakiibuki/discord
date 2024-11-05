import sqlite3
import json

def initialize_database():
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY,
            bot_room_id INTEGER,
            announce_channel_ids TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            question TEXT,
            options TEXT,
            deadline DATETIME,
            results TEXT,
            FOREIGN KEY (guild_id) REFERENCES settings (guild_id)
        )
    ''')
    conn.commit()
    conn.close()

def save_settings(guild_id, bot_room_id, announce_channel_ids):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO settings (guild_id, bot_room_id, announce_channel_ids)
        VALUES (?, ?, ?)
    ''', (guild_id, bot_room_id, json.dumps(announce_channel_ids)))
    conn.commit()
    conn.close()

def load_settings(guild_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('SELECT bot_room_id, announce_channel_ids FROM settings WHERE guild_id = ?', (guild_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0], json.loads(row[1]) if row[1] else []
    return None, []

def save_vote(guild_id, question, options, deadline):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO votes (guild_id, question, options, deadline, results)
        VALUES (?, ?, ?, ?, ?)
    ''', (guild_id, question, json.dumps(options), deadline, json.dumps({})))
    conn.commit()
    conn.close()

def get_votes(guild_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('SELECT * FROM votes WHERE guild_id = ?', (guild_id,))
    votes = c.fetchall()
    conn.close()
    return votes

def delete_vote(vote_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('DELETE FROM votes WHERE vote_id = ?', (vote_id,))
    conn.commit()
    conn.close()
