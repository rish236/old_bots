import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import utils, app_commands
import random as r
from discord.ext.commands import has_permissions, MissingPermissions
import config
import requests
from collections import Counter
from datetime import datetime
import asyncio
from form import Form
import csv
from bs4 import BeautifulSoup
import cloudscraper
import re
import json
import pytz
from typing import Literal
from PIL import Image, ImageFont, ImageDraw



TOKEN = config.llama_token #discord token
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)
etherscan_token = config.etherscan_token

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user} has connected to Discord!!')


def convert_to_discord_timestamp(date_string,timezone):
    try:
        date_format = "%m/%d/%Y %I:%M %p"
    
        tz = pytz.timezone(timezone)
        date_object = datetime.strptime(date_string, date_format)
        if timezone == "UTC":
            date_object = pytz.utc.localize(date_object)  
        else:
            date_object = tz.localize(date_object)
        
        unix_timestamp = int(date_object.timestamp())
        discord_timestamp = f"<t:{unix_timestamp}:F>"
    except Exception as e:
        print(e)
        discord_timestamp = None
    
    return discord_timestamp

@bot.tree.command(name="create_poll", description="Create a poll (admin only)")
async def create_poll(interaction: discord.Interaction, name:str, choice1:str, choice2: str, choice3:str=None, choice4:str=None, choice5:str=None, choice6:str=None, choice7:str=None, choice8:str=None, choice9:str=None, choice10:str=None,time:int=3):
    await interaction.response.defer()
    

    file2 = discord.File("assets/red_llama.png", filename="red_llama.png")


    choices = [value for key, value in locals().items() if key.startswith('choice') and value is not None]
    numbered_choices = '\n'.join([f"{i+1}.) **{choice}**" for i, choice in enumerate(choices)])
    formatted_date = datetime.utcnow().strftime("%A, %B %d, %Y %I:%M %p")
    emb = discord.Embed(title=f"{name}  \U00002753", description=f"{numbered_choices}").set_thumbnail(url=f"https://i.seadn.io/gcs/files/be034dc3f3465e5522f710f147f475d0.gif?auto=format&dpr=1&w=1000").set_footer(text="Created ", icon_url="attachment://red_llama.png")
    emb.add_field(name="", value="Join our platform here: [llamaverse.io](https://home.llamaverse.io/)", inline=False)
    emb.timestamp = datetime.now()
    await interaction.followup.send(f"Starting poll for **{time}** seconds. Cast your vote using the emojis below before the time runs out.", embed=emb,file=file2)
    
    sent_message = await interaction.original_response()
    reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]

    for _ in range(len(choices)):
        await sent_message.add_reaction(reactions[_])

    await asyncio.sleep(time)

    new_message = await sent_message.channel.fetch_message(sent_message.id)
    reaction_list = [reaction.count for reaction in new_message.reactions]

    max_value = max(reaction_list)
    max_indices = [i for i, x in enumerate(reaction_list) if x == max_value]

    if len(max_indices) == 1:
        await interaction.followup.send(f"Poll ended. Thank you for casting your votes! The winner is {choices[max_indices[0]]}!")

    else:
        winners = ""
        for i, _ in enumerate(max_indices):
            winners += f"**{choices[_]}**"
            if i < len(max_indices) - 2:
                winners += ", "
            elif i == len(max_indices) - 2:
                winners += ", and "


        await interaction.followup.send(f"Poll ended. Thank you for casting your votes! The winners are {winners}!")



@create_poll.error
async def create_poll_error(interaction, error):
    if isinstance(error, MissingPermissions):
        print("You must be an administrator to use this command.", error)
    else:
        print("error: ", error)


def make_request(token):
    '''This makes a single request to the server to get data from it.'''
    headers = {'x_cg_demo_api_key': 'CG-SV98yDB95b3mtvXuFQa8NEaV'}
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={token}&precision=4"

    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        raise RuntimeError(f"HTTP Response Code {r.status_code} received from server.")
    else:
        data = json.loads(r.text)        
        return data
            
# @bot.command(name = 'calendar', help = 'Token distribution and vesting')
# async def calendar(ctx):

