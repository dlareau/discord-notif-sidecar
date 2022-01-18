import discord
import os
import sqlite3
from quart import Quart, request
from discord.ext import commands, tasks
from datetime import datetime

TOKEN = os.getenv('DISCORD_TOKEN')

COMMAND_PREFIX = "!"
DB_NAME = "database.sqlite"
MOD_DISCORD_ID = int(os.getenv('MOD_DISCORD_ID'))
MOD_ROLES = os.getenv('MOD_ROLES').split(",")

bot = commands.Bot(command_prefix=COMMAND_PREFIX, case_insensitve=True)

def can_sub(ctx):
    if(ctx.guild.id == MOD_DISCORD_ID):
        for role in MOD_ROLES:
            if(discord.utils.get(ctx.author.roles, name=role) is not None):
                return True
    return False

def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = connect()
    with conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS subs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            image_name TEXT NOT NULL,
                            guild_id TEXT NOT NULL,
                            channel_id TEXT NOT NULL,
                            UNIQUE(image_name, guild_id, channel_id)
                        );""")

app = Quart(__name__)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Subscribe a channel to an image's updates
@bot.command(name='subscribe')
@commands.check(can_sub)
async def subscribe(ctx, image_name):
    conn = connect()
    data = (image_name, ctx.guild.id, ctx.channel.id)
    with conn:
        conn.execute("INSERT INTO subs(image_name, guild_id, channel_id) VALUES (?,?,?)", data)
        await ctx.send("Subscribed successfully!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.send('You do not have the correct permissions for this command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Please supply an argument to the command.")
    elif isinstance(error, commands.errors.TooManyArguments):
        await ctx.send("Too many arguments supplied to the command.")
    else:
        print("unknown command error", error)


@app.route('/', methods=['POST'])
async def send_notif():
    routes = {}
    data = await request.get_json(force=True)

    conn = connect()
    with conn:
        for row in conn.execute('SELECT * FROM subs WHERE image_name=?', (data["service"],)):
            guild = bot.get_guild(int(row[2]))
            channel = discord.utils.get(guild.channels, id=int(row[3]))
            message = f"Service \"{data['service']}\" updated!\nPrev image: {data['prevImage']}\nNew image: {data['currImage']}"
            await channel.send(message)
    return 'ok'

create_db()
bot.loop.create_task(app.run_task())
bot.run(TOKEN)

