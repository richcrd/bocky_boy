import discord
import random 
from discord.ext import commands
import os 
from dotenv import load_dotenv
import requests
from collections import defaultdict

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.all()
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents)

def get_computer_choice():
    return random.choice(["piedra", "papel", "tijera"])

def determine_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "Empate"
    elif (
        (player_choice == "piedra" and computer_choice == "tijera") or
        (player_choice == "papel" and computer_choice == "piedra") or
        (player_choice == "tijera" and computer_choice == "papel")
    ):
        return "Ganaste!"
    else:
        return "Perdiste"

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command(name="jugar")
async def ppt(ctx, player_choice: str):
    print(f"Jugador {ctx.author.name} eligió {player_choice}")
    player_choice = player_choice.lower()
    if player_choice not in ["piedra", "papel", "tijera"]:
        await ctx.send("Escribe piedra, papel o tijera")
        return
    computer_choice = get_computer_choice()
    result = determine_winner(player_choice, computer_choice)
    await ctx.send(f"Tu elegiste {player_choice}\n"
                   f"Yo elegí {computer_choice}\n"
                   f"Resultado: {result}")

@bot.command(name="invite")
async def invite(ctx):
    await ctx.send("https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot")

# @bot.command(name="hola")
# async def hola(ctx):
#     username = ctx.author.name
#     await ctx.send(f"Hola! {username}\nSoy Bocky, el robot y asistente creado por Richard. Estoy listo para asistirte en lo que necesites")

@bot.event
async def on_message(message):
    if message.content.lower() == "hola":
        username = message.author.name
        await message.channel.send(f"Hola! {username}\nSoy Bocky, el robot y asistente creado por Richard. Estoy listo para ayudarte en lo que necesites")
    await bot.process_commands(message)

@bot.command(name = "halaga")
async def halaga(ctx, member: discord.Member):
    halagos = [
        f"Eres muy inteligente", 
        f"Eres muy guap@", 
        f"Eres muy talentos@", 
        f"Eres muy amable",
        f"tu sonrisa ilumnina el día de cualquiera",
        f"Eres muy divertido",
        f"deber[ias dar clases de cómo ser tan genial",
    ]
    halago = random.choice(halagos)
    await ctx.send(f"{member.mention} {halago}")

@bot.command(name="adivina")
async def guess_game(ctx):
    number = random.randint(1, 10)
    await ctx.send("Adivina el número que estoy pensando entre 1 y 10")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

    attempts = 0
    while True:
        try:
            msg = await bot.wait_for("message", check=check, timeout=30.0)
            guess = int(msg.content)
            attempts += 1

            if guess < number:
                await ctx.send("¡Es más alto!")
            elif guess > number:
                await ctx.send("¡Es más bajo!")
            else:
                await ctx.send(f"¡Correcto! Lo lograste en {attempts} intentos.")
                break
        except:
            await ctx.send(f"Se acabó el tiempo. El número era {number}.")
            break

@bot.command(name="chiste")
async def joke(ctx):
    response = requests.get("https://v2.jokeapi.dev/joke/Any?type=single")
    if response.status_code == 200:
        joke_data = response.json()
        await ctx.send(joke_data["joke"])
    else:
        await ctx.send("No encontré chistes en este momento. 😔")

user_data = {}

# Comando para economia
@bot.command(name="balance")
async def balance(ctx):
    user = str(ctx.author.id)
    balance = user_data.get(user, 0)
    await ctx.send(f"{ctx.author.name}, Tu saldo es de {balance} monedas")
@bot.command(name="trabajar")
async def work(ctx):
    user = str(ctx.author.id)
    if user not in user_data:
        user_data[user] = 0
    earnings = random.randint(1, 100)
    user_data[user] += earnings
    await ctx.send(f"Felicidades {ctx.author.name}, Ganaste {earnings} monedas por tu trabajo")

# @bot.command(name="transferir")
# async def transfer(ctx, member: discord.Member, amount: int):
#     user = str(ctx.author.id)
#     target = str(member.id)
#     if user not in user_data or user_data[user] < amount:
#         await ctx.send("No tienes suficientes monedas")
#         return
#     user_data[user] -= amount
#     user_data[target] = user_data.get(target, 0) + amount
#     await ctx.send(f"Transferencia exitosa de {amount} monedas a {member.name}")

@bot.command(name="dados")
async def roll_dice(ctx, sides: int = 6):
    if sides < 1:
        await ctx.send("No puedo lanzar un dado con menos de 1 lado")
        return
    result = random.randint(1, sides)
    await ctx.send(f"{ctx.author.name} lanzó un 🎲 dado de {sides} lados y sacó: {result}")

stocks = {"BotCorp": 100, "CodeTech": 50}
user_portfolio = defaultdict(lambda: {"balance": 1000, "stocks": defaultdict(int)})

@bot.command(name="mercado")
async def market(ctx):
    market_status = "\n".join([f"{stock}: ${price}" for stock, price in stocks.items()])
    await ctx.send(f"📈 **Mercado Actual:**\n{market_status}")

@bot.command(name="comprar")
async def buy_stock(ctx, stock: str, amount: int):
    user = user_portfolio[ctx.author.id]
    if stock not in stocks or amount < 1:
        await ctx.send("Stock inválido.")
        return
    cost = stocks[stock] * amount
    if user["balance"] < cost:
        await ctx.send("No tienes suficiente dinero.")
        return
    user["balance"] -= cost
    user["stocks"][stock] += amount
    await ctx.send(f"Compraste {amount} acciones de {stock}. Saldo restante: ${user['balance']}")

@bot.command(name="cartera")
async def portfolio(ctx):
    user = user_portfolio[ctx.author.id]
    stocks_list = "\n".join([f"{stock}: {amount}" for stock, amount in user["stocks"].items()])
    await ctx.send(f"💼 **Tu cartera:**\nSaldo: ${user['balance']}\n{stocks_list}")

bot.run(TOKEN)