#     table = """
# | Category            | Sub Category      | Allocation | Tokens (#)    | TGE unlock    | Vesting in mo.(cliff,linear,total)|
# |---------------------|-------------------|------------|-------------- |------------   |---------------------------------  |
# | Private Sale        | Private Sale #1   | 7.0%       | 70,000,000    | 10.0%         | 12, 18, 30                        |
# | Private Sale        | Private Sale #2   | 5.0%       | 50,000,000    | 10.0%         | 9, 15, 24                         |
# | Community Pre-Sale  | Community Presale | 10.00%     | 100,000,000   | TBD           | TBD                               |
# | Community Airdrop   | Airdrop           | 0.0%       | 0             | 0.0%          | *                                 |
# | Ecosystem           | Liquidity         | 5.0%       | 50,000,000    | 100.0%        |                                   |
# | Community Airdrop   | Rewards & Airdrop | 30.0%      | 300,000,000   | 10.0%         | 36 months monthly vesting         |
# | Ecosystem           | Ecosystem         | 25.0%      | 250,000,000   | 0.0%          | 36 months monthly vesting         |
# | Team                | Team              | 15.0%      | 150,000,000   | 0.0%          | 9, 36, 42                         |
# | Ecosystem           | Advisors          | 3.0%       | 30,000,000    | 33.0%         | 12, 36, 42                        |
# |                     |                   | 100%       | 1,000,000,000 | 10.2%         |                                   |  
#    """

#     formatted_table = f"```{table}```"

#     view = discord.ui.View()
#     url = "https://imgur.com/a/5jWr7PR"
#     view.add_item(discord.ui.Button(label="For Mobile Users", url=url))

