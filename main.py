# made by ID_Dester with love
import discord
import discord.ext
from discord.ext import commands
import json
from art import *
import yt_dlp as youtube_dl
import asyncio
import ffmpeg



intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)



# Настройки для YouTube-DL и FFMPEG
voice_clients = {}

YDL_OPTIONS = {
    'format': 'worstaudio/best',
    'noplaylist': 'False',
    'simulate': 'True',
    'key': 'FFmpegExtractAudio'
}
FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 - reconnect_streamed 1 - reconnect_delay_max 5',
    'options': '-vn'
}

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_opts)
ffmpeg_options = {'options': "-vn"}



@client.event
async def on_ready():
  await tree.sync()
  gotov = text2art("ready")
  print (gotov)

# тест команда
@tree.command(name="ping", description="pong")
async def slash_command(interaction: discord.Interaction):
  await interaction.response.send_message("pong")



# вывод рейтинга по количеству сообщений
@tree.command(name="top", description="Responds with top users")
async def top_command(interaction: discord.Interaction):
    await interaction.response.send_message("just a sec") # Временное сообщение
    guild = str(interaction.guild_id)
    with open('users.json', "r") as f:
        andor = json.load(f)  
    sorted_people = sorted(andor[guild][0].items(),
                           key=lambda item: item[1],
                           reverse=True)    
    ii = 0
    biba = []
    for i in sorted_people:
        nick = await client.fetch_user(sorted_people[ii][0])
        biba.append(f"{nick}" + " Количество сообщений: " +
                    f"{sorted_people[ii][1]}")
        ii += 1    
    await interaction.followup.send(content='\n'.join(biba))
    await interaction.delete_original_response()



# Счет сообщений на сервере
@client.event
async def on_message(message):
    if message.author.bot:  # Пропускаем сообщения от ботов.
        return
    guild = str(message.guild.id)
    idd = str(message.author.id)
    with open('users.json', "r") as f:
        andor = json.load(f)
    if guild not in andor:
        andor[guild] = [{}]
    if idd in andor[guild][0]:
        andor[guild][0][idd] += 1
    else:
        andor[guild][0][idd] = 1
    with open('users.json', 'w') as f:
        json.dump(andor, f, ensure_ascii=False, indent=2)



@tree.command(name="play", description="Play audio from a URL")
async def playvid(interaction: discord.Interaction, url: str):
    try:
        voice_channel = interaction.user.voice.channel
        voice_client = await voice_channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except Exception as e:
        await interaction.response.send_message("Error connecting to voice channel.")
        print(f"Error connecting to voice channel: {e}")
        return

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        song = data['url']

        def after_playing(error):
            if error:
                print(f"Error occurred after playing: {error}")
            coro = voice_client.disconnect()
            fut = asyncio.run_coroutine_threadsafe(coro, loop)
            fut.result()

        player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
        voice_clients[voice_client.guild.id].play(player, after=after_playing)

        # Получаем URL превью (миниатюры)
        thumbnail_url = data.get('thumbnail')
        title = data.get('title', 'No title')
        uploader = data.get('uploader', 'Unknown uploader')
        duration = str(data.get('duration') // 60) + ":" + str(data.get('duration') % 60).zfill(2)

        # Создаем embed
        embed = discord.Embed(title=title, url=url, description=f"Requested by {interaction.user.mention}")
        embed.set_thumbnail(url=thumbnail_url)
        embed.add_field(name="Uploader", value=uploader, inline=True)
        embed.add_field(name="Duration", value=duration, inline=True)

        # Отправляем embed в ответ
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("Error playing audio.")
        print(f"Error playing audio: {e}")



client.run("MTEyMjkzNjU1NjUyNTcxOTYzMw.GF8pgh.Se7s1Mnw5XsgtGLC_CJus1oVxOySaqEtdBPgII")
