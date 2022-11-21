#READ ME SECTION
'''
This is a python file, so it needs the extension .py, currently it is .txt just to be able to share it easily

1)go into hypixel on an account and do /api to get your api key, now put that key into the API_KEY variable below inside the " and "
2)go into your discord bot and get the token, then put it into the BOT_TOKEN variable below inside the " and "
3)make sure you are using at least python version 3.6 because f strings are utilised in this program
4) the non default libraries needed for this will be shown below with installations
5) the non default python libraries are: discord.py, requests and MojangAPI
6) to install them run the following commands in your command line of the virtual machine or device
pip install discord.py
pip install requests
pip install mojang

HEROKU ONLY SECTION-----------------
put the following into a file called requirements.txt

discord.py
requests
mojang


put the following into a file called Procfile with no extension, just base file

worker: python pithub_bot.py

-------------------------------------

with these libraries installed and the correct api and bot information, you can now just run the file and the bot will automatically function as intended
for information on creating the actual discord bot, that is easily shown by the discord developer section where you just follow the instructions until you get a bot token and invite link
for the bot

additionally, change special users to include users you want to access special commands

additional info will be added about the other files holding the price guide
'''

#Hypixel API Token
API_KEY = ""

#BOT Token
BOT_TOKEN = ""

#Special User IDS
special_user_ids = []

#Not all the imports are necessary but just copied from another bot project for simplicity
import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import asyncio
import time
import datetime
import random
import math
import re
import pickle
import json
import requests
from mojang import MojangAPI


#Bot Client Commands
Client = discord.Client()
#Prefix Setting Command

intents = discord.Intents.default()
intents.members = True
intents.messages = True

client = commands.Bot(command_prefix=['.', '!'], intents=intents)



#status command, runs when the bot first goes online
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=".help for the command list and bot help")) #Status of the bot
    print('Bot is online and connected to Discord') #message to show the bot is fully connected


#Help Command for the bot
client.remove_command('help') #default help command is removed to make room for the custom one
@client.command(aliases=["Help"])
async def help(ctx):
    #uses an embed to look more professional
    em = discord.Embed(title='__Commands__', description=
    ("**.help**: To view this page"+
     "\n\n**.verify**: Used to verify yourself only in the verify-here channel"+
     "\n\n**.pricecheck**: Returns a pricecheck from the Pithub Price Guided created by Pithub staff and checked by Silly and Jo Nathanz"+
     "\n\n**.ownerhistory**: Use this command to search the ownership history of an item (oh or owner for short)"+
     "\n\n**.status**: Returns the status of a hypixel ign"+
     "\n\n**.events**: Returns an ascending list of upcoming events"+
     "\n\n**.scammercheck**: Used to check if someone is marked as a scammer on pit panda and why"+
     "\n\n**.disable**: Disables or enables another command"+
     "\n\n**.minors**: Joke Command"+
     "\n\n**.coinflip**: Flips a coin"+
     "\n\n**INFO:**: Eunning commands without any extra input (in the correct channel if necessary) will explain its format!"+
     "\n\nIf there are any issues, make a ticket!"), colour=14593471)
    em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=em)


#command to disable and enable commands incase there is an issue or probelm with anything the bot is doing
@client.command()
async def disable(ctx, command):
    #makes sure that the only people who can disable bot commands are in the special user id list
    if ctx.author.id in special_user_ids:

        #gets command object
        command = client.get_command(command)
        if command is None:
            await ctx.send("Couldn't find that command")
            return

        #flips the state of the command then stores the state for a message
        command.enabled = not command.enabled
        new_state = command.enabled
        await ctx.send(f"Command has been changed to {new_state}")
        
    else:
        await ctx.send("You are not powerful enough to disable/enable commands")


#pit player count command
#channel name changes are limited to twice every 10 minutes, this command updates once every 10 minutes but could be as fast as every 5 minutes (unnecessary)
@tasks.loop(minutes=10)
async def playercount():
    try:
        playercounts = requests.get(f"https://api.hypixel.net/gameCounts?key={API_KEY}").json()
        pitcount = playercounts["games"]["PIT"]["players"]
        channel_name = f"Pit Player Count: {pitcount}"
        channel = client.get_channel(1001815202855129202)
        await channel.edit(name=channel_name)
    except:
        pass

#starts the loop
playercount.start()

#pit player count command
#channel name changes are limited to twice every 10 minutes, this command updates once every 10 minutes but could be as fast as every 5 minutes (unnecessary)
@tasks.loop(minutes=10)
async def servercount():
    try:
        pithub = client.get_guild(904154208989761617)
        membercount = pithub.member_count
        channel_name = f"Pithub Members: {membercount}"
        channel = client.get_channel(1001824992981422210)
        await channel.edit(name=channel_name)
    except:
        pass