#     await ctx.send(formatted_table,view=view)
@bot.command(name = 'calendar', help = 'Upcoming events')
async def calendar(ctx):
   # Read the data from the calendar.csv
    events = []
    month_names = {
    1: ("January","https://i.seadn.io/gcs/files/ce7d4e0329c59c4f4e35fae7c2b6c680.gif?auto=format&dpr=1&w=1000"),
    2: ("February","https://i.seadn.io/gcs/files/9e269a2ef3370f3aba716c2cd8c7723f.gif?auto=format&dpr=1&w=1000"),
    3: ("March","https://i.seadn.io/gcs/files/29e92872541b7335e5c48efa99c30b13.gif?auto=format&dpr=1&w=1000"),
    4: ("April","https://i.seadn.io/gcs/files/81582f5b9c2ef89f8ef9681fcda10603.gif?auto=format&dpr=1&w=1000"),
    5: ("May","https://i.seadn.io/gcs/files/a1efdb6764ba73db2566d2d3e289f568.gif?auto=format&dpr=1&w=1000"),
    6: ("June","https://i.seadn.io/gcs/files/0e719e2994d269068d5fb4b56cd6ddab.gif?auto=format&dpr=1&w=1000"),
    7: ("July","https://i.seadn.io/gcs/files/507208209e51a301a9d2e13e9c4927c7.gif?auto=format&dpr=1&w=1000"),
    8: ("August","https://i.seadn.io/gcs/files/7ae48af80ab7a3ca85e264ead18a2f4e.gif?auto=format&dpr=1&w=1000"),
    9: ("September","https://i.seadn.io/gcs/files/081ba3912db3ba3507a2c3a8a607ed4f.gif?auto=format&dpr=1&w=1000"),
    10: ("October","https://i.seadn.io/gcs/files/178d49ab9ee0e73896df80a3ddb2b70a.gif?auto=format&dpr=1&w=1000"),
    11: ("November","https://i.seadn.io/gcs/files/ba774809411ad369c96f515246629c8c.gif?auto=format&dpr=1&w=1000"),
    12: ("December","https://i.seadn.io/gcs/files/1fcecde32948e4f38c222ebfd5440a7e.gif?auto=format&dpr=1&w=1000")
    }
    hours = ''
    def convert_minutes_to_hours(minutes):
        if minutes == 0:
            return ""
        if minutes == 60:
            return "1 hour"
        else:
            hours = minutes / 60
            formatted_hours = "{:.2f}".format(hours)
            if formatted_hours.endswith(".00"):
                return formatted_hours[:-3] + " hours"
            if formatted_hours.endswith("0"):
                return formatted_hours[:-1] + " hours"
            else:
                return formatted_hours + " hours"

    with open('calendar.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        try:
            for row in reader:        
                event = {
                    'date': datetime.strptime(row[0], '%m/%d/%Y'),
                    'name': row[1],
                    'start_time': row[2],
                    'length': row[3],
                    'link': row[4],
                    'timezone': row[5]
                }
                events.append(event)
        except Exception as e:
            pass
            

    # Group the events by month
    events_by_month = {}
    for event in events:
        month = event['date'].month
        if month not in events_by_month:
            events_by_month[month] = []
        events_by_month[month].append(event)

    for month in events_by_month:
        events_by_month[month].sort(key=lambda x: x['date'])


    # Get the current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Create the embed and buttons
    embed = discord.Embed(title=f':calendar_spiral:Events in **{month_names[current_month][0]}**', color=discord.Color.blue())

    view = discord.ui.View()
    prev_button = discord.ui.Button(label='<')
    next_button = discord.ui.Button(label='>')
    view.add_item(prev_button)
    view.add_item(next_button)

    # Show the events for the current month
    month_events = events_by_month.get(current_month, [])
    try:
        for event in month_events:
            date = event['date'].strftime('%m/%d/%Y')
            name = event['name']
            start_time = str(event['start_time'])
            length = str(event['length']) 
            link = event['link'] 
            timezone = event['timezone']
            combined_date = convert_to_discord_timestamp(f'{date} {start_time}',timezone)
            hours = convert_minutes_to_hours(int(length))

            if link!= '':
                embed.add_field(name=f'{combined_date}\n{hours}', value=f"[{name}]({link})", inline=True)
            else:
                embed.add_field(name=f'{combined_date}\n{hours}', value=f"{name}", inline=True)
            hours = ''

    except Exception as e:
        print(e)
        pass
    embed.add_field(name="", value="**Join our platform here:** [llamaverse.io](https://home.llamaverse.io/)", inline=False)
    embed.set_thumbnail(url=month_names[current_month][1])

    async def show_events(interaction: discord.Interaction, month: int):
        embed.clear_fields()
        month_events = events_by_month.get(month, [])
        try:
            for event in month_events:
                date = event['date'].strftime('%m/%d/%Y')
                name = event['name']
                start_time = event['start_time']
                length = event['length'] 
                link = event['link']
                timezone = event['timezone'] 
                combined_date = convert_to_discord_timestamp(f'{date} {start_time}',timezone)


                hours = convert_minutes_to_hours(int(length))
                if link != "":
                    embed.add_field(name=f'{combined_date}\n{hours}', value=f"[{name}]({link})", inline=True)


                else:
                    embed.add_field(name=f'{combined_date}\n{hours}', value=f"{name}", inline=True)
                                                                                                            
                hours = ''
        except Exception as e:
            print(e)
            pass
        embed.title = f':calendar_spiral: Events in **{month_names[month][0]}**'
        embed.add_field(name="", value="**Join our platform here:** [llamaverse.io](https://home.llamaverse.io/)", inline=False)
        embed.set_thumbnail(url=month_names[month][1])
        await interaction.response.edit_message(embed=embed)

    # Add button callbacks
    async def previous_month(interaction: discord.Interaction):
        nonlocal current_month
        # if interaction.user == ctx.author:
        if current_month == 1:
            current_month = 12
        else:
            current_month -= 1
        await show_events(interaction, current_month)

    async def next_month(interaction: discord.Interaction):
        nonlocal current_month
        # if interaction.user == ctx.author:
        if current_month == 12:
            current_month = 1
        else:
            current_month += 1
        await show_events(interaction, current_month)

    prev_button.callback = previous_month
    next_button.callback = next_month

    await ctx.send(embed=embed, view=view)

@bot.tree.command(name="add_event", description="Add an event to the calendar (admin only)")
@app_commands.choices(
  timezone=[ # param name
    app_commands.Choice(name="EST", value="US/Eastern"),
    app_commands.Choice(name="CST", value="America/Chicago"),
    app_commands.Choice(name="MST", value="America/Phoenix"),
    app_commands.Choice(name="PST", value="US/Pacific"),
    app_commands.Choice(name="UTC", value="UTC")
  ]
)
@app_commands.describe(date='mm/dd/YYYY', name='Event name', start_time='hh:mm AM/PM', timezone='timezone', length='Time in minutes ie. 60', link='Must be in the format: https://linkgoeshere.com')
async def add_event(interaction: discord.Interaction, date: str, name: str, start_time: str, timezone: app_commands.Choice[str],length: int = 0, link: str = ""):
    # if not interaction.user.guild_permissions.administrator:
    #     await interaction.response.send_message("You must be an administrator to use this command.", ephemeral=True)
    #     return
    
    try:
        datetime.strptime(date, '%m/%d/%Y')
    except ValueError:
        await interaction.response.send_message("Invalid date format. Please use the format mm/dd/YYYY.(4/25/2024) You entered {date}", ephemeral=True)
        return

    if link != "" and not re.match(r'^https://', link):
        await interaction.response.send_message(f"Invalid link format. Please use the format https:// You entered: {link}", ephemeral=True)
        return

    allowed_time = ["am", "pm"]
    x = start_time[-2:].lower()
    if(len(start_time.split(" ")) != 2 or start_time[-2:].lower() not in allowed_time):
        await interaction.response.send_message(f"Please make sure you included AM or PM at the end, separated with a space. (9:30 AM). You entered: '{start_time}'", ephemeral=True)
        return
    
    event = {
        'date': date,
        'name': name,
        'start_time': start_time,
        'length': length,
        'link': link,
        'timezone': timezone.value
    }
    try:
        with open('calendar.csv', mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['date', 'name', 'start_time', 'length', 'link','timezone'])
            writer.writerow(event)
            await interaction.response.send_message("Event added successfully!", ephemeral=True)

            
    except:
        await interaction.response.send_message("Unable to add event, please try again later.", ephemeral=True)

@bot.tree.command(name="edit_event", description="Edit an event in the calendar (admin only)")
@app_commands.choices(
  new_timezone=[ # param name
    app_commands.Choice(name="EST", value="US/Eastern"),
    app_commands.Choice(name="CST", value="America/Chicago"),
    app_commands.Choice(name="MST", value="America/Phoenix"),
    app_commands.Choice(name="PST", value="US/Pacific"),
    app_commands.Choice(name="UTC", value="UTC")
  ]
)
@app_commands.describe(new_date='mm/dd/YYYY', new_name='Event name', new_start_time='hh:mm AM/PM',new_timezone='timezone', new_length='Time in minutes ie. 60', new_link='Must be in the format: https://linkgoeshere.com')
async def edit_event(interaction: discord.Interaction, event_name: str, new_date: str = None, new_name: str = None, new_start_time: str = None, new_timezone: app_commands.Choice[str] = None, new_length: int = None, new_link: str = None):
    # if not interaction.user.guild_permissions.administrator:
    #     await interaction.response.send_message("You must be an administrator to use this command.", ephemeral=True)
    #     return
    try:
        with open('calendar.csv', mode='r') as file:
            reader = csv.DictReader(file)
            events = list(reader)
    
        event = next((e for e in events if e['name'] == str(event_name)), None)
        if event is None:
            await interaction.response.send_message("Event not found.", ephemeral=True)
            return
    
        if new_date is not None:
            try:
                datetime.strptime(new_date, '%m/%d/%Y')
            except ValueError:
                await interaction.response.send_message("Invalid date format. Please use the format mm/dd/YYYY.", ephemeral=True)
                return
            event['date'] = new_date
        
        if new_name is not None:
            event['name'] = new_name
        
        if new_start_time is not None:
            event['start_time'] = new_start_time
        
        if new_length is not None:
            event['length'] = new_length
        
        if new_link is not None:
            if not re.match(r'^https://', new_link):
                await interaction.response.send_message("Invalid link format. Please use the format https://", ephemeral=True)
                return
            event['link'] = new_link

        if new_timezone is not None:
            event['timezone'] = new_timezone.value

        with open('calendar.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['date', 'name', 'start_time', 'length', 'link','timezone'])
            writer.writeheader()
            writer.writerows(events)
    
        await interaction.response.send_message("Event edited successfully!", ephemeral=True)
    
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@bot.tree.command(name="remove_event", description="Remove an event from the calendar (admin only)")
async def remove_event(interaction: discord.Interaction, event_name: str):
    # if not interaction.user.guild_permissions.administrator:
    #     await interaction.response.send_message("You must be an administrator to use this command.", ephemeral=True)
    #     return
    
    try:
        with open('calendar.csv', mode='r') as file:
            reader = csv.DictReader(file)
            events = list(reader)
    
        event = next((e for e in events if e['name'] == event_name), None)
        if event is None:
            await interaction.response.send_message("Event not found.", ephemeral=True)
            return
    
        events.remove(event)
    
        with open('calendar.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['date', 'name', 'start_time', 'length', 'link','timezone'])
            writer.writeheader()
            writer.writerows(events)
    
        await interaction.response.send_message("Event removed successfully!", ephemeral=True)
    
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

@bot.command(name = 'form', help = 'Fill out form')
async def form(ctx):
    form = Form(ctx.interaction)
    await ctx.send(view=form)

@bot.command(name = 'show_form', help = 'Show csv file')
async def show_form(ctx):
    # if not interaction.user.guild_permissions.administrator:
    #     await interaction.response.send_message("You must be an administrator to use this command.", ephemeral=True)
    #     return
    
    file = discord.File("form.csv")
    await ctx.send(file=file, ephemeral=True)

@show_form.error
async def show_form_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have the required permissions to use this command.", ephemeral=True)
    else:
        await ctx.send("An error has occurred, please try again later.", ephemeral=True)


    
# @bot.tree.command(name="wallet_checker", description="Wallet checker + live token data.")
# @app_commands.choices(
#   token_name=[ # param name
#     app_commands.Choice(name="QORPO", value="qorpo"),
#     app_commands.Choice(name="Blockgames", value="blockgames"),
#     app_commands.Choice(name="MetaDOS", value="metados"),
#     app_commands.Choice(name="Mintify", value="mintify"),
#     app_commands.Choice(name="Bowled", value="bowled"),
#     app_commands.Choice(name="Skillful AI", value="skillfulai"),
#     app_commands.Choice(name="WITS", value="wits"),
#     app_commands.Choice(name="PlayEmber KOL", value="pekol"),
#     app_commands.Choice(name="PlayEmber Strategic", value="pestrat"),
#     app_commands.Choice(name="SA World", value="saworld"),
#     app_commands.Choice(name="Kokodi", value="kokodi"),
#     app_commands.Choice(name="Everreach", value="everreach"),
#     app_commands.Choice(name="Redacted Coin", value="redactedcoin"),
#     app_commands.Choice(name="SOMO", value="somo"),
#     app_commands.Choice(name="CounterFire", value="counterfire"),
#     app_commands.Choice(name="Revolving Games", value="revolvinggames"),
#     app_commands.Choice(name="KIP Protocol", value="kipprotocol"),
#     app_commands.Choice(name="BloodLoop", value="bloodloop"),
#     app_commands.Choice(name="Well3", value="well3"),
#     app_commands.Choice(name="Aether", value="aether"),
#     app_commands.Choice(name="Kokodi", value="mixmob"),
#     app_commands.Choice(name="Lingo", value="lingo"),
#     app_commands.Choice(name="Portal", value="portal"),
#     app_commands.Choice(name="Block Lords", value="blocklords")


#   ]
# )
# async def wallet_checker(interaction: discord.Interaction, address:str, token_name: app_commands.Choice[str]):
#     await interaction.response.defer()

#     file = discord.File("assets/red_llama.png", filename="red_llama.png")
#     amount = 0

#     token = token.lower()
#     try:
#         with open(f'{token}.csv') as csvfile:
#             reader = csv.DictReader(csvfile)

#             prev_url = ""
#             scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})

#             # Iterate through the rows and search for the word in a specific column
#             for row in reader:
#                 if row["Wallet"] == address:
#                     if token == "bloodloop":
#                         url = row["Etherscan"]
#                         #check for multiple links in one row

#                         if ".io" not in url:
#                             url = f"https://etherscan.io/tx/{url}"
#                         try:
#                             if prev_url != url:
#                                 response = scraper.get(url)
#                                 html_content = response.text
#                                 soup = BeautifulSoup(html_content, 'html.parser')
#                                 element = soup.select_one('span.text-muted:nth-child(7)').text
#                                 amount += round(float(re.findall(r"\d+\.\d+|\d+", element)[0]), 2)
#                                 prev_url = url
                            
#                         except Exception as e:
#                             element = row["Amount"]
#                             amount += round(float(re.findall(r"\d+\.\d+|\d+", element)[0]), 2)
#                             print(e,amount)

#                     if token == "mixmob":
#                         amount = row["Amount"]
#                         initial = row["Initial"]
#                         monthly = row["Monthly"]
#     except FileNotFoundError as e:
#         embed=discord.Embed(title ="", description= "Sorry, this token is not supported. Please try again with a supported token.")
#         await interaction.followup.send(embed=embed, ephemeral=True)
#         return

#     if float(amount) == 0: 
#         embed=discord.Embed(title ="", description= "Sorry, there are no records of this wallet in our database. Please try a different wallet or contact xyz for assitance.")
    
#     if token == "bloodloop":
#         if amount > 300:
#             embed=discord.Embed(title ="",description= f"You have contributed a total of **${amount}**. This unlocks **5%** BloodLoop :drop_of_blood: on TGE and **3%** every month for 15 months.")
#         else:
#             embed=discord.Embed(title ="", description= f"You have contributed a total of **${amount}**. This unlocks **2%** BloodLoop :drop_of_blood: on TGE and **1%** every month for 15 months.")
#     if token == "mixmob":
#         try:
#             mxb_data = make_request("mixmob")
#             current_price = mxb_data[0]['current_price']

#             table = f"""|---------------|----------------|\n| Current Price | 24 Hr % Change | \n| ${current_price:,}       | {mxb_data[0]['price_change_percentage_24h']:.2f}%         |\n|---------------|----------------|\n| Total Supply  | Total Volume   |\n| 1,000,000,000 | ${mxb_data[0]['total_volume']:,.2f}  |\n|---------------|----------------|\n| Total Market Cap  | Mcap 24 hr % change |  \n| ${mxb_data[0]['market_cap']:,}       | {mxb_data[0]['market_cap_change_percentage_24h']:.2f}%              |\n|-------------------|---------------------|
#              """

#             # embed.add_field(name="Current Price", value=f"${mxb_data[0]['current_price']:,}", inline=True)
#             # embed.add_field(name="Total Volume", value=f"${mxb_data[0]['total_volume']:,}", inline=True)
#             # embed.add_field(name="Total Supply", value=f"1,000,000,000", inline=True)
#             # embed.add_field(name="Market Cap", value=f"${mxb_data[0]['market_cap']:,}", inline=True)
#             # embed.add_field(name="24 Hr Percentage Change", value=f"{mxb_data[0]['price_change_percentage_24h']:.2f}%", inline=True)

#             formatted_table = f"```{table}```"
#             embed=discord.Embed(title ="", description=formatted_table)
#             embed.set_thumbnail(url=mxb_data[0]["image"])
#             embed.set_footer(text="Created ")
#             embed.timestamp = datetime.now()


#             initial_amount = float(initial) * current_price
#             monthly_amount = float(monthly) * current_price

#             description= f""" You have contributed a total of **${amount}**. This unlocks **{initial}** MixMob on TGE (current estimated value is ${initial_amount:,.2f}) and **{monthly}** MixMob (current estimated value is ${monthly_amount:,.2f}) every month for 15 months."""
#             embed.add_field(name="", value=description, inline=False)


#         except Exception as e:
#             print(e)
#     embed.add_field(name="", value="**Join our platform here:** [llamaverse.io](https://home.llamaverse.io/)", inline=False)
#     await interaction.followup.send(embed=embed, ephemeral=True)


# def draw(current_price, total_supply, total_volume, total_mcap, day_change, mcap_day_change):
#     image = Image.open('assets/Llamaverse_WalletTokenCheck_Blank.png')
#     draw = ImageDraw.Draw(image)

#     # Define the font
#     font_bold = ImageFont.truetype("assets/ChakraPetch-Bold.ttf", size=100)
#     font_regular = ImageFont.truetype("assets/ChakraPetch-Regular.ttf", size=40)

#     # Define the text and positions for each variable

#     # Draw text on the image for each variable
#     draw.text((130, 135 + 30), f"{current_price}", font=font_bold, fill=(160, 32, 240))
#     draw.text((620, 390 + 30), f"{total_volume}", font=font_regular, fill=(255, 255, 255))
#     draw.text((620, 190 + 30), f"{day_change}", font=font_regular, fill=(255, 255, 255))
#     draw.text((130, 390 + 30), f"{total_supply}", font=font_regular, fill=(255, 255, 255))
#     draw.text((130, 600 + 30), f"{total_mcap}", font=font_regular, fill=(255, 255, 255))
#     draw.text((620, 600 + 30), f"{mcap_day_change}", font=font_regular, fill=(255, 255, 255))


#     # Save the modified image
#     image.save('assets/Llamaverse_WalletTokenCheck_Numbered.png')

bot.run(TOKEN, reconnect=True)


