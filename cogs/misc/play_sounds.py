import discord
from discord.ext import commands
from gtts import gTTS
from helpers import logHelper
import os
import random
import asyncio
import youtube_dl

youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = ""

    @classmethod
    async def from_url(cls, url: str, *, loop=None, stream=False):
        """
        extracts audio from specified url

        :param url: specified url
        :type url: str
        :param loop: AbstractEventLoop, defaults to None
        :type loop: Unknown, optional
        :param stream: Unknown, defaults to False
        :type stream: bool, optional
        :return: audio file
        :rtype: Any
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )
        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]
        filename = data["title"] if stream else ytdl.prepare_filename(data)
        return filename


def textVoice(myText: str):
    """
    convets text in tts.mp3 file

    :param myText: text to convet in speech
    :type myText: str
    """
    myobj = gTTS(text=myText, lang="en", slow=False)
    # Saving the converted audio in a mp3 file
    myobj.save("soundfiles/tts.mp3")


def randomSound(dir: str) -> str:
    """
    plays an random audio from specified directory

    :return: audio's location
    :rtype: str
    """
    listOfFiles = []
    for filename in os.listdir("./soundfiles/" + dir):
        listOfFiles.append(filename)
    chosenOne = random.choice(listOfFiles)
    return "soundfiles/" + dir + "/" + chosenOne


def playNext(ctx, path: str) -> None:
    """
    skips current playing song and moves to next

    :param path: location / url of next song
    :type path: str
    """
    guild = ctx.message.guild
    voice_client = guild.voice_client
    print(path)
    voice_client.play(
        discord.FFmpegPCMAudio(path),
        after=lambda x: playNext(ctx, randomSound("chord")),
    )
    voice_client.source = discord.PCMVolumeTransformer(voice_client.source, 1)


def musicMaker(ctx) -> None:
    """
    plays next chord

    """
    guild = ctx.message.guild
    voice_client = guild.voice_client
    path = randomSound("chord")
    print(path)
    voice_client.play(
        discord.FFmpegPCMAudio(path),
        after=lambda x: playNext(ctx, randomSound("chord")),
    )
    voice_client.source = discord.PCMVolumeTransformer(voice_client.source, 1)


async def joinMusicChannel(ctx) -> bool:
    """
    makes bot join voice channel

    :return: whether join successful or not
    :rtype: bool
    """
    try:
        channel = ctx.author.voice.channel
    except:
        await ctx.send(ctx.author.mention + " Please join the music voice channel.")
        return False

    vc = ctx.voice_client
    if vc == None:
        await channel.connect()
    return True


def endSong(guild, path: str) -> None:
    """
    removes song from the playlist

    :param guild: discord guild bot is in
    :type guild: int
    :param path: path/location to remove
    :type path: str
    """
    os.remove(path)


def over():
    pass


class PlaySounds(commands.Cog):
    """
    Bot Audio Module
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Definitely Doesn't Play Nyan Cat")
    async def nyan(self, ctx) -> None:
        """
        plays Nyan cat audio

        """
        try:
            data = await joinMusicChannel(ctx)
            if data == True:
                guild = ctx.message.guild
                voice_client = guild.voice_client
                path = "soundfiles/Nyan.mp3"
                voice_client.play(discord.FFmpegPCMAudio(path), after=lambda x: over())
                voice_client.source = discord.PCMVolumeTransformer(
                    voice_client.source, 1
                )
        except Exception as e:
            logHelper.logger.warning(e)

    @commands.command(help="Text-To-Speech Command")
    async def tts(self, ctx, *args: list[str]) -> None:
        """
        converts text to speech
        """
        try:
            joinedSentence = " ".join(map(str, args))
            textVoice(joinedSentence)
            data = await joinMusicChannel(ctx)
            if data == True:
                guild = ctx.message.guild
                voice_client = guild.voice_client
                path = "soundfiles/tts.mp3"
                voice_client.play(discord.FFmpegPCMAudio(path), after=lambda x: over())
                voice_client.source = discord.PCMVolumeTransformer(
                    voice_client.source, 1
                )
        except Exception as e:
            logHelper.logger.warning(e)

    @commands.command(
        help="Plays random sound file from specified directory,\ntry *pog starwars or *pog animesounds"
    )
    async def pog(self, ctx, dir: str) -> None:
        """
        play a random sound from specified directory

        :param dir: specified directory
        :type dir: str
        """
        try:
            data = await joinMusicChannel(ctx)
            if data == True:
                guild = ctx.message.guild
                voice_client = guild.voice_client
                path = randomSound(dir)
                print(path)
                voice_client.play(discord.FFmpegPCMAudio(path), after=lambda x: over())
                voice_client.source = discord.PCMVolumeTransformer(
                    voice_client.source, 1
                )
        except Exception as e:
            logHelper.logger.warning(e)

    @commands.command(help="creates song from sound clips")
    async def song(self, ctx) -> None:
        """
        creates song form sound clips

        """
        try:
            data = await joinMusicChannel(ctx)
            if data == True:
                while True:
                    musicMaker(ctx)
        except Exception as e:
            logHelper.logger.warning(e)

    @commands.command(help="tts from song lyrics or txt files")
    async def rap(self, ctx, dir: str) -> None:
        """
        play song from text files in a specified directory or song lyrics


        :param dir: specified directory
        :type dir: str
        """
        try:
            line = random.choice(open("textfiles/" + dir + ".txt").readlines())
            textVoice(line)
            data = await joinMusicChannel(ctx)
            if data == True:
                guild = ctx.message.guild
                voice_client = guild.voice_client
                path = "soundfiles/tts.mp3"
                print(path)
                voice_client.play(discord.FFmpegPCMAudio(path), after=lambda x: over())
                voice_client.source = discord.PCMVolumeTransformer(
                    voice_client.source, 1
                )
        except Exception as e:
            logHelper.logger.warning(e)

    @commands.command(help="Plays youtube sound from specified link")
    async def play(self, ctx, link: str) -> None:
        """
        play audion from specified youtube video

        :param link: youtube video link
        :type link: str
        """
        try:
            data = await joinMusicChannel(ctx)
            if data == True:
                guild = ctx.message.guild
                voice_client = guild.voice_client
                path = await YTDLSource.from_url(link, loop=self.bot.loop)
                print(path)
                voice_client.play(
                    discord.FFmpegPCMAudio(path), after=lambda x: endSong(guild, path)
                )
                voice_client.source = discord.PCMVolumeTransformer(
                    voice_client.source, 1
                )
        except Exception as e:
            logHelper.logger.warning(e)

    @commands.command(name="pause", help="This command pauses the song")
    async def pause(self, ctx) -> None:
        """
        pauses current song/audio

        """
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name="resume", help="Resumes the song")
    async def resume(self, ctx) -> None:
        """
        resumes previously paused song/audio

        """
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send(
                "The bot was not playing anything before this. Use play_song command"
            )

    @commands.command(name="stop", help="Stops the song")
    async def stop(self, ctx) -> None:
        """
        stops audio/song

        """
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")


def setup(bot):
    bot.add_cog(PlaySounds(bot))