#starts the loop
servercount.start()


#Returns the current status of hypixel players
@client.command(aliases=["online", "isonline", "onlinecheck"])
async def status(ctx, username=None):
    
    if username==None: #tutorial for command if no username provided
        await ctx.send("This command returns the current hypixel status of players. Format: .status username")
        return

    #trys to get the uuid, if no uuid is found then an account with that username doesn't currently exist
    try:
        uuid = MojangAPI.get_uuid(username)
        if uuid == None:
            raise ValueError
    except:
        await ctx.send("Sorry, that username doesn't exist.")
        return

    #API request for player information
    requestlink = str(f"https://api.hypixel.net/status?key={API_KEY}&uuid=" + uuid)

    #converts to a json for parsing
    status_data = requests.get(requestlink).json()

    #gathers the online session data
    session_data = status_data["session"]
    online = session_data["online"]
    
    if online is False:
        body = "**OFFLINE**"
    else:
        # gathers additional data if the player is online about their current game
        gametype = session_data["gameType"]
        mode = session_data["mode"]
        body = f"**ONLINE** \nGametype: {gametype}\nMode: {mode}"


        
    #creates a status embed for the professional look
    status_embed = discord.Embed(title=f'Status Query: **{username}**', description = body, colour=12745742)
    status_embed.set_image(url=f"https://mc-heads.net/avatar/{uuid}")
    await ctx.send(embed=status_embed)

#Not commented yet 
#Returns the pit panda scammer status of a player
@client.command(aliases=["Scammercheck", "sc", "Sc"])
async def scammercheck(ctx, username=None): #If username is not provided the command instead returns a mini tutorial

    #checks if the command has a username provided to see if a tutorial is needed
    if username == None:
        await ctx.send("To use this command, you use the format **.scammercheck ign**")
        return

    #tries to get their uuid and gives a default error message if the user doesn't exist
    try:
        uuid = MojangAPI.get_uuid(username)
    except:
        await ctx.send("Sorry, that username doesn't exist.")
        return

    requestlink = f"https://pitpanda.rocks/api/players/{username}"
    panda_player_data = requests.get(requestlink).json()

    #parses the pit panda information to find scammer type and description
    sidebar = panda_player_data["data"]["displays"]
    scammer = False
    scam_desc = None
    scam_desc2 = None
    main_uuid = None
    for item in sidebar:
        try:
            value = item["type"]
            if value == "scammer":
                scammer = True
                if scam_desc == None:  
                    scam_desc = item["notes"]
                else:
                    scam_desc2 = item["notes"]

                try:
                    main_uuid = item["main"]
                except:
                    pass
        except:
            pass

    #creates the embed body for scammer or non scammer
    if scammer == False:
        body = "**Innocent**\n" + "Not a scammer but still be careful trading!"
    else:
        body = "**Scammer**\n"+ "Marked as a scammer on Pit Panda. Do not trust this player!\n\n" + f"**Notes**:\n{scam_desc}"
        if scam_desc2 != None:
            body += f"\n" + f"**Additional Notes**\n" + f"{scam_desc2}"
        if main_uuid != None:
            requestlink = f"https://api.mojang.com/user/profiles/{main_uuid}/names"
            namedata = requests.get(requestlink).json()
            current_name = namedata[-1]["name"]
            
            body += f"\n\n" + f"**Main**\n" + f"{current_name}"
        

    #scammed embed
    scammer_embed = discord.Embed(title=f'**{username}**', description=body, colour=14593471)
    scammer_embed.set_image(url=f"https://crafatar.com/avatars/{uuid}?overlay=true")
    await ctx.send(embed=scammer_embed)


#Returns the pit panda scammer status of a player
@client.command(aliases=["st"])
async def scammertag(ctx): #If username is not provided the command instead returns a mini tutorial
    if ctx.author.id not in special_user_ids :
        return


    scam_role = discord.utils.get(ctx.guild.roles, name="Scammer")

    for user in ctx.guild.members:
        
        
        try:
            nickname = user.nick
            if nickname == None:
                nickname = str(user).split("#")[0]

                
            requestlink = f"https://pitpanda.rocks/api/players/{nickname}"
            panda_player_data = requests.get(requestlink).json()

            sidebar = panda_player_data["data"]["displays"]
            scammer = False
            for item in sidebar:
                try:
                    value = item["type"]
                    if value == "scammer":
                        scammer = True
                except:
                    pass

            if scammer == True:
                await user.add_roles(scam_role)

                

        except:
            pass


       
