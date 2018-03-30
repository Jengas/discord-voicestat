import discord
import logging
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
from flata import Flata, where, Query
from flata.storages import JSONStorage
import json
import threading
import time

t = None

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

db = Flata('db.json', storage=JSONStorage)
db.table('stats')
tb = db.get('stats')
# Start if script

client = Bot(description="Discord BOT that collects info about people being in voice channel", command_prefix="$", pm_help = False)

@client.event
async def on_ready():
	print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
	print('--------')
	print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
	print('--------')
	print('Use this link to invite {}:'.format(client.user.name))
	print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
	print('--------')
	print('You are running VoiceStatBot v0.1') #Do not change this. This will really help us support you, if you need support.
	print('Created by Jengas')
	print(' ')
	print(' ')
	return await client.change_presence(status="invisible", game=discord.Game(name='pony status')) #This is buggy, let us know if it doesn't work.

@client.event
async def on_voice_state_update(before, after):

    if str(before.voice_channel) == "None":
        print(after.name + " joined " + str(after.voice_channel))
        getdata = tb.search(Query().uid == after.id)
        try:
            result_checkforuser = getdata[0]['uid']
        except:
            db.table('stats').insert({'name': after.name, 'time': 0, 'uid': after.id })
        try:
            getstartpoint = getdata[0]['time']
            print('Startpoint is ' + str(getstartpoint))
        except:
            print("error 1. No start point")
        def countlifepersecond():
            global t

            getnewdata = tb.search(Query().uid == after.id)
            getnewstartpoint = getnewdata[0]['time']
            timetoaddit = getnewstartpoint
            timetoaddit += 1
            print(str(timetoaddit) + ' ' + str(after.name))
            final_time = timetoaddit
            tb.update({'time': final_time}, where('time') == getnewstartpoint )
            t = threading.Timer(1, countlifepersecond)
            t.start()
        countlifepersecond()

    elif str(after.voice_channel) == "None":
        t.cancel()
        print(after.name + " left " + str(before.voice_channel))
    else:
        return


@client.command(pass_context = True)
async def topv(ctx, *args):

    with open('db.json') as json_data:
        topvjson = json.load(json_data)
        stats = topvjson['stats']
        stats.sort(key = lambda entry: int(entry['time']), reverse=True)

    em = discord.Embed(title='Топ 10 поней в голосовом канале', description='Здесь показаны ТОП 10 поней которые провели в голосовом канале за сегодня.', colour=0x80a842)
    for entry in stats[:10]:
        # print("%s: %d" % (entry['name'], int(entry['time'])))
        playername = "%s" % (entry['name'])
        playertime = "%s" % (int(entry['time']))
        em.add_field(name=playername, value=playertime, inline=False)
    await client.send_message(ctx.message.channel, embed=em)


client.run('YOURTOKENHERE')
