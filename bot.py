import sys
import subprocess
import os
import json

# Auto-install requirements
def check_and_install():
    try:
        import discord
        import requests
    except ImportError:
        print("Required packages missing. Installing discord.py and requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py", "requests"])
        print("Packages installed! Restarting script...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

check_and_install()

import discord
from discord.ext import commands
from discord import app_commands
import requests
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
TOKEN = "MTU1MjAwMjMzMjAwOTQzOTMyMg.G6af3Z.dGJ7M6Ujun8Sjy8VjUSC-NlYS9o2THCZIjetnI"
API_BASE = "https://enzo-info-api.vercel.app"
CONFIG_FILE = "guild_configs.json"
# ==========================================

REGION_MAP = {
    "IND": "IND - India",
    "BD":  "BD  - Bangladesh",
    "NP":  "NP  - Nepal",
    "BR":  "BR  - Brazil",
    "US":  "US  - United States",
    "SAC": "SAC - South America",
    "NA":  "NA  - North America",
    "NX":  "NX",
    "AG":  "AG",
    "SG":  "SG  - Singapore",
    "RU":  "RU  - Russia",
    "ID":  "ID  - Indonesia",
    "TW":  "TW  - Taiwan",
    "VN":  "VN  - Vietnam",
    "TH":  "TH  - Thailand",
    "ME":  "ME  - Middle East",
    "PK":  "PK  - Pakistan",
    "CIS": "CIS - Russia/CIS"
}

# BD and NP share the IND server pool per the API README
REGION_CHOICES = [
    app_commands.Choice(name="India (IND)",          value="IND"),
    app_commands.Choice(name="Bangladesh (BD = IND)", value="IND"),
    app_commands.Choice(name="Nepal (NP = IND)",      value="IND"),
    app_commands.Choice(name="Pakistan (PK)",         value="PK"),
    app_commands.Choice(name="Singapore (SG)",        value="SG"),
    app_commands.Choice(name="Indonesia (ID)",        value="ID"),
    app_commands.Choice(name="Thailand (TH)",         value="TH"),
    app_commands.Choice(name="Vietnam (VN)",          value="VN"),
    app_commands.Choice(name="Taiwan (TW)",           value="TW"),
    app_commands.Choice(name="Middle East (ME)",      value="ME"),
    app_commands.Choice(name="Brazil (BR)",           value="BR"),
    app_commands.Choice(name="South America (SAC)",   value="SAC"),
    app_commands.Choice(name="North America (NA)",    value="NA"),
    app_commands.Choice(name="Russia / CIS (CIS)",    value="CIS"),
    app_commands.Choice(name="AG",                    value="AG"),
    app_commands.Choice(name="NX",                    value="NX"),
]

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def format_epoch(epoch_str):
    if not epoch_str or str(epoch_str) == "0":
        return "N/A"
    try:
        return datetime.datetime.fromtimestamp(int(epoch_str)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(epoch_str)

def format_block(title, fields):
    text = f"**{title}**\n"
    items = list(fields.items())
    for i, (k, v) in enumerate(items):
        conn = "**`L`** " if i == len(items) - 1 else "**`|`** "
        text += f"{conn}**{k}:** {v}\n"
    return text + "\n"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Syncing slash commands...")
    await bot.tree.sync()
    print("Ready! All commands are slash commands.")
    print("------")

# ==========================================
# CHANNEL LOCK
# ==========================================

def check_channel(command_type):
    async def predicate(interaction: discord.Interaction):
        if not interaction.guild:
            return True
        config = load_config()
        guild_id = str(interaction.guild_id)
        if guild_id not in config:
            return True
        allowed_id = config[guild_id].get(f"{command_type}_channel")
        if allowed_id and interaction.channel_id != allowed_id:
            await interaction.response.send_message(
                f"❌ This command can only be used in <#{allowed_id}>", ephemeral=True
            )
            return False
        return True
    return app_commands.check(predicate)

# ==========================================
# ADMIN COMMANDS
# ==========================================

@bot.tree.command(name="setinfochannel", description="Set the dedicated channel for /info commands")
@app_commands.describe(channel="Target text channel")
@app_commands.checks.has_permissions(administrator=True)
async def setinfochannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    config = load_config()
    guild_id = str(interaction.guild.id)
    if guild_id not in config:
        config[guild_id] = {}
    config[guild_id]["info_channel"] = channel.id
    save_config(config)

    embed = discord.Embed(
        title="Info Channel Set",
        description=(
            "This channel is now dedicated to `/info` commands.\n"
            "The bot will only respond here.\n\n"
            "**Usage:** `/info uid: <UID> region: <Region>`"
        ),
        color=0x00b300
    )
    await channel.send(embed=embed)
    await interaction.response.send_message(
        f"Info channel set to {channel.mention}", ephemeral=True
    )

@bot.tree.command(name="setstatschannel", description="Set the dedicated channel for /stats commands")
@app_commands.describe(channel="Target text channel")
@app_commands.checks.has_permissions(administrator=True)
async def setstatschannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    config = load_config()
    guild_id = str(interaction.guild.id)
    if guild_id not in config:
        config[guild_id] = {}
    config[guild_id]["stats_channel"] = channel.id
    save_config(config)

    embed = discord.Embed(
        title="Stats Channel Set",
        description=(
            "This channel is now dedicated to `/stats` commands.\n"
            "The bot will only respond here.\n\n"
            "**Usage:** `/stats uid: <UID> region: <Region> gamemode: <Mode> matchmode: <Mode>`"
        ),
        color=0x00b300
    )
    await channel.send(embed=embed)
    await interaction.response.send_message(
        f"Stats channel set to {channel.mention}", ephemeral=True
    )

# ==========================================
# /info — region REQUIRED
# ==========================================

@bot.tree.command(name="info", description="Get account, pet, and guild info for a Free Fire player")
@app_commands.describe(
    uid="Player Free Fire UID",
    region="Player server region — MUST match their actual region to get correct data"
)
@app_commands.choices(region=REGION_CHOICES)
@check_channel("info")
async def slash_info(interaction: discord.Interaction, uid: str, region: app_commands.Choice[str]):
    await interaction.response.defer()
    try:
        server = region.value

        info_res = requests.get(f"{API_BASE}/info?uid={uid}&server={server}").json()
        if info_res.get("status") == "error":
            await interaction.followup.send(
                f"**Error:** {info_res.get('message', 'Failed to fetch data')}\n"
                "> Double-check the UID and make sure you selected the correct region."
            )
            return

        # Optional clan fetch for live member count
        clan_data = None
        guild_info = info_res.get("GuildInfo", {})
        if guild_info.get("GuildID") and str(guild_info.get("GuildID")) != "0":
            try:
                clan_res = requests.get(f"{API_BASE}/clan?clan_id={guild_info['GuildID']}&server={server}").json()
                if clan_res.get("status") == "success":
                    clan_data = clan_res.get("clan")
            except:
                pass

        acc    = info_res.get("AccountInfo", {})
        prof   = info_res.get("AccountProfileInfo", {})
        credit = info_res.get("creditScoreInfo", {})
        social = info_res.get("socialinfo", {})
        pet    = info_res.get("petInfo", {})

        raw_region = acc.get("AccountRegion", server)
        region_display = REGION_MAP.get(raw_region, raw_region)

        basic_fields = {
            "Name":        acc.get("AccountName", "N/A"),
            "UID":         uid,
            "Level":       f"{acc.get('AccountLevel', 0)} (Exp: {acc.get('AccountEXP', 0)})",
            "Region":      region_display,
            "Likes":       acc.get("AccountLikes", 0),
            "Honor Score": credit.get("creditscore", "N/A"),
            "Signature":   social.get("signature", "N/A"),
        }
        activity_fields = {
            "Most Recent OB":    acc.get("ReleaseVersion", "N/A"),
            "Current BP Badges": acc.get("AccountBPBadges", 0),
            "BR Rank":           acc.get("BrRankPoint", 0),
            "CS Rank":           acc.get("CsRankPoint", 0),
            "Created At":        format_epoch(acc.get("AccountCreateTime")),
            "Last Login":        format_epoch(acc.get("AccountLastLogin")),
        }
        overview_fields = {
            "Avatar ID":       prof.get("AvatarId", acc.get("AccountAvatarId", "N/A")),
            "Banner ID":       acc.get("AccountBannerId", "N/A"),
            "Equipped Skills": str(prof.get("EquippedSkills", [])),
        }
        pet_fields = {
            "Equipped?": "Yes" if pet.get("isselected") else "No",
            "Pet ID":    pet.get("id", "N/A"),
            "Pet Exp":   pet.get("exp", 0),
            "Pet Level": pet.get("level", 0),
        }

        description  = format_block("**┌ ACCOUNT BASIC INFO**", basic_fields)
        description += format_block("**┌ ACCOUNT ACTIVITY**",   activity_fields)
        description += format_block("**┌ ACCOUNT OVERVIEW**",   overview_fields)
        description += format_block("**┌ PET DETAILS**",        pet_fields)

        if guild_info.get("GuildID") and str(guild_info.get("GuildID")) != "0":
            guild_fields = {
                "Guild Name":   guild_info.get("GuildName", "N/A"),
                "Guild ID":     guild_info.get("GuildID", "N/A"),
                "Guild Level":  clan_data.get("level", guild_info.get("GuildLevel", "N/A")) if clan_data else guild_info.get("GuildLevel", "N/A"),
                "Live Members": f"{clan_data.get('members', 'N/A')}/50" if clan_data else str(guild_info.get("GuildMember", "N/A")),
            }
            capt = info_res.get("captainBasicInfo", {})
            if capt and isinstance(capt, dict) and capt.keys():
                guild_fields["Leader Name"]  = capt.get("nickname", "N/A")
                guild_fields["Leader UID"]   = capt.get("accountId", "N/A")
                guild_fields["Leader Level"] = capt.get("level", "N/A")
            description += format_block("**┌ GUILD INFO**", guild_fields)
        else:
            description += "**┌ GUILD INFO**\n`L` Not in a guild\n"

        embed = discord.Embed(title="Player Information", description=description, color=0x2b2d31)
        if interaction.user.display_avatar:
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(
            text=f"DARK FF V1 | Requested by {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"An error occurred: `{str(e)}`")


# ==========================================
# /stats — region REQUIRED
# ==========================================

@bot.tree.command(name="stats", description="Get detailed BR or CS stats for a Free Fire player")
@app_commands.describe(
    uid="Player Free Fire UID",
    region="Player server region — MUST match their actual region to get correct data",
    gamemode="Game mode: Battle Royale or Clash Squad",
    matchmode="Match mode: Ranked, Lifetime/Career, or Normal"
)
@app_commands.choices(region=REGION_CHOICES)
@app_commands.choices(gamemode=[
    app_commands.Choice(name="Battle Royale (BR)", value="br"),
    app_commands.Choice(name="Clash Squad (CS)",   value="cs"),
])
@app_commands.choices(matchmode=[
    app_commands.Choice(name="Ranked",            value="RANKED"),
    app_commands.Choice(name="Lifetime / Career", value="CAREER"),
    app_commands.Choice(name="Normal",            value="NORMAL"),
])
@check_channel("stats")
async def slash_stats(
    interaction: discord.Interaction,
    uid: str,
    region: app_commands.Choice[str],
    gamemode: app_commands.Choice[str],
    matchmode: app_commands.Choice[str]
):
    await interaction.response.defer()
    try:
        server = region.value
        g_mode = gamemode.value
        m_mode = matchmode.value

        stats_res = requests.get(
            f"{API_BASE}/stats?uid={uid}&server={server}&gamemode={g_mode}&matchmode={m_mode}"
        ).json()

        if not stats_res.get("success"):
            await interaction.followup.send(
                f"**Error:** {stats_res.get('message', 'Failed to fetch stats')}\n"
                "> Double-check the UID and make sure you selected the correct region."
            )
            return

        data = stats_res.get("data", {})

        if g_mode == "br":
            matches = wins = kills = deaths = top_n = headshots = damage = revives = 0
            for key in ["solostats", "duostats", "quadstats"]:
                s = data.get(key, {})
                matches   += s.get("gamesplayed", 0)
                wins      += s.get("wins", 0)
                kills     += s.get("kills", 0)
                d          = s.get("detailedstats", {})
                deaths    += d.get("deaths", 0)
                headshots += d.get("headshotkills", 0)
                damage    += d.get("damage", 0)
                revives   += d.get("revives", 0)
                top_n     += d.get("topntimes", 0)

            safe_deaths = max(deaths, 1)
            stats_fields = {
                "Matches Played": matches,
                "Wins":           wins,
                "Top Placements": top_n,
                "Kills":          kills,
                "Deaths":         deaths,
                "Booyah Rate":    f"{(wins / max(matches, 1)) * 100:.2f}%",
                "K/D Ratio":      f"{kills / safe_deaths:.2f}",
                "Headshots":      headshots,
                "Total Damage":   damage,
                "Revives":        revives,
            }
        else:
            cs      = data.get("csstats", {})
            matches = cs.get("gamesplayed", 0)
            wins    = cs.get("wins", 0)
            kills   = cs.get("kills", 0)
            d       = cs.get("detailedstats", {})
            deaths    = d.get("deaths", 0)
            headshots = d.get("headshotkills", 0)
            damage    = d.get("damage", 0)
            mvps      = d.get("mvpcount", 0)
            quadra    = d.get("fourkills", 0)

            safe_deaths = max(deaths, 1)
            stats_fields = {
                "Matches Played": matches,
                "Wins":           wins,
                "MVPs":           mvps,
                "Kills":          kills,
                "Deaths":         deaths,
                "Win Rate":       f"{(wins / max(matches, 1)) * 100:.2f}%",
                "K/D Ratio":      f"{kills / safe_deaths:.2f}",
                "Headshots":      headshots,
                "Total Damage":   damage,
                "Quadra Kills":   quadra,
            }

        desc  = format_block(f"**┌ {g_mode.upper()} {m_mode} STATISTICS**", stats_fields)
        embed = discord.Embed(title="Player Statistics", description=desc, color=0x2b2d31)
        if interaction.user.display_avatar:
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(
            text=f"UID: {uid} | {server} | Requested by {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"An error occurred: `{str(e)}`")


# ==========================================
# GLOBAL ERROR HANDLER
# ==========================================

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        msg = "You need **Administrator** permissions to use this command."
    elif isinstance(error, app_commands.CheckFailure):
        return
    else:
        msg = f"An error occurred: {str(error)}"

    if not interaction.response.is_done():
        await interaction.response.send_message(msg, ephemeral=True)
    else:
        await interaction.followup.send(msg, ephemeral=True)


if __name__ == "__main__":
    if TOKEN == "MTU1MjAwMjMzMjAwOTQzOTMyMg.G6af3Z.dGJ7M6Ujun8Sjy8VjUSC-NlYS9o2THCZIjetnI":
        print("Please replace MTU1MjAwMjMzMjAwOTQzOTMyMg.G6af3Z.dGJ7M6Ujun8Sjy8VjUSC-NlYS9o2THCZIjetnI with your actual bot token.")
    else:
        bot.run(TOKEN)
