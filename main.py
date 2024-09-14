import discord
import asyncio
from pydub import AudioSegment
from discord.ext import commands, tasks
import speech_recognition as sr
import time

connections = {}
intents = discord.Intents.default()
intents.message_content = True
r = sr.Recognizer()
bot = commands.Bot(command_prefix='!', intents=intents)
wordlist = ["cock", "balls", "shaft", "dick", "penis", "pussy", "cunt", "ball"]

@bot.event
async def on_ready():
    print("logged in")

@bot.event
async def on_message(ctx):
    text = ctx.content
    await bot.process_commands(ctx)
    client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ctx.author == bot.user:
        return
    for i in wordlist:
        if text.find(i) != -1:
            #If bot is already in call for other purposes, just play the sound
            if client:
                vc = connections[ctx.guild.id]
                await ctx.channel.send("?")
                vc.play(discord.FFmpegPCMAudio('Huh.wav'))
            # If bot is not in call, joins the users channel, plays the sound, and leaves when sound is done
            else:
                vc = await ctx.author.voice.channel.connect()
                await ctx.channel.send("?")
                vc.play(discord.FFmpegPCMAudio('Huh.wav'))
                time.sleep(1)
                await vc.disconnect()
            return

@bot.command()
async def listen(ctx):
    #starts the loop of recording
    recorder.start(ctx)

@tasks.loop(seconds=6)
async def recorder(ctx):
    #Loop to make the bot actively record and transcribe what the users are saying
    client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    #if bot is already in call, does not connect, but repeats rest of code
    if client:
        vc = connections[ctx.guild.id]
        connections.update({ctx.guild.id: vc})
        vc.start_recording(discord.sinks.MP3Sink(), once_done, ctx.channel)
        await asyncio.sleep(4)
        vc.stop_recording()
        return
    vc = await ctx.author.voice.channel.connect()
    connections.update({ctx.guild.id: vc})
    vc.start_recording(discord.sinks.MP3Sink(), once_done, ctx.channel)
    await asyncio.sleep(4)
    vc.stop_recording()

async def once_done(sink: discord.sinks, ctx):
    #Writes MP3 file of the audio recorded
    for user_id, audio in sink.audio_data.items():
        with open("SpeechtoDecipher.mp3", "wb") as f:
            f.write(audio.file.getbuffer())
    #Turns audio from MP3 to WAV so SpeechRecognizer can translate it
    newsound = AudioSegment.from_mp3("C:\\Users\\aidan\\PycharmProjects\\MrBeastBot\\SpeechtoDecipher.mp3")
    newsound.export("C:\\Users\\aidan\\PycharmProjects\\MrBeastBot\\SpeechtoDecipher.wav", format="wav")
    exportedaudio = "SpeechtoDecipher.wav"
    #Use SpeechRecognizer to transcribe the audio, then looks for the words to enable playsound
    try:
        with sr.AudioFile(exportedaudio) as source:
            recording = r.record(source)
            transcript = r.recognize_google(recording)
        print(transcript)
        for i in wordlist:
            if transcript.find(i) != -1:
                playsound(ctx)
    except sr.UnknownValueError:
        print("Audio Could Not Be Picked Up")
    except sr.RequestError:
        print("idk")

def playsound(ctx):
    #This was made into a separate def as putting this into the callback causes an error
    client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if client:
        vc = connections[ctx.guild.id]
        vc.play(discord.FFmpegPCMAudio('Huh.wav'))
        return

@bot.command()
async def stop(ctx):
    recorder.stop()
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        vc.disconnect()
        del connections[ctx.guild.id]  # Remove the guild from the cache.
        del ctx # And delete.
    else:
        await ctx.send("I am currently not recording here.")  # Respond with this if we aren't recording.


bot.run('MTE2NzkzMDg4NjA3MTc3OTMyOQ.GJsyMm.pwKnvGuznBnYWsetTZD1ZYDQM6t2LDahsgQopw')