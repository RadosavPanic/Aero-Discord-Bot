import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
weather_api_key = os.getenv('WEATHER_API_KEY')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

required_role = "Weather"

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")

@bot.command()
async def reply(ctx):
    await ctx.reply("I am replying to your message")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=required_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} You have been assigned **{required_role}** role")
    else:
        await ctx.send(f"{required_role} role does not exist.")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=required_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} Your role **{required_role}** has been removed")
    else:
        await ctx.send(f"{required_role} role does not exist.")

@bot.command()
async def weather(ctx, *, city: str):
    url = f"http://api.openweathermap.org/data/3.0/weather?q={city}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        await ctx.send(f"⚠️ Could not find weather for `{city}`. Try again.")
        return

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"].capitalize()
    await ctx.send(f"☁️ Weather in **{city}**: {temp}°C, {description}")

@weather.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"You need to be assigned to role **{required_role}** to use this command")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
