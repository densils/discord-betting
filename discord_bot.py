#####################################
## Read the readme before anything##
#####################################
# Imports
import asyncio
import json
import os
import random
from datetime import datetime
import discord
from discord.ext import commands
import discord.ext
from time import sleep
import bot_secrets

# Get your token here: https://discord.com/developers/applications
### Your bot token goes here. Don't forget the "" at the beginning and the end.
BOT_TOKEN = bot_secrets.token
bet_channel = bot_secrets.bet_channel
bookie = bot_secrets.bookie
### Decides the prefix of the bot. Default is "!". So for example to type the help command you would type !help.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
### Bad words go in here. If users type these words in any message the message will be deleted and they lose 100 coins.
bad_words = ("")
### Slurs go in here. If users type these words in any message the message will be deleted and they lose all their coins.
slurs = ("Wodka")
### If you have a meme channel type it here. Users who post links or files in this channel have a chance to get some coins.
meme_channelname = "channel_name"
### If set to true, there is no cooldown on games, which means you can farm an infinite amount of coins.
infinite_games = False
gewinnmöglichkeiten = [[1000, 100], [500, 95],
                       [200, 75], [100, 55], [50, 1], [-100, 0]]

## Initializing variables

# Tells the bot if there is an active minigame.
active_minigame = False
# Tells the bot if there is an active prediction.
active_prediction = False
# Sets current_directory to the one this file is in.
current_directory = os.getcwd()

# Sets the location of the data.json file. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/data.json"
jsonfile = current_directory + '/data.json'
# Sets the location of the questions.txt file. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/questions.txt"
#questions = current_directory + "/Game1/questions.txt"
# Sets the location of the Game2 folder. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/Game2"
#game2images = os.listdir(current_directory + "/Game2")
# Sets the location of the nums folder. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/Game3/nums"
#game3nums = os.listdir(current_directory + "/Game3/nums")
# Sets the location of the images folder. If you want to change this you need to set the whole path Example: "C:/Users/username/Documents/folder1/Game3/images"
#game3images = os.listdir(current_directory + "/Game3/images")

## These functions are code which is used often inside other functions, so i don't have to write the same code multiple times.

# Loads coins from file.


def load_coins():
    global coinsd, data
    # reads data.json
    with open(jsonfile) as file:
        data = json.load(file)
        coinsd = data["coins"]

# Changes coins of a user.


def coinchange(user, amount):
    # Reloads coins from file.
    load_coins()
    # Can subtract aswell by simply making the amount negative.
    coinsd[user] = coinsd[user] + amount
    # Checks if the coins are below 0 after changing them.
    if coinsd[user] < 0:
        # If they are, this will set them to 0.
        coinsd[user] = 0
    # Saves coins to data.json
    with open(jsonfile, "w") as file:
        json.dump(data, file)

# Checks if the user is already signed up


def signed_up(author):
    # Reloads coins from file.
    load_coins()
    if author in coinsd:
        return True

# Checks if the user has enough coins


def enough_coins(author, amount):
    # Reloads coins from file.
    load_coins()
    if coinsd[author] >= int(amount):
        return True

# Loads the times users have last played a minigame


def check_times():
    global timesd
    # Reads data.json
    with open(jsonfile) as file:
        data = json.load(file)
        timesd = data["play_times"]

# Updates the users last played time.


def update_last_played(user):
    check_times()
    timesd[user] = str(datetime.now())
    data["play_times"] = timesd
    # Saves last played to data.json
    with open(jsonfile, "w") as file:
        json.dump(data, file)

# Checks if a user has already played a game in the last 24hrs or day.


def Already_played(author):
    # This method lets you play once a calender day
    check_times()
    # Gets current time as string.
    current_time = str(datetime.now())
    try:
        # Gets last played time as string.
        last_played = timesd[author]
    except KeyError:
        # Sets it to the year 2000 if user has never played.
        last_played = "2000-06-29 20:14:54.391623"
    # Checks year.
    if int(last_played[:4]) < int(current_time[:4]):
        return False
    # Checks month.
    if int(last_played[5:7]) < int(current_time[5:7]):
        return False
    # Checks day.
    if int(last_played[8:10]) < int(current_time[8:10]):
        return False
    return True
    # This method lets you play once every 24 hours
    check_times()
    try:
        timeobj = datetime.strptime(timesd[author], "%Y-%m-%d %H:%M:%S.%f")
    except KeyError:
        timeobj = datetime.strptime(
            "2000-06-29 20:14:54.391623", "%Y-%m-%d %H:%M:%S.%f")
    if (((datetime.now() - timeobj).total_seconds() / 60) / 60) < 16:
        return False
    return True


