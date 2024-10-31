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
        bot_room_id = row[0]
        announce_channel_ids = json.loads(row[1]) if row[1] else []
        return bot_room_id, announce_channel_ids
    else:
        return None, []