#verification command
@client.command(aliases=["Verify", "verification"])
async def verify(ctx, username=None): #If username is not provided the command instead returns a mini tutorial

    #makes the command only work on the verify-here channel
    if ctx.channel.id != 960421193893183548:
        return

    #checks if the command has a username provided to see if a tutorial is needed
    if username == None:
        await ctx.send("To access the server you must verify your ingame username.\n**.verify ign**")
        return

    #temporary verification message object that is deleted if verification is completed
    verifying_msg = await ctx.send("Verifying... might take a few seconds!")

    #MojangAPI library is used to get the uuid from someone's username, if nothing is returned then that username doesn't exist
    try:
        uuid = MojangAPI.get_uuid(username)
    except:
        await ctx.send("Sorry, that username doesn't exist.")
        return

    #Some requests depending on when/how the name was changed can return None rather than give an error so this catches any non-existant usernames missed by the try except
    if uuid == None:
        await ctx.send("That account does not exist.")

    #request link to the hypixel api for that specific player
    requestlink = str(f"https://api.hypixel.net/player?key={API_KEY}&uuid=" + uuid)

    #data is requested in json format for parsing
    hydata = requests.get(requestlink).json()

    #if an aspect of hypixel isnt used, it provides no data rather than a False statement. if the links section doesn't contain a discord then nothing was linked at all on the account
    try:
        linked_discord_tag = hydata["player"]["socialMedia"]["links"]["DISCORD"]
        if linked_discord_tag == None:
            raise ValueError #error doesn't matter, just needs to raise an exception, same None check as earlier because sometimes doesn't exist and sometimes its None
    except:
        await ctx.send("You have not linked a valid discord to your hypixel account.")
        await ctx.send("<#1001096469077565540>") #this mentions the verification tutorial channel through the format <#id>
        return

    #this checks if the discord tag in hypixel matches the discord tag of the original messager
    if str(ctx.author) == linked_discord_tag:

        #creates objects for the verified and unverified roles based on name so they can be more easily edited and deleted/remade as long as the name is kept the same
        verified_role = discord.utils.get(ctx.guild.roles, name=str("Verified"))
        unverified_role = discord.utils.get(ctx.guild.roles, name=str("Unverified"))

        #unnecessary feature that added additional text that made the bot look more clunky, kept incase this will be needed
        #if verified_role in ctx.author.roles:
            #await ctx.send("You have already been verified but might be missing other roles.")

        #this loop attempts to give the roles but depending on factors listed below, it might cause an error
        #1) the bot is below other users which means it can't change their nickname or certain roles
        #2) the hypixel api returned an unexpected result for one of the ranks/roles
        #3) it can't locate certain roles
        #4) to avoid this breaking the bot, if any part of it fails it says "some roles have been added". usually if an error occurs
        # it occurs in later less important section compared to general verification that can be more easily remedied e.g. not being given mvp rank vs not being verified at all
        
        try:

            #this blocks edits roles and nicknames
            #ordered with most important parts at the top so if a later part fails they are still verified in the important ways
            await ctx.author.add_roles(verified_role) #gives verified role
            await ctx.author.remove_roles(unverified_role) #removes unverified role
            await ctx.author.edit(nick=str(username)) #changes their nickname

            #This gives the correct role/bracket name depending on prestige
            #A switch statement should have been used here but the version of python was 3.6.7 and I didn't want to update to 3.10 and have any unexpected library issues
            #just to reduce this command slightly
            prestige = hydata['player']['stats']['Pit']["profile"]["prestiges"][-1]["index"]
            if prestige == 0:
                role_name = "non"
            elif prestige < 5:
                role_name = "Blue Brackets [I]"
            elif prestige < 10:
                role_name = "Yellow Brackets [V]"
            elif prestige < 15:
                role_name = "Orange Brackets [X]"
            elif prestige < 20:
                role_name = "Red Brackets [XV]"
            elif prestige < 25:
                role_name = "Purple Brackets [XX]"
            elif prestige < 30:
                role_name = "Pink Brackets [XXV]"
            elif prestige < 35:
                role_name = "White Brackets [XXX]"
            elif prestige < 40:
                role_name = "Aqua Brackets [XXXV]"
            elif prestige < 45:
                role_name = "Dark Blue Brackets [XL]"
            elif prestige < 50:
                print("no idea what this role will be") #the bracket colour is unknown so it exits the loop
                return
            elif prestige == 50:
                print("no idea what this role will be") #the bracket colour is unknown so it exits the loop
                return

            #uses the information above to find the correct role and give it
            bracket_role = discord.utils.get(ctx.guild.roles, name=role_name)
            await ctx.author.add_roles(bracket_role)


            #sorts through hypixel rank information to find the correct rank
            try:
                rank = hydata['player']["newPackageRank"]
            except:
                rank = None
            try:
                rank_ = hydata['player']["monthlyPackageRank"]
            except:
                rank_ = None
            if rank == "VIP":
                rank = "VIP"
            elif rank == "VIP_PLUS":
                rank = "VIP+"
            elif rank == "MVP":
                rank = "MVP"
            elif rank == "MVP_PLUS":
                rank = "MVP+"
            else:
                rank = None
            if rank_ == "SUPERSTAR":
                rank = "MVP++"
            if rank != None: #if the rank is None then they have no rank so no roles need to be added
                #finds and assigns the rank
                rank_role = discord.utils.get(ctx.guild.roles, name=rank)
                await ctx.author.add_roles(rank_role)



            requestlink = f"https://pitpanda.rocks/api/players/{username}"
            panda_player_data = requests.get(requestlink).json()

            #parses the pit panda information to find scammer type and description
            sidebar = panda_player_data["data"]["displays"]
            scammer = False
            for item in sidebar:
                try:
                    value = item["type"]
                    if value == "scammer":
                        scammer = True
                except:
                    pass

            
            #creates the verification embed using data from earlier
            verify_embed = discord.Embed(title=f'Verified: {username}', description=f"**Bracket**: {role_name}\n" + f"**Rank**: {rank}\n" + f"**Discord**: {str(ctx.author)}")
            verify_embed.set_image(url=f"https://crafatar.com/avatars/{uuid}?overlay=true")
            if scammer == True:
                verify_embed.set_footer(text="**SCAMMER**")
                scam_role = discord.utils.get(ctx.guild.roles, name="Scammer")
                await ctx.author.add_roles(scam_role)
                
            await ctx.send(embed=verify_embed)

            #deletes the earlier referenced temporarily verification message
            await verifying_msg.delete()
        except:
            await ctx.send("Some roles have been added.") #error message incase only part of the process was completed
        
    else:
        #Generic unable to find the account error message
        await ctx.send("We were unable to verify that account. Please make sure you follow the guide linked below and check for any spelling mistakes.  https://youtu.be/0JmXxBN3Gv0")
        return


#Currently doesn't function due to the api link used currently returning no data 
@client.command(aliases=["events", "Events", "EVENTS", "Event",])
async def event(ctx):

    #removed event role feature requiring users to get a role to use the command
    #event_role = discord.utils.find(lambda r: r.name == "Ingame-events", ctx.message.guild.roles)
    
    if ctx.channel.id not in [1001793918624604170, 904174184647757865]: #limits this command to event channels
        await ctx.send("Sorry, to avoid spam this command is limited to a pre approved events checking channel and commands channel.")
        return

    #same removed event role feature
    #elif event_role not in ctx.author.roles:
        #await ctx.send("You need the ingame events role to use this command.")
        #return

    #uses this api link
    events = requests.get("https://events.mcpqndq.dev/").json()

    events = events[:20] #artifically limiting how many events since the default next 20 hours made too many messages

    
    #The code below haa been left since it could be used in future versions of this bot and other commands
    #The code is currently unnecessary since the number of events is capped at 20 by an earlier statement, but if it shows unlimited events then this page splitting
    # is necessary
    events_by_page = []
    page = 1
    while (page-1)*50 < len(events):
        
        events_by_page.append(events[(page-1)*50 : (page-1)*50+50])

        page += 1

    #uses a loop to append additional information to the overall body, a new body is created for every embed sent
    page = 1
    for event_page in events_by_page:
        body = ""
        for event in event_page:
            event_info = ""

            event_name = event["event"]
            event_type = event["type"]
            
            event_timestamp = event["timestamp"]
            event_time_until_seconds = event_timestamp/1000 - time.time() #finding the difference in unix standard time, miliseconds since api provides event time in unix (3 extra 0s??? so i also divide by 1000 to eliminate them)
            event_time_format = (str(datetime.timedelta(seconds=event_time_until_seconds)).split(".")[0]).split(":")
            
            event_info += f"**{event_name}** ({event_type}): {event_time_format[0]} hours : {event_time_format[1]} minutes : {event_time_format[2]} seconds\n"

            body += event_info

        
        event_embed = discord.Embed(title=f'**Upcoming Events {page}**', description=
        (body + "\n\nIf there are any issues, make a ticket!"), colour=14593471)
        event_embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=event_embed)

        page += 1
        
#converts enchants to their relevant pit panda name, accepts a large list as input with enchant names
def pit_panda_enchant_conversion(enchants): #takes a list of enchants as input and converts based on pit_to_panda dictionary from key to value and no number to 0+, while keeping 1,2,3
    new_enchants = []

    #Part below: takes the last part of an enchant name, removes and stores the number. e.g. mlb3 is converted into mlb and 3, or mlb into mlb and 0+
    for enchant in enchants:
        if enchant[-2:] == "0+":
            number = "0+"
            enchant = enchant[:-2]
        elif enchant[-1].isdigit():
            number = enchant[-1]
            enchant = enchant[:-1]
        else:
            number = "0+"
            
        if enchant in pit_to_panda:
            enchant = pit_to_panda[enchant]

        enchant += number #add the number back on after converting it with the dictionary
        new_enchants.append(enchant)
        
    return new_enchants #returns the new enchantment list


#combines the numbers of enchants into 1 word if they have spaces e.g. perun 3 ls 3 into perun3 ls3
def combining_enchant_lists(enchants): #takes list of enchants as input e.g. ["perun", "3", "ls", "3"]

    #makes sure the data given isnt in set format but in list format so that order matters which is important for the iterative process where enchant order matters
    if not isinstance(enchants, list):
        enchants = list(enchants)

    #loops through every element in enchants
    for i in range(len(enchants)):
        try:
            #if the "enchant slot" is just a digit then it belongs to the previous enchant so its joined to the previous list element
            if enchants[i].isdigit():
                enchants[i-1:i+1] = [''.join(map(str,enchants[i-1:i+1]))]

                #this function is run recursively because the number of elements and positions in the list changes when elements are combined
                #it runs recursively until it fully finishes a cycle with no changes needed so no rouge numbers
                enchants = combining_enchant_lists(enchants)
        except:
            pass
        
    return enchants
    #returns the final list with proper enchant structure    return enchants



#item history command
#command can give accuracy down to seconds but that was not necessary

@client.command(aliases=["ownersearch", "history", "ownerhistory", "Ownersearch", "History", "Ownerhistory", "oh"])
async def itemhistory(ctx, ign=None, *enchants): #accepts information in the form: .itemhistory enchant1 enchant2 enchant3

    enchants = combining_enchant_lists(enchants)

    #acquires the approved roles for this command in the form of role objects based on the list of names below
    approved_roles_names = ["Staff", "Server-Booster", "Bot Access (Owner/Dev Friend)", "Owner"]
    approved_roles = []
    for role_name in approved_roles_names:
        role = discord.utils.find(lambda r: r.name == role_name, ctx.message.guild.roles)
        approved_roles.append(role)

    #checks that the user has the above roles
    if not any(role in approved_roles for role in ctx.author.roles):
        await ctx.send("Sorry, ,that command is currently restricted for testing and other purposes.")
        return


    #checks that the following conditions are met
    #correct channels for item ownership searching are used
    #an ign was provided, if not then the command is run as a tutorial instead
    #if more than 3 enchants are provided, the command ends here as the item cannot exist in the current state of pit
    approved_channel_ids = [904174184647757865, 1001654075902931044, 1001644337525960704, 1001644377166327869, 1001650170255114290, 964212085015855184]
    if ctx.channel.id not in approved_channel_ids:
        await ctx.send("Sorry, this is not an approved channel for the command. This is to avoid spam as 1 single search can span up to 10 pages.")
        return
    elif ign==None:
        await ctx.send("__Format__ \n" +".itemhistory ign enchant1 enchant2 \n" + "**Example:** .itemhistory 98rs megalongbow1 telebow3")
        return
    elif len(enchants)>3:
        await ctx.send("You can't have more than 3 enchants on an item unless you are minikloon or his e girl.")
        return

    #the pit panda api is used here
    #the request link to find the items from a search is created below using the information provided
        
    
    requestlink = "https://pitpanda.rocks/api/itemsearch/"
    requestlink += "uuid" + str(ign)
    enchants = pit_panda_enchant_conversion(enchants)
    for enchant in enchants:
        requestlink += ("," + str(enchant))

    item_data = requests.get(requestlink).json()

    items = item_data["items"]

    #the command currently doesn't allow item selection if more than 1 search is returned just because it was released immediately after it was made and I didn't get around to it
    if len(items) > 1:
        await ctx.send("Too broad, more than 1 matching option found and I am too lazy to code the additional item display menus right now, but I will in the future")
        return
    elif len(items) == 0:
        await ctx.send("No matching items found, it might exist but pit panda was currently unable to find it.")

    item_id = items[0]["id"]

    #once the item id is acquired a new api request is done for ownership history using that item id
    requestlink = "https://pitpanda.rocks/api/item/"
    requestlink += str(item_id)

    item_history = requests.get(requestlink).json()
    owners = item_history["item"]["owners"] #list of dictionaries where each dictionary has owner information in the keys: "uuid" and "time"

    #an embed splitting mechanism is used because there can be up to 100 owners which wouldn't fit into 1 embedded message
    owners_by_page = []


    #section below converts the information into pages, code is kinda scuffed because I just used something I wrote years ago for a bot
    page = 1
    while (page-1)*10 < len(owners):
        
        owners_by_page.append(owners[(page-1)*10 : (page-1)*10+10])

        page += 1

    page = 1
    for owner_page in owners_by_page:
        body = ""
        for owner in owner_page:
            owner_info = ""
            
            owner_ign = MojangAPI.get_username(owner['uuid'])
            
            owner_time_unformat = owner["time"][:19]
            owner_time = owner_time_unformat.replace("T", " | ")
            
            owner_info += f"**{owner_ign}**\n"
            owner_info += f"Date of Ownership: {owner_time}\n"

            body += owner_info
            body += "\n"

        
        owner_embed = discord.Embed(title=f'Owners Page {page}', description=
        (body + "\n\nIf there are any issues, make a ticket!"), colour=14593471)
        owner_embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=owner_embed)

        page += 1



