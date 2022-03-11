import discord
from discord.ext import commands

import os, re, requests, random

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from dotenv import load_dotenv

from mplsoccer import PyPizza, FontManager, add_image
from PIL import Image, ImageDraw
from urllib.request import urlopen
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

load_dotenv()

client = commands.Bot(command_prefix="!")
token = os.getenv("DISCORD_TOKEN")

options = Options()
options.add_argument("user-data-dir=C:\PythonProjects\Selenium")
options.add_argument("--log-level-3")
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors-spki-list")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
s = Service("C:\PythonProjects\chromedriver.exe")

font_normal = FontManager(
    (
        "https://github.com/google/fonts/blob/main/apache/roboto/static/"
        "Roboto-Regular.ttf?raw=true"
    )
)

font_bold = FontManager(
    (
        "https://github.com/google/fonts/blob/main/apache/roboto/static/"
        "Roboto-Medium.ttf?raw=true"
    )
)


@client.event
async def on_ready():
    print("Inloggad som {0.user}".format(client))


@client.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f"{username}: {user_message} ({channel})")

    if message.author == client.user:
        return

    if message.channel.name == "general":
        if user_message.lower() == "hej leifi":
            await message.channel.send(f"seeenare {username}!")
            return
        elif user_message.lower() == "läget leifi?":
            await message.channel.send(f"jåå de bra")
            return
        elif user_message.lower() == "vad kan du leifi?":
            await message.channel.send(
                f'Jåå do kan pråva å fråg vem jag är å du kan häls på mig\n"Vem är du Leifi?"\n"Hej/Tjenare/Tjena/Tjo Leifi"'
            )
            return
        elif user_message.lower() == "vem är du leifi?":
            await message.channel.send(
                f"Tet er jak såm er herr Plomeros, fråka sej vat som helst vettu, jak alltit svara. Fråka sej tumma krejer, jak spruta met hakelsprackaren i ansicktet"
            )
            return
        elif user_message.lower() == "är det skii eller skoo?":
            skii_skoo = ["skii", "skoo"]
            await message.channel.send(f"ja tycker de e {random.choice(skii_skoo)}")
            return
        elif user_message.lower() == "skii":
            skii2 = ["ajjemån de e skii", "redi skii", "haaaa"]
            await message.channel.send(f"{random.choice(skii2)}")
            return
        elif user_message.lower() == "skoo":
            skoo2 = ["haaa skooooo", "redi skoo", "haaaa"]
            await message.channel.send(f"{random.choice(skoo2)}")
            return
    await client.process_commands(
        message
    )  # Has to end with this if invoking on_message


@client.event
async def get_porr(cat=None):
    if cat is not None:
        url = "http://porngif.cz/index.php?k=" + cat
    else:
        url = "http://porngif.cz/"
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        gif = soup.find("img", {"class": "big"})
        link = "http://porngif.cz/" + gif["src"]
        with open("/data/porrgif.gif", "wb") as f:
            im = requests.get(link)
            f.write(im.content)
    except KeyError:
        pass


@client.event
async def get_loadout(weapon_name):
    # Saves screenshot of the weapons current loadout meta (CoD WZ)
    weapon_name.replace(" ", "_")
    url = f"https://wzstats.gg/loadout/{weapon_name}"
    driver = webdriver.Chrome(service=s, options=options)
    driver.get(url)

    loadout = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//div[@class="weapon-build-container"]')
        )
    )
    loadout.screenshot("data/loadout.png")


