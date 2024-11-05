import sqlite3
import json
from datetime import datetime

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
    
    # 投票用テーブルの作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            question TEXT,
            options TEXT,
            expiration TEXT,
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

def save_vote(question, options, expiration):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO votes (guild_id, question, options, expiration, results)
        VALUES (?, ?, ?, ?, ?)
    ''', (1, question, json.dumps(options), expiration, json.dumps({})))
    conn.commit()
    conn.close()

def get_votes():
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('SELECT id, question, options, expiration, results FROM votes')
    votes = []
    for row in c.fetchall():
        votes.append({
            'id': row[0],
            'question': row[1],
            'options': json.loads(row[2]),
            'expiration': row[3],
            'results': json.loads(row[4]) if row[4] else {}
        })
    conn.close()
    return votes

def delete_vote_entry(vote_id):
    conn = sqlite3.connect('settings.db')
    c = conn.cursor()
    c.execute('DELETE FROM votes WHERE id = ?', (vote_id,))
    conn.commit()
    rowcount = c.rowcount
    conn.close()
    return rowcount > 0
