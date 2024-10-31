import discord
import os
from client import MyClient
from keep import keep_alive
from database import initialize_database

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

client = MyClient(intents=intents)
keep_alive()
initialize_database()

client.run(os.environ['TOKEN'])