@client.event
async def get_player(name):
    # Takes an input of a football players name
    # Outputs a pie chart with categorized stats
    driver = webdriver.Chrome(service=s, options=options)
    driver.get("https://fbref.com/en/")

    # Accept cookies
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@class=" css-47sehv"]'))
    ).click()

    try:
        search = driver.find_element(By.NAME, "search")
        search.send_keys(name)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[@class='search-results-item']")
            )
        ).click()

        url = driver.current_url

        # Parsing name so input can be for e.g. Pogba and the output
        # text on the picture will be the full name Paul Pogba
        real_name = driver.find_element(By.XPATH, "//h1[@itemprop='name']")

        # Player headshot img
        try:
            image_url = driver.find_element(
                By.XPATH, "//img[@alt='" + real_name.text + " headshot']"
            ).get_attribute("src")
        except Exception:
            print(Exception)

        # Player birthplace flag
        flag_url = driver.find_element(By.XPATH, "//span[@class='f-i']").get_attribute(
            "style"
        )
    finally:
        # driver.close()
        pass

    try:
        df = pd.read_html(url)
        df_parsed = df[0]
        df_parsed.drop(
            [
                df_parsed.index[3],
                df_parsed.index[4],
                df_parsed.index[5],
                df_parsed.index[7],
                df_parsed.index[8],
                df_parsed.index[9],
                df_parsed.index[13],
                df_parsed.index[15],
            ],
            inplace=True,
        )
        df_parsed.reset_index(inplace=True)
        df_parsed.drop("index", axis="columns", inplace=True)
    except KeyError:
        print(KeyError)
    # Cropping circle picture
    # Exception if headshot is missing from player
    try:
        img = Image.open(urlopen(image_url)).convert("RGB")
        npImage = np.array(img)
        h, w = img.size
        alpha = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0, 0, h, w], 0, 360, fill=255)
        npAlpha = np.array(alpha)
        npImage = np.dstack((npImage, npAlpha))
        Image.fromarray(npImage).save("data/headshot.png")
        img_localfile = Image.open("data/headshot.png")
    except Exception:
        pass

    # Processing flag image url
    pattern = pattern = '"(.*?)"'
    flag_url_parsed = re.search(pattern, flag_url).group(1)

    # Saving locally and converting SVG to PNG
    with open("data/flag.svg", "wb") as f:
        im = requests.get(flag_url_parsed, stream=True).content
        f.write(im)
    flag_img_svg = svg2rlg("data/flag.svg")
    renderPM.drawToFile(flag_img_svg, "data/flag.png", fmt="PNG")

    params = df_parsed["Statistic"]
    values = df_parsed["Percentile"]
    slice_colors = (
        ["#1A78CF"] * 4 + ["#FF9300"] * 4 + ["#D70232"] * 6
    )  # Attacking, Possession and Defending slice colors
    text_colors = ["#000000"] * 8 + [
        "#F2F2F2"
    ] * 6  # Attacking/Possession and Defending text colors

    baker = PyPizza(
        params=params,  # list of parameters
        background_color="#222222",  # background color
        straight_line_color="#000000",  # color for straight lines
        straight_line_lw=1,  # linewidth for straight lines
        last_circle_color="#000000",  # color for last line
        last_circle_lw=1,  # linewidth of last circle
        other_circle_lw=0,  # linewidth for other circles
        inner_circle_size=20,  # size of inner circle
    )

    fig, ax = baker.make_pizza(
        values,  # list of values
        figsize=(8, 8),  # adjust figsize according to your need
        color_blank_space="same",  # use the same color to fill blank space
        slice_colors=slice_colors,  # color for individual slices
        value_colors=text_colors,  # color for the value-text
        value_bck_colors=slice_colors,  # color for the blank spaces
        blank_alpha=0.4,  # alpha for blank-space colors
        param_location=105,  # where the parameters will be added
        kwargs_slices=dict(
            facecolor="#33ceff", edgecolor="#000000", zorder=2, linewidth=1
        ),  # values to be used when plotting slices
        kwargs_params=dict(
            color="#F2F2F2", fontsize=10, fontproperties=font_normal.prop, va="center"
        ),  # values to be used when adding parameter
        kwargs_values=dict(
            color="#000000",
            fontsize=11,
            fontproperties=font_normal.prop,
            zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="#33ceff", boxstyle="round,pad=0.2", lw=1
            ),
        ),  # values to be used when adding parameter-values
    )

    # title name of player
    fig.text(
        0.515,
        0.97,
        str(real_name.text),
        size=18,
        ha="center",
        fontproperties=font_bold.prop,
        color="#F2F2F2",
    )

    # description title
    fig.text(
        0.515,
        0.932,
        "per 90 Percentile Rank vs Positional Peers in Top 5 Leagues | 365 Days",
        size=15,
        ha="center",
        fontproperties=font_bold.prop,
        color="#F2F2F2",
    )

    # text rectangles
    fig.text(
        0.30,
        0.03,
        "Attacking        Possession       Defending",
        size=14,
        fontproperties=font_bold.prop,
        color="#F2F2F2",
    )

    # rectangles
    fig.patches.extend(
        [
            plt.Rectangle(
                (0.27, 0.03),
                0.025,
                0.021,
                fill=True,
                color="#1a78cf",
                transform=fig.transFigure,
                figure=fig,
            ),
            plt.Rectangle(
                (0.422, 0.03),
                0.025,
                0.021,
                fill=True,
                color="#ff9300",
                transform=fig.transFigure,
                figure=fig,
            ),
            plt.Rectangle(
                (0.592, 0.03),
                0.025,
                0.021,
                fill=True,
                color="#d70232",
                transform=fig.transFigure,
                figure=fig,
            ),
        ]
    )

    # image player headshot
    try:
        ax_image = add_image(
            img_localfile, fig, left=0.4478, bottom=0.4315, width=0.13, height=0.127
        )
    except Exception:
        pass

    # Placing the flag to the left of the player name
    # location based on len of name
    flag_img = Image.open("data/flag.png")
    name_length = len(str(real_name.text))

    def flagimager(leftlength):
        ax_image = add_image(
            flag_img,
            fig,
            left=leftlength,
            bottom=0.97,
            width=0.032,
            height=0.024,
            interpolation="hanning",
        )

    # TODO fix the values
    if name_length > 18:
        flagimager(0.40)
    elif name_length >= 16:
        flagimager(0.38)
    elif name_length >= 14:
        flagimager(0.36)
    elif name_length >= 12:
        flagimager(0.35)
    else:
        flagimager(0.34)

    plt.savefig("data/player.png")


@client.command()
async def porr(ctx, *, cat=None):
    await get_porr(cat)
    embed = discord.Embed()
    file = discord.File("data/porrgif.gif")
    embed.set_image(url="attachment://data/porrgif.gif")
    await ctx.channel.send(file=file, embed=embed)


@client.command()
async def minmor(ctx):
    username = str(ctx.author).split("#")[0]
    yomama = requests.get("https://api.yomomma.info/")
    jsonloading = yomama.json()
    final = jsonloading["joke"]
    await ctx.channel.send(f"{username}, {str(final)}.")


@client.command()
async def dinmor(ctx, *, arg):
    yomama = requests.get("https://api.yomomma.info/")
    jsonloading = yomama.json()
    final = jsonloading["joke"]
    await ctx.channel.send(f"{arg}, {str(final)}.")


@client.command()
async def player(ctx, *, name):
    await get_player(name)
    embed = discord.Embed()
    file = discord.File("data/player.png")
    embed.set_image(url="attachment://data/player.png")
    await ctx.channel.send(file=file, embed=embed)


@client.command()
async def loadout(ctx, *, weapon_name):
    await get_loadout(weapon_name)
    embed = discord.Embed()
    file = discord.File("data/loadout.png")
    embed.set_image(url="attachment://data/loadout.png")
    await ctx.channel.send(file=file, embed=embed)


client.run(token)