# loads any open prediction from data.json
def load_prediction():
    global data, sum_of_bets_per_option, both, total, active_prediction, closed_prediction, options, prediction_starter, prediction_name
    with open(jsonfile) as file:
        data = json.load(file)
        sum_of_bets_per_option = data["prediction"]["sum_of_bets_per_option"]
        both = data["prediction"]["both"]
        total = data["prediction"]["total"]
        active_prediction = data["prediction"]["status"]["active_prediction"]
        closed_prediction = data["prediction"]["status"]["closed_prediction"]
        options = data["prediction"]["options"]
        prediction_starter = data["prediction"]["prediction_starter"]
        prediction_name = data["prediction"]["prediction_name"]

# saves a open prediction to data.json.
# This makes predictions persist even if the bot goes offline
# if statements basically checks if there is prediction active


def save_prediction():
    with open(jsonfile, "w") as file:
        if sum_of_bets_per_option:
            data["prediction"]["sum_of_bets_per_option"] = sum_of_bets_per_option
        if both:
            data["prediction"]["both"] = both
        if total:
            data["prediction"]["total"] = total
        if active_prediction:
            data["prediction"]["status"]["active_prediction"] = active_prediction
        if closed_prediction:
            data["prediction"]["status"]["closed_prediction"] = closed_prediction
        if options:
            data["prediction"]["options"] = options
        if prediction_starter:
            data["prediction"]["prediction_starter"] = prediction_starter
        if prediction_name:
            data["prediction"]["prediction_name"] = prediction_name
        json.dump(data, file)

# resets prediction and all variables


def reset_prediction():
    global data, sum_of_bets_per_option, both, total, active_prediction, closed_prediction
# Loads a active prediction from data.json, if there is one.
    load_prediction()
    both = {}
    sum_of_bets_per_option = {}
    active_prediction = False
    closed_prediction = False
    total = 0
    options = []
    prediction_starter = ""
    with open(jsonfile, "w") as file:
        data["prediction"]["sum_of_bets_per_option"] = sum_of_bets_per_option
        data["prediction"]["both"] = both
        data["prediction"]["total"] = total
        data["prediction"]["status"]["active_prediction"] = active_prediction
        data["prediction"]["status"]["closed_prediction"] = closed_prediction
        data["prediction"]["options"] = options
        data["prediction"]["prediction_starter"] = prediction_starter
        json.dump(data, file)

#Methode für !spin


def Drehen():
    p = 0
    suchen = True
    spinergebnis = random.randint(0, 100)
    while(p < len(gewinnmöglichkeiten) and suchen):
        #print(p)
        a = int(gewinnmöglichkeiten[p][1])
        b = int(gewinnmöglichkeiten[p][0])
        if spinergebnis >= a:
            suchen = False
            return b
        p = p+1

#Methode für !spin


def Glücksrad(nutzer):
    gewinn = Drehen()
    coinchange(nutzer, int(gewinn))
    return gewinn


## Bot commands

@bot.command(brief="Registrier dich, um 1000 Nuggets zu erhalten.")
async def signup(ctx):
    if ctx.channel.id == bet_channel:
        author = ctx.message.author.mention
        global coinsd
        # Checks if the author of the command is signed up and refreshes coins from data.json.
        if signed_up(author):
            await ctx.send("Du bist bereits registriert, du hast %s Nuggets." % coinsd[author])
            return
        # Creates dictionary entry with userid as key and the amount of coins as value.
        coinsd[author] = 1000
        with open(jsonfile, "w") as file:
            # Saves it to data.json.
            json.dump(data, file)
        await ctx.send('%s hat sich registriert und hat nun %d Nuggets. ' % (str(author), coinsd[author]))


@bot.command(brief="Zeigt an, wie viele Nuggets du hast.")
async def coins(ctx):
    if ctx.channel.id == bet_channel:
        author = ctx.message.author.mention
        # Checks if the author of the command is signed up and refreshes coins from data.json.
        if not signed_up(author):
            await ctx.send("Du bist nicht registriert! Nutze !signup, um 1000 Nuggets zu erhalten!")
            return
        # Grammar correction: when you only have 1 coin it says "1 coin" instead of "1 coins".
        if coinsd[author] == 1:
            await ctx.send(f"Du hast {coinsd[author]} Nugget.")
            return
        await ctx.send(f"Du hast {coinsd[author]} Nuggets!")


