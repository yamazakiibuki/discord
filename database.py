import psycopg2
import json

DATABASE_URL = "postgres://koyeb-adm:TJQV65jSfXBK@ep-curly-mode-a2v5q610.eu-central-1.pg.koyeb.app/koyebdb"

def get_connection():
    """PostgreSQL接続を取得"""
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def initialize_database():
    """データベースの初期化"""
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
            results JSON,
            FOREIGN KEY (guild_id) REFERENCES settings (guild_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def save_settings(guild_id, bot_room_id, announce_channel_ids):
    """設定情報を保存"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO settings (guild_id, bot_room_id, announce_channel_ids)
        VALUES (%s, %s, %s)
        ON CONFLICT (guild_id) DO UPDATE 
        SET bot_room_id = EXCLUDED.bot_room_id, announce_channel_ids = EXCLUDED.announce_channel_ids
    ''', (guild_id, bot_room_id, json.dumps(announce_channel_ids)))
    conn.commit()
    conn.close()

def load_settings(guild_id):
    """指定されたギルドIDの設定をロード"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT bot_room_id, announce_channel_ids FROM settings WHERE guild_id = %s', (guild_id,))
    row = c.fetchone()
    conn.close()
    if row:
        # announce_channel_ids が文字列型の場合のみ JSON デコードを実行
        announce_channel_ids = json.loads(row[1]) if isinstance(row[1], str) else row[1]
        return {
            'bot_room_id': row[0],
            'announce_channel_ids': announce_channel_ids
        }
    return None

def save_vote(guild_id, question, options):
    """投票を保存"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO votes (guild_id, question, options, results)
        VALUES (%s, %s, %s, %s)
    ''', (guild_id, question, json.dumps(options), json.dumps({})))
    conn.commit()
    conn.close()

def get_votes(guild_id):
    """投票を取得"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, question, options, results FROM votes WHERE guild_id = %s', (guild_id,))
    votes = []
    for row in c.fetchall():
        votes.append({
            'id': row[0],
            'question': row[1],
            'options': row[2] if isinstance(row[2], list) else json.loads(row[2]),
            'results': json.loads(row[3]) if row[3] else {}
        })
    conn.close()
    return votes

def ensure_guild_settings(guild_id):
    """guild_id が設定テーブルに存在しない場合はデフォルト値を挿入"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT guild_id FROM settings WHERE guild_id = %s', (guild_id,))
    if not c.fetchone():
        c.execute('''
            INSERT INTO settings (guild_id, bot_room_id, announce_channel_ids)
            VALUES (%s, NULL, %s)
        ''', (guild_id, json.dumps([])))
        conn.commit()
    conn.close()