#Joke command that just returns a message
@client.command(aliases=["minor", "Minors", "Minor"])
async def minors(ctx):
    await ctx.send("Nightloot's favourite thing")
    

#basic coinflip command
@client.command()
async def coinflip(ctx):
    roll = random.choice(["Heads", "Tails"])
    await ctx.send(f"Rolled: {roll}")


#Not fully commented
#Price guide command
#Data structure, sets will act as keys for prices
#There will be a parsing section to convert the price guide currently online into this usable format of having 2-4 length of objects sets
#this is because every set will contain one of "sword", "bow" or "pants" and then up to 3 enchant names which will include numbers
    
with open('priceguide.pickle', 'rb') as handle:
    priceguide = pickle.load(handle) 

@client.command(aliases=["Pricecheck", "pc", "Pc", "price", "Price", "PC"])
async def pricecheck(ctx, *data):

    #makes the command only work on the bot-commands and price check channels
    if ctx.channel.id not in [942544538747150366, 904174184647757865]:
        return
    
    data = combining_enchant_lists(data)

    arranged_data = []
    for item in data:
        try:
            item = item.lower()
        except:
            pass
        if item[:-1] in short_to_long_mystics.keys():
            digit = list(item)[-1]
            item = item[:-1]
            proper_name = short_to_long_mystics[item]
            with_number = proper_name + digit
            arranged_data.append(with_number)
        else:
            arranged_data.append(item)
    data = arranged_data

    data = set(data)
    
    mystic_types = ["sword", "bow", "pants"]
    
    if len(data)>4:
        await ctx.send("Currently, you have included more than 4 elements which can't exist. (Note: ensure no spaces between enchantments and their level e.g. bill3 vs bill 3.")
        return
    elif not any(item in mystic_types for item in data):
        await ctx.send("You have not included a specification for the mystic type e.g. sword or pants.")
        await ctx.send("To use this command, use the following format: .pricecheck sword/bow/pants enchant1 enchant2 enchant3")
        return

    try:
        price = priceguide[frozenset(data)]
        if "ðÿ’§" in price:
            price = price.replace("ðÿ’§", "water")
        if price==None:
            raise ValueError

        enchants = ""
        for enchant in data:
            enchants += enchant + " "
            
        await ctx.reply(f"**Price check**: {price}")
        
    except:
        await ctx.send("Sorry that item was not found in the price guide.")
        return


#general dictionary to convert short enchant names into the full name no spaces no caps plain text
short_to_long_mystics ={
"toxic" : "reallytoxic",
"cd" : "combodamage",
"cdmg" : "combodamage",
"cmg" : "combodamage",
"ch" : "comboheal",
"cheal" : "comboheal",
"pun" : "punisher",
"punish" : "punisher",
"fancy" : "fancyraider",
"fr" : "fancyraider",
"pf" : "painfocus",
"kb" : "kingbuster",
"cs" : "comboswift",
"moct" : "moctezuma",
"moc" : "moctezuma",
"sw" : "sweaty",
"ds" : "diamondstomp",
"stomp" : "diamondstomp",
"dstomp" : "diamondstomp",
"br" : "bountyreaper",
"breaper" : "bountyreaper",
"reaper" : "bountyreaper",
"ls" : "lifesteal",
"bill" : "billionaire",
"bil" : "billionaire",
"exe" : "executioner",
"gboost" : "goldboost",
"boost" : "goldboost",
"gb" : "goldboost",
"gbump" : "goldbump",
"bump" : "goldbump",
"cxp" : "comboxp",
"mlb" : "megalongbow",
"mega" : "megalongbow",
"drain" : "sprintdrain",
"pin" : "pindown",
"ftts" : "fasterthantheirshadows",
"chip" : "chipping",
"pcts" : "pushcomestoshove",
"para" : "parasite",
"pull" : "pullbow",
"tele" : "telebow",
"dc" : "devilchicks",
"explo" : "explosive",
"lucky": "luckyshot",
"true" : "trueshot",
"fletch" : "fletching",
"bq" :"bottomlessquiver",
"bottom" :"bottomlessquiver",
"bottomless" :"bottomlessquiver",
"quiver" :"bottomlessquiver",
"rgm" : "retrogravitymicrocosm",
"retro" : "retrogravitymicrocosm",
"cf" : "criticallyfunky",
"funky" : "criticallyfunky",
"blob" : "pitblob",
"pblob" : "pitblob",
"reg" : "regularity",
"nw" : "newdeal",
"new" : "newdeal",
"frac" : "fractionalreserve",
"fract" : "fractionalreserve",
"fractional" : "fractionalreserve",
"notglad" : "notgladiator",
"gtgf" : "gottagofast",
"fast" : "gottagofast",
"dag" : "davidandgoliath",
"ghearts" : "goldenhearts",
"da" : "diamondallergy",
"hth" : "huntthehunter",
"sing" : "singularity",
"soli" : "solitude",
"booboo" : "booboo",
"pero" : "peroxide",
"respawnabs" : "respawnabsorption"

}

    