@bot.command(brief="Gib jemandem Nuggets !give <@user> <Anzahl>")
async def give(ctx, receiver, amount):
    if ctx.channel.id == bet_channel:
        # Lazy way to catch wrong inputs and send "Wrong input"
        try:
            author = ctx.message.author.mention
            # Checks if Author has enough coins.
            if not enough_coins(author, int(amount)):
                await ctx.send("Du hast nicht genug Nuggets.")
                return
        except ValueError:
            await ctx.send("Falsche Eingabe")
            return
        amount = int(amount)
        # Checks if the author of the command is signed up and refreshes coins from file.
        if not signed_up(author):
            await ctx.send("Registrier dich zu erst!")
            return
        # Checks if the receiver is signed up.
        if receiver not in coinsd:
            await ctx.send("Empfänger hat sich noch nicht registriert!")
            return
        # Adds/Removes Coins to/from author.
        coinchange(author, -amount)
        # Gives coins to receiver.
        coinchange(receiver, amount)
        # Grammar correction: when you only have 1 coin it says "1 coin" instead of "1 coins".
        if amount == 1:
            await ctx.send(f"{author} hat {amount} Nugget an {receiver} geschickt!")
            return
        await ctx.send(f"{author} hat {amount} Nuggets an {receiver} geschickt!")


# rolleid = 985272095103680542 channelid = bet_channel
@bot.command(brief='Starte eine Wette, !nw <Name der Wette>. (Kann nur von Wettbüromitarbeiter verwendet werden.)')
@commands.has_role(bot_secrets.bookie)
async def nw(ctx, *name):
    if ctx.channel.id == bet_channel:
        global options, prediction_starter, active_prediction, closed_prediction, prediction_name
        # Loads a active prediction from data.json, if there is one.
        load_prediction()
        if active_prediction:
            await ctx.send("Es läuft bereits eine Wette.")
            return
        # Checks if the user typed the prediction name after !prediction.
        if len(ctx.message.content.split()) < 2:
            await ctx.send("Gebe den Namen der Wette nach !prediction ein\n**WETTE NICHT GESTARTET**")
            reset_prediction()
            return
        # Makes sure the bot only accepts answers from the user that started it.

        def check(m):
            return ctx.author == m.author
        await ctx.send("Gebe die Optionen getrennt durch "","" an\nBeispiel: A, B, C")
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        # Puts all options into a list seperated by ",".
        options = msg.content.split(",")
        # Removes whitespaces at start/end points for each option.
        options = [i.strip() for i in options]
        # Checks if atleast 2 options were given.
        if len(options) < 2:
            await ctx.send("Mind. zwei Optionen\n**WETTE NICHT GESTARTET!**")
            reset_prediction()
            return
        prediction_starter = ctx.message.author.mention
        prediction_name = " ".join(name)
        await ctx.send(f"<@&987752460254871562>\n{prediction_starter} hat eine Wette gestartet!\nDu kannst jetzt mit \n**!bet (Nummer der Antwort) (Anzahl der zu wettenden Nuggets)** abstimmen.\nOhne die ( )\n**{prediction_name}**\nAntwortmöglichkeiten:")
        active_prediction = True
        closed_prediction = False
        save_prediction()
        # Sends the given options back in one list for better viewability.
        for n, i in enumerate(options):
            await ctx.send(f"**{n+1}**. {i}")


@bot.command(brief="Lässt dich an einer laufenden Wette teilnehmen.")
async def bet(ctx, choice, amount):
    if ctx.channel.id == bet_channel:
        author = ctx.message.author.mention
        global both, total
        # Loads a active prediction from data.json, if there is one.
        load_prediction()
        if active_prediction == False:
            await ctx.send(f"Keine aktive Wette.")
            return
        if closed_prediction == True:
            await ctx.send(f"Wetten sind geschlossen")
            return
        choicenr = int(choice)
        try:
            # If users choose a number higher then the available options, they get an error message.
            if choicenr > len(options):
                await ctx.send(f"Du hast {choicenr} gewählt aber es gibt nur {len(options)} Optionen.")
                return
        except ValueError:
            await ctx.send('Falsche Eingabe!\n !bet "Option" "Anzahl Nuggets"')
            return
        bet = int(amount)
        # Checks if the user has enough coins.
        if not enough_coins(author, bet):
            await ctx.send("Du hast dafür nicht genug Nuggets.")
            return
        choice = options[choicenr - 1]
        # If user already has an active bet.
        if author in both:
            # Refund coins.
            coinchange(author, both[author][0])
        # Adds dictionary entry with user id as key and bet amount and choice(in a list) as value.
        both[author] = [bet, choice]
        # Adds/Removes Coins to/from author.
        coinchange(author, -bet)
        await ctx.send(f"{author} hat {bet} Nuggets auf {choice} gesetzt.\n")
        # Sends the given options back in one list for better viewability.
        ganzesErgebnis = "Aktuelle Einsätze:\n"
        for n, i in enumerate(options):
            coins_on_i = 0
            teilErgebnis = ""
            # Itterates over a list wich has the amount of what a user bet(index 0) and the name of the option(index 1).
            for bet, choice in both.values():
                # If the name of what a user bet on matches the name of an option.
                if choice == i:
                    coins_on_i += int(bet)
            # I do it this way instead of writing directly to the dictionary to avoid KeyErrors when there is no value set to an option.
            sum_of_bets_per_option[i] = coins_on_i
            teilErgebnis = str(
                (f"**{n+1} {i}** - {sum_of_bets_per_option[i]}\n"))
            ganzesErgebnis += teilErgebnis
        await ctx.send(ganzesErgebnis)
        save_prediction()


@bot.command(brief="Schließt eine offene Wette.")
@commands.has_role(bot_secrets.bookie)
async def close(ctx):
    if ctx.channel.id == bet_channel:
        global closed_prediction, active_prediction, total
        # Loads a active prediction from data.json, if there is one.
        load_prediction()
        if active_prediction == False:
            await ctx.send("Keine offene Wette.")
            return
        if prediction_starter != ctx.message.author.mention:
            await ctx.send("Nur ein Wettbüromitarbeiter kann eine Wette schließen!")
            return
        if closed_prediction:
            await ctx.send("Wette ist bereits zu!")
            return
        # Gets total by summing up all bets.
        total = sum([int(f) for f in sum_of_bets_per_option.values()])
        closed_prediction = True
        await ctx.send("Wetten sind jetzt geschlossen!")
        save_prediction()


@bot.command(brief="Zeigt die aktuelle Wette und Einsätze an.")
async def active(ctx):
    if ctx.channel.id == bet_channel:
        load_prediction()
        if active_prediction or closed_prediction:
            await ctx.send(f"Aktuelle Wette: {prediction_name}\n")
            for n, i in enumerate(options):
                await ctx.send(f"**{n+1} {i}**\nGesamt: {sum_of_bets_per_option[i]}")
            return
        await ctx.send("Keine aktive Wette.")


@bot.command(brief="Lässt den Ersteller das Ergebnis verkünden.")
@commands.has_role(bot_secrets.bookie)
async def winner(ctx, winner):
    if ctx.channel.id == bet_channel:
        global active_prediction
        # Loads a active prediction from data.json, if there is one.
        load_prediction()
        if active_prediction == False:
            await ctx.send("Keine offene Wette.")
            return
        if closed_prediction == False:
            await ctx.send("Wette ist noch offen.")
            return
        if prediction_starter != ctx.message.author.mention:
            await ctx.send("Nur der Ersteller kann das Ergebnis verkünden!")
            return
        # decides winner from input. -1 is to correct for the index starting at 0.
        winner = options[int(winner) - 1]
        if winner not in options:
            await ctx.send(f"{winner} war keine Antwortmöglichkeit.\n Antwortmöglichkeiten:")
            # Sends the given options back in one list for better viewability.
            for n, i in enumerate(options):
                await ctx.send(f"**{n+1}**. {i}")
            return
        # Itterates over options to find winner.
        for i in options:
            if i == winner:
                await ctx.send(f"Das Ergebnis ist {winner}!")
                # k = discord user v = list[(index 0 = bet amount), (index 1 = choice)].
                for k, v in both.items():
                    # If user chose the winning option.
                    if v[1] == winner:
                        # Formula to calculate winnings broken down into steps
                        # Step 1: bet amount /  (total bets on that option / 100) = percentage of how much the user bet was compared to all bets on that option
                        # Step 2: result from step 1 / 100 = the multiplier for the percentage
                        # Step 3: result from step 2 * total = payout

                        ## Example bet
                        # user 1 bets 75 on option 1
                        # user 2 bets 25 on option 1
                        # user 3 bets 100 in option 2
                        # option 1 wins

                        # calculation for user1:
                        # 75 / ((75+25) / 100) = 75
                        # 75 / 100 = 0.75
                        # 0.75 * 200 = 150
                        # payout is 150

                        # calculation for user2:
                        # 25 / ((75+25) / 100) = 25
                        # 25 / 100 = 0.25
                        # 0.25 * 200 = 50
                        # payout is 50

                        # calculation for user3:
                        # payout is 0 because they lost
                        winnings = int(
                            round((both[k][0]) / (sum_of_bets_per_option[winner] / 100)) / 100 * int(total))
                        coinchange(k, winnings)
                        await ctx.send(f"{k} won and got {winnings} coins")
                        active_prediction = False
        reset_prediction()


