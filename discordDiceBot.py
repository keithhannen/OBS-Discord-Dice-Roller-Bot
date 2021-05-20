#imports
import discord
import asyncio
import simpleobsws
from discord.ext import commands
import random

#variables
loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host='127.0.0.1', port=4444, password='YOUR_OBS_WEBSOCKETS_PASSWORD', loop=loop) # <---remember to change host ip if on a different computer!
bot = commands.Bot(command_prefix='!')

#definitions
async def make_request(diceRoll='1d4'):
    # connect to obs
    await ws.connect() 
    # create the browser source diceBot in the scene LIVE
    await ws.call(
        'CreateSource', {
            'sourceName':'diceBot', 
            'sourceKind':'browser_source', 
            'sceneName':'LIVE', # <--- change to your scene
            'setVisible':True
        }
    )
    # pass settings to source
    await ws.call(
        'SetSourceSettings', {
            'sourceName':'diceBot', 
            'sourceSettings': {
                'css': '', 
                'height': 1080, # <--- change to match obs resolution
                'shutdown': True, 
                'url': 'http://dice.bee.ac/?dicehex=4E1E78&labelchex=CC9EEC&chromahex=00ff00&roll&d='+diceRoll, 
                'width': 1920 # <--- change to match obs resultion
            }
        }
    )
    # chroma key added to the source diceBot
    await ws.call(
        'AddFilterToSource', {
            'sourceName':'diceBot',
            'filterName':'Chroma Key',
            'filterType': 'chroma_key_filter', 
            'filterSettings':{
            }
        }
    )
    # how long the diceBot source exists
    await asyncio.sleep(7)
    # delete the source diceBot from the scene LIVE
    await ws.call(
        'DeleteSceneItem', {
            'scene':'LIVE', # <--- change to your scene
            'item':{
                'name':'diceBot'
            }
        }
    )
    # disconnect from OBS
    await ws.disconnect()

#commands  
# basic dice rolling command          
@bot.command(name='r', help='Simulates rolling dice. Uses d notation. ex: 3d6')
async def roll(ctx, roll):
    roll = roll.split('d')
    number_of_dice = int(roll[0])
    number_of_sides = int(roll[1])
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))
    r = 1
    results = '@' + str(dice[0]) 
    for x in dice[1:]:
        results = results + '%2' + str(dice[r]).zfill(2)
        r = r+1
    await make_request(str(number_of_dice)+'d'+str(number_of_sides)+results)

# run the bot
bot.run('YOUR_DISCORD_BOT_TOKEN')