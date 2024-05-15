import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
from specials import specials


def run_bot():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    client = discord.Client(intents=intents)

    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'options': '-vn'}

    all_special_options = ""
    for item in specials:
        all_special_options += f'\n Usa: **{item["name"]}** para {item["desc"]}'

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')

    @client.event
    async def on_message(message):
        if message.content.startswith("/play"):
            try:
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
            except Exception as e:
                print(e)

            try:
                message_content = message.content.split()[1:]
                url = ""

                # Change url if is a single word in special cases
                if "www.youtube.com" not in message_content[0]:
                    print("not a link")
                    try:
                        video = ytdl.extract_info(f'ytsearch:{" ".join(message_content)}', download=False)['entries'][0]
                        url = video.get("url")

                    except Exception as e:
                        print(e)
                else:
                    url = message_content[0]

                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                song = data['url']
                player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

                voice_clients[message.guild.id].play(player)
            except Exception as e:
                print(e)

        if message.content.startswith("/special"):
            try:
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
            except Exception as e:
                print(e)

            message_content = message.content.split()[1:]
            url = ""

            # Change url if is a single word in special cases
            for special in specials:
                if special["name"] == message_content[0] and len(message_content) == 1:
                    url = special["link"]

            if url != "":
                try:
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                    song = data['url']
                    player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
                    voice_clients[message.guild.id].play(player)

                except Exception as e:
                    print(e)
            else:
                await message.channel.send("No está en las escrituras")
                await message.channel.send("Estas son las escrituras: " + all_special_options)

        if message.content.startswith("/help"):
            await message.channel.send("Estas son las escrituras:\n" + all_special_options)
            await message.channel.send(
                f"Estos son los comandos:\n **play** - **pause** - **stop** - **resume** - **help**")

        if message.content.startswith("/pause"):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)

        if message.content.startswith("/resume"):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)

        if message.content.startswith("/stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
            except Exception as e:
                print(e)

    client.run(TOKEN)