#general dictionary used in another function to convert regular mystic enchant names to the ones used in pit panda
#Could be loaded in from another file but unnecessary in its current form because of the relatively low size of the program
pit_to_panda = {"pitmba": "pit_mba",
"mba" : "pit_mba",
"fractionalreserve" : "fractional_reverse",
"fractional" : "fractional_reserve",
"frac" : "fractional_reserve",
"paparazzi" : "paparazzi",
"papa" : "paparazzi",
"robinhood" : "homing",
"doublejump" : "double_jump",
"dj" : "double_jump", 
"arrowarmory" : "damage_per_arrow",
"bottomlessauiver" : "gain_arrows_on_hit",
"bq" : "gain_arrows_on_hit",
"chipping" : "arrow_true_damage",
"chip" : "arrow_true_damage",
"criticallyrich" : "gold_per_crit",
"critrich" : "gold_per_crit",
"fasterthantheirshadow" : "bow_combo_speed",
"ftts" : "bow_combo_speed",
"fletching" : "bow_damage",
"fletch" : "bow_damage",
"firstshot" : "first_shot",
"fs" : "first_shot",
"goldboost" : "gold_boost",
"gb" : "gold_boost",
"gboost" : "gold_boost",
"goldbump" : "gold_per_kill",
"gbump": "gold_per_kill",
"jumpspammer" : "jump_spammer",
"js" : "jump_spammer",
"mixedcombat" : "mixed_combat",
"moctezuma" : "gold_strictly_kills",
"moct" : "gold_strictly_kills",
"pantsradar" : "pants_radar",
"pr" : "pants_radar",
"parasite" : "parasite",
"para" : "parasite",
"pindown" : "pin_down",
"pin" : "pin_down",
"pushcomestoshove" : "punch_once_in_a_while",
"pcts" : "punch_once_in_a_while",
"spammerandproud" : "bow_spammer",
"sap" : "bow_spammer",
"sprintdrain" : "bow_slow",
"drain": "bow_slow",
"sniper" : "sniper",
"strikegold" : "gold_per_hit",
"sweaty" : "streak_xp",
"sw" : "streak_xp",
"whatdoesntkillyou" : "heal_on_shoot_self",
"wdky" : "heal_on_shoot_self",
"wasp" : "bow_weakness_on_hit",
"xpboost" : "xp_boost",
"megalongbow" : "instant_shot",
"mlb": "instant_shot",
"mega": "instant_shot",
"telebow" : "telebow",
"tele" : "telebow",
"explosive" : "explosive_bow",
"explo" : "explosive_bow",
"volley" : "volley",
"pullbow" : "pullbow",
"pull": "pullbow",
"pb": "pullbow",
"devil chicks" : "explosive_chickens",
"dc" : "explosive_chickens",
"trueshot" : "bow_to_true_damage",
"true": "bow_to_true_damage",
"luckyshot" : "lucky_shot",
"lucky" : "lucky_shot",
"billy" : "less_damage_when_high_bounty",
"booboo" : "passive_health_regen",
"creative" : "wood_blocks",
"cricket" : "power_against_crits",
"criticallyfunky" : "power_against_crits",
"critfunky" : "power_against_crits",
"cf" : "power_against_crits",
"counter-offensive" : "speed_when_hit_few_times",
"co" : "speed_when_hit_few_times",
"dangerclose" : "less_damage_vs_bounties",
"davidandgoliath" : "less_damage_vs_bounties",
"dag" : "less_damage_vs_bounties",
"diamondallergy" : "less_damage_vs_diamond_weapons",
"da" : "less_damage_vs_diamond_weapons",
"eggs" : "eggs",
"electrolytes" : "refresh_speed_on_kill",
"elec" : "refresh_speed_on_kill",
"excess" : "overheal_enchant",
"goldenheart" : "absorption_on_kill",
"ghearts": "absorption_on_kill",
"gheart": "absorption_on_kill",
"gottagofast" : "perma_speed",
"gtgf": "perma_speed",
"hearts" : "higher_max_hp",
"huntthehunter" : "counter_bounty_hunter",
"hth" : "counter_bounty_hunter",
"laststand" : "resistance_when_low",
"lodbrok" : "increase_armor_drops",
"mcswimmer" : "less_damage_when_swimming",
"mirror" : "immune_true_damage",
"negotiator"  : "contract_rewards",
"nego" : "contract_rewards",
"notgladiator" : "less_damage_nearby_players",
"notglad": "less_damage_nearby_players",
"pebble" : "increase_gold_pickup",
"peroxide" : "regen_when_hit",
"pero" : "regen_when_hit",
"prick" : "thorns",
"protection" : "damage_reduction",
"prot": "damage_reduction",
"respawnabsorption" : "respawn_with_absorption",
"respawnabs" : "respawn_with_absorption",
"respawnresistance" : "respawn_with_resistance",
"respawnres" : "respawn_with_resistance",
"revitalize" : "regen_speed_when_low",
"self-checkout" : "max_bounty_self_claim",
"selfcheck" : "max_bounty_self_claim",
"checkout" : "max_bounty_self_claim",
"seco" : "max_bounty_self_claim",
"steaks" : "steaks_on_kill",
"tnt" : "tnt",
"assassin" : "sneak_teleport",
"divinemiracle" : "chance_dont_lose_life",
"divine" : "chance_dont_lose_life",
"doublejump" : "double_jump",
"dj" : "double_jump",
"escapepod" : "escape_pod",
"gomrawsheart" : "regen_when_ooc",
"instaboom" : "instaboom_tnt",
"phoenix" : "phoenix",
"pitBlob" : "the_blob",
"pitblob" : "the_blob",
"blob" : "the_blob",
"singularity" : "singularity",
"sing" : "singularity",
"snowballs" : "snowballs",
"snowmenarmy" : "snowmen",
"wolfpack" : "wolf_pack",
"solitude" : "solitude",
"soli" : "solitude", 
"retrogravitymicrocosm" : "rgm",
"rgm" : "rgm",
"berserker" : "melee_crit_midair",
"bers" : "melee_crit_midair",
"bountyreaper" : "melee_damage_vs_bounties",
"breaper" : "melee_damage_vs_bounties",
"bullettime" : "blocking_cancels_projectiles",
"bt" : "blocking_cancels_projectiles",
"bruiser" : "increased_blocking",
"combodamage" : "melee_combo_damage",
"cd" : "melee_combo_damage",
"comboheal" : "melee_combo_heal",
"ch" : "melee_combo_heal",
"comboswift" : "melee_combo_speed",
"swift" : "melee_combo_speed",
"cs" : "melee_combo_speed",
"comboxp" : "combo_xp",
"cxp" : "combo_xp",
"counterjanitor" : "resistance_on_kill",
"cj" : "resistance_on_kill",
"crush" : "melee_weakness",
"diamondstomp" : "melee_damage_vs_diamond",
"ds" : "melee_damage_vs_diamond",
"duelist" : "melee_strike_after_block",
"fancyraider" : "melee_damage_vs_leather",
"fancy" : "melee_damage_vs_leather",
"grasshopper" : "melee_damage_when_on_grass",
"goldandboosted" : "melee_damage_when_absorption",
"gab" : "melee_damage_when_absorption",
"guts" : "melee_heal_on_kill",
"kingbuster" : "melee_damage_vs_high_hp",
"kb" : "melee_damage_vs_high_hp",
"lifesteal" : "melee_heal_on_hit",
"ls" : "melee_heal_on_hit",
"painfocus" : "melee_damage_when_low",
"pf" : "melee_damage_when_low",
"pitpocket" : "pickpocket",
"pickpocket" : "pickpocket",
"punisher" : "melee_damage_vs_low_hp",
"pun" : "melee_damage_vs_low_hp",
"revengeance" : "melee_avenge",
"sierra" : "gold_per_diamond_piece",
"shark" : "melee_damage_when_close_low_players",
"sharp" : "plain_melee_damage",
"billionaire" : "melee_literally_p2w",
"bill" : "melee_literally_p2w",
"bil" : "melee_literally_p2w",
"perunwrath" : "melee_lightning",
"perun" : "melee_lightning",
"combostun" : "melee_stun",
"stun" : "melee_stun",
"executioner" : "melee_execute",
"exe" : "melee_execute",
"gamble" : "melee_gamble",
"healer" : "melee_healer",
"hemorrhage" : "melee_bleed",
"hemo" : "melee_bleed",
"knockback" : "melee_knockback",
"knock" : "melee_knockback",
"speedyhit"  : "melee_speed_on_hit",
"thepunch" : "melee_launch",
"punch" : "melee_launch"}


#runs the bot on discord
client.run(BOT_TOKEN)


