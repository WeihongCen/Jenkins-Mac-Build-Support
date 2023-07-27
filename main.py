import os
from dotenv import load_dotenv
import discord
from discord import Embed
from discord import app_commands
from discord.ext import commands
import datetime
import requests

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_TOKEN = os.getenv('API_TOKEN')
BUILD_TOKEN = os.getenv('BUILD_TOKEN')

JENKINS_PATH = "saleblazerspc:8080"
DEFAULT_BUILD_PATH = f"{JENKINS_PATH}/job/Saleblazers%20Default%20Build"

BLURPLE = 0x5865F2
GREEN = 0x43b581
RED = 0xf04747
GRAY = 0x4f545c

DISCORD_EMBED_LIMIT = 5800 # left 200 for fields that are not changelogs
DISCORD_EMBED_VALUE_LIMIT = 1024

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

# class AbortButton(discord.ui.View):
#     def __init__(self):
#         super().__init__(timeout=None)
#     @discord.ui.button(label="ABORT", style=discord.ButtonStyle.red)
#     async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         button.disabled = True
#         await interaction.response.edit_message(view=self)
#         try:
#             response = requests.post(f"http://jenkins_as:{API_TOKEN}@saleblazerspc:8080/job/Saleblazers%20Default%20Build/lastBuild/stop")
#             if response.status_code == 200:
#                 await interaction.followup.send("Build aborted successfully.")
#             else:
#                 await interaction.followup.send(f"Failed to abort the build. Error: {response.text}")
#         except Exception as e:
#             await interaction.followup.send(f"An error occurred: {str(e)}")


def get_datetime(sec):
    dt = datetime.datetime.fromtimestamp(sec / 1e3)
    dt = dt.replace(microsecond=0)
    dt = datetime.datetime.strptime(str(dt), '%Y-%m-%d %H:%M:%S')
    dt = dt.strftime('%Y-%m-%d %I:%M %p')
    return dt


def get_time_hh_mm_ss(sec):
    td_str = str(datetime.timedelta(seconds=sec/1e3))
    x = td_str.split(':')
    return (x[0] + ' Hours ' + x[1] + ' Minutes')


@bot.event
async def on_ready():
    print(f'{bot.user} connected to Discord')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands)")
    except Exception as e:
        print(e)


@bot.tree.command(name="windows_status", description="Get the build status")
@app_commands.describe(build="Build number (-1 for latest build)")
async def status(interaction, build: int):

    build_number = str(build)
    if (build == -1):
        build_number = "lastBuild"

    try:
        response = requests.get(f"http://jenkins_as:{API_TOKEN}@{DEFAULT_BUILD_PATH}/{build_number}/api/json")
        if response.status_code == 200:
            result = response.json()
            name = result["fullDisplayName"]
            status = result["result"]
            duration = result["duration"]
            building = result["building"]
            timestamp = result["timestamp"]
            change_log = result["changeSet"]["items"]

            if (building):
                status = "BUILDING"
            match status:
                case "SUCCESS":
                    color=GREEN
                case "FAILURE":
                    color=RED
                case "ABORTED":
                    color=GRAY
                case _:
                    color=BLURPLE

            change_description_list = [] # Used to separate descriptions to different embed fields
            change_description = ""
            for i in range(len(change_log)):
                change = change_log[i]
                change_number = change["changeNumber"]
                change_msg = change["msg"]
                change_author = change["author"]["fullName"]
                change_item_description = f"- `{change_number}` {change_msg} -_{change_author}_"
                change_item_description = change_item_description.replace("\n", " ") + "\n"

                if (len(change_description + change_item_description) > DISCORD_EMBED_VALUE_LIMIT):
                    change_description_list.append(change_description)
                    change_description = change_item_description
                else:
                    change_description += change_item_description

                if (i == len(change_log) - 1):
                    change_description_list.append(change_description)


            embed = Embed(title=name, color=color)
            embed.add_field(name="Status", value=status, inline=False)
            embed.add_field(name="Timestamp", value=get_datetime(timestamp), inline=True)
            if (not building):
                embed.add_field(name="Duration", value=get_time_hh_mm_ss(duration), inline=True)

            for i in range(len(change_description_list)):
                if (len("".join(change_description_list[:i])) > DISCORD_EMBED_LIMIT):
                    embed.add_field(name="", value="(Changelog too long, omitted)", inline=False)
                    break
                embed.add_field(name="", value=change_description_list[i], inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            embed = Embed(description="Failed to get status.", color=RED)
            await interaction.response.send_message(embed=embed)
            print(f"Error: {response.text}")
    except Exception as e:
        embed = Embed(description="An error occurred.", color=RED)
        await interaction.response.send_message(embed=embed)
        print(e)


@bot.tree.command(name="windows_start_build", description="Build the latest Saleblazers Default Build")
async def start_build(interaction):
    try:
        response = requests.post(f"http://jenkins_as:{API_TOKEN}@{DEFAULT_BUILD_PATH}/build?token={BUILD_TOKEN}")
        if response.status_code == 201:
            embed = Embed(description="Build request sent.", color=GREEN)
            await interaction.response.send_message(embed=embed)
        else:
            embed = Embed(description="Failed to request the build.", color=RED)
            await interaction.response.send_message(embed=embed)
            print(f"Error: {response.text}")
    except Exception as e:
        embed = Embed(description="An error occurred.", color=RED)
        await interaction.response.send_message(embed=embed)
        print(e)


@bot.tree.command(name="windows_abort_build", description="Abort the latest Saleblazers Default Build")
async def abort_build(interaction):
    try:
        response = requests.post(f"http://jenkins_as:{API_TOKEN}@{DEFAULT_BUILD_PATH}/lastBuild/stop")
        if response.status_code == 200:
            embed = Embed(description="Abort request sent.", color=GREEN)
            await interaction.response.send_message(embed=embed)
        else:
            embed = Embed(description="Failed to request abort.", color=RED)
            await interaction.response.send_message(embed=embed)
            print(f"Error: {response.text}")
    except Exception as e:
        embed = Embed(description="An error occurred.", color=RED)
        await interaction.response.send_message(embed=embed)
        print(e)


bot.run(DISCORD_TOKEN)