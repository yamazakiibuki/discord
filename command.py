import psycopg2
import json
import os

db_url = "postgres://koyeb-adm:TJQV65jSfXBK@ep-curly-mode-a2v5q610.eu-central-1.pg.koyeb.app/koyebdb"


def get_connection():
    return psycopg2.connect(db_url, sslmode="require")

def initialize_commands_table():
    """簡易コマンド用のテーブルを作成"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS custom_commands (
            guild_id BIGINT,
            command TEXT,
            response TEXT,
            PRIMARY KEY (guild_id, command)
        )
    ''')
    conn.commit()
    conn.close()

def add_command(guild_id, command, response):
    """簡易コマンドをデータベースに保存"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO custom_commands (guild_id, command, response)
        VALUES (%s, %s, %s)
        ON CONFLICT (guild_id, command) DO UPDATE 
        SET response = EXCLUDED.response
    ''', (guild_id, command, response))
    conn.commit()
    conn.close()

def remove_command(guild_id, command):
    """簡易コマンドをデータベースから削除"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        DELETE FROM custom_commands WHERE guild_id = %s AND command = %s
    ''', (guild_id, command))
    conn.commit()
    conn.close()

def get_commands(guild_id):
    """ギルドの簡易コマンドを取得"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT command, response FROM custom_commands WHERE guild_id = %s
    ''', (guild_id,))
    commands = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return commands

async def handle_custom_command(message):
    """メッセージが簡易コマンドなら応答"""
    guild_id = message.guild.id
    commands = get_commands(guild_id)
    
    if message.content.startswith("-"):
        command = message.content[1:]
        if command in commands:
            await message.channel.send(commands[command])
            return
