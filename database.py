import sqlite3
import json

def initialize_database():
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    
    # settingsテーブルの作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY,
            bot_room_id INTEGER,
            announce_channel_ids TEXT
        )
    ''')
    
    # votesテーブルの作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            expiry TIMESTAMP NOT NULL,
            message_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL
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

# 投票データを管理する関数

def register_vote(question, options, expiry, message_id, guild_id, channel_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO votes (question, options, expiry, message_id, guild_id, channel_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (question, json.dumps(options), expiry, message_id, guild_id, channel_id))
    conn.commit()
    conn.close()

def get_votes(guild_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('SELECT vote_id, question, options, expiry, message_id FROM votes WHERE guild_id = ?', (guild_id,))
    votes = c.fetchall()
    conn.close()
    return votes

def delete_vote(vote_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('DELETE FROM votes WHERE vote_id = ?', (vote_id,))
    conn.commit()
    conn.close()

def get_vote_by_id(vote_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('SELECT question, options, expiry, message_id, guild_id, channel_id FROM votes WHERE vote_id = ?', (vote_id,))
    vote = c.fetchone()
    conn.close()
    return vote