@bot.command(brief="Einmal Täglich Spinnen für die Möglichkeit, Nuggets zu bekommen")
async def spin(ctx):
    if ctx.channel.id == bet_channel:
        author = ctx.message.author.mention
        if not signed_up(author):
            await ctx.send("Du bist nicht registriert! Benutz !signup")
            return
        if Already_played(author) and not infinite_games:
            await ctx.send(f"Du hast heute schon gespielt")
            return
        else:
            update_last_played(author)
            await ctx.send(f"{author} hat " + str(Glücksrad(author)) + " Nuggets gewonnen!")


#asd
#asd
''' skrr'''
'''
@bot.command(brief='Pay to roll 2 6-sided die, choose "seven", "high" or "low"', description= "Costs 50 coins to roll. If you choose high/low correctly you win 100 coins. If you choose seven correctly you win 250 coins.")
async def roll(ctx, choice):
    author = ctx.message.author.mention
    # Checks if user has enough coins.
    if not enough_coins(author, 50):
        await ctx.send("You don't have enough coins.")
        return
    # Rolls dice 1.
    rand1 = random.randint(1, 6)
    # Rolls dice 2.
    rand2 = random.randint(1, 6)
    result = rand1 + rand2# Adds them together.
    # Dictionary to convert numbers to emojis.
    emoji = {1:"1️⃣",2:"2️⃣",3:"3️⃣",4:"4️⃣",5:"5️⃣",6:"6️⃣"}
    # Reloads coins from file.
    load_coins()
    # Adds/Removes Coins to/from author.
    coinchange(author, -50)
    await ctx.send(f"{emoji[rand1]}  {emoji[rand2]}")
    if result == 7 and choice == "seven":
        await ctx.send("**You win 250 Coins!**")
        # Adds/Removes Coins to/from author.
        coinchange(author, 250)
    elif result <= 6 and choice == "low":
        await ctx.send("**You win 100 Coins!**")
        # Adds/Removes Coins to/from author.
        coinchange(author, 100)
    elif result >=8 and choice == "high":
        await ctx.send("**You win 100 Coins!**")
        # Adds/Removes Coins to/from author.
        coinchange(author, 100)
    else:
        await ctx.send("You lost :(")
'''

# on_message triggers on every message.
'''
@bot.event
async def on_message(message):
    author = message.author.mention
    # Returns if the message is from the bot.
    if message.author == bot.user:
        return
    # Checks if any word in the message matches a word on the bad_word list.
    if any(bad_word in message.content.lower().split() for bad_word in bad_words):
        # Deletes message.
        await message.delete()
        await message.channel.send("Du darfst sowas nicht sagen!\n**-100 Nuggets**")
        # Adds/Removes Coins to/from author.
        coinchange(author, -100)
    # Checks if any word in the message matches a word on the slurs list.
    if any(bad_word in message.content.lower().split() for bad_word in slurs):
        # Deletes message.
        await message.delete()
        await message.channel.send("Dieses Wort ist verboten!\n**Du verlierst alle deine Nuggets!**")
        # Adds/Removes Coins to/from author.
        coinchange(author, -coinsd[author])
    # Tells the bot to still listen to commands.
    await bot.process_commands(message)
'''

if BOT_TOKEN == "Your token":
    print("You forgot to add your token. Make sure you read the README.md!")
    print("Closing in 10 Seconds")
    sleep(10)
    exit()

# Starts the bot
bot.run(BOT_TOKEN)
