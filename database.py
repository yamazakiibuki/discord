import psycopg2
import json
from datetime import datetime

DATABASE_URL = "postgres://koyeb-adm:TJQV65jSfXBK@ep-curly-mode-a2v5q610.eu-central-1.pg.koyeb.app/koyebdb"

def get_connection():
    """PostgreSQL接続を取得"""
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def initialize_database():
    conn = get_connection()
    c = conn.cursor()
    # 設定テーブルの作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            guild_id BIGINT PRIMARY KEY,
            bot_room_id BIGINT,
            announce_channel_ids JSON
        )
    ''')
    # 投票テーブルの作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            question TEXT,
            options JSON,
            expiration TIMESTAMP,
            results JSON,
            FOREIGN KEY (guild_id) REFERENCES settings (guild_id)
        )
    ''')
    conn.commit()
    conn.close()

def ensure_guild_settings(guild_id):
    """guild_id が settings テーブルに存在しない場合、デフォルト値を挿入"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT guild_id FROM settings WHERE guild_id = %s', (guild_id,))
    if not c.fetchone():
        c.execute('''
            INSERT INTO settings (guild_id, bot_room_id, announce_channel_ids)
            VALUES (%s, %s, %s)
        ''', (guild_id, None, json.dumps([])))
        conn.commit()
    conn.close()

def save_vote(question, options, expiration):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO votes (guild_id, question, options, expiration, results)
        VALUES (%s, %s, %s, %s, %s)
    ''', (1, question, json.dumps(options), expiration, json.dumps({})))
    conn.commit()
    conn.close()

def get_votes():
    conn = get_connection()
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
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM votes WHERE id = %s', (vote_id,))
    conn.commit()
    rowcount = c.rowcount
    conn.close()
    return rowcount > 0
