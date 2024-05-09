import discord
import os
from discord.ext import commands
from discord.ext.commands import Bot
from discord import utils
import random as r
import time
from datetime import datetime, timedelta, timezone
from discord.ext.commands import has_permissions
from discord_slash import SlashCommand, SlashContext
from discord.ext.tasks import loop
from discord.ext import *
import requests
import json
import config
from discord_slash.utils.manage_commands import create_choice, create_option
import psycopg2
from psycopg2.extensions import AsIs
from psycopg2.errors import UniqueViolation
import time
from datetime import datetime, timedelta, timezone
import pytz
from dateutil import tz
import requests
import re
import tweepy


TOKEN = config.anti_alpha_token


bot = commands.Bot(command_prefix='!')
slash = SlashCommand(bot, sync_commands=True)

@slash.slash(
    name='remindme',
    description='Set up a reminder to notify the community of an upcoming event.',
    guild_ids=[899440695671160912, 933093752417972275], 
    options=[
        create_option(name="option", description="Select an event type", required=True, option_type=3,
        choices=[create_choice(name="Mint",value="mint"), create_choice(name="Other",value="other"), create_choice(name="Birthday",value="birthday")]
        ),
        create_option(name="message", description="Enter a message", required=True, option_type=3 
        ),
        create_option(name="month", description="Select a month", required=True, option_type=3,
        choices=[create_choice(name="January",value="01"), create_choice(name="February",value="02"), create_choice(name="March",value="03"), create_choice(name="April",value="04"), create_choice(name="May",value="05"), create_choice(name="June",value="06"), create_choice(name="July",value="07"), create_choice(name="August",value="08"), create_choice(name="September",value="09"), create_choice(name="October",value="10"), create_choice(name="November",value="11"), create_choice(name="December",value="12")]
        ),
        create_option(name="day", description="Enter a day", required=True, option_type=4 
        ),
        create_option(name="year", description="Select a year", required=True, option_type=3,
        choices=[create_choice(name="2022",value="2022"), create_choice(name="2023",value="2023")]
        ),
        create_option(name="time", description="Enter a time. HH:MM AM/PM", required=True, option_type=3 
        ),
        create_option(name="timezone", description="Select a timezone", required=True, option_type=3,
        choices=[create_choice(name="EST",value="US/Eastern"), create_choice(name="CST",value="America/Chicago"), create_choice(name="MST",value="America/Phoenix"), create_choice(name="PST",value="US/Pacific")]
        ),
        ]
)
async def remindme(ctx:SlashContext, option:str, message:str, month:str, day:int, year:str, time:str, timezone:str):
    conn = psycopg2.connect(
                    host="localhost",
                    database="a3w",
                    user="postgres",
                    password="")
    conn.autocommit = True
    cur = conn.cursor()
    try:
        if day < 1 or day > 31:
            await ctx.send(f"Please enter a correct day. You entered: '{day}' ")
            return
        print("length of time: ", len(time.split(" ")))
        allowed = ["am", "pm"]
        x = time[-2:].lower()
        if(len(time.split(" ")) != 2 or time[-2:].lower() not in allowed):
            print(f"time[-2:].lower{time[-2:].lower()}")
          
            await ctx.send(f"Please make sure you included AM or PM at the end, separated with a space. (9:30 AM). You entered: '{time}'")
            return
        else:
            print("length of time is 2")
            in_time = datetime.strptime(time, "%I:%M %p")
            out_time = datetime.strftime(in_time, "%H:%M")
            print(out_time)


            
            date = f"{year}-{month}-{day} {out_time}:00"
            to_zone = tz.gettz('UTC')
            def convert_to_utc(timezone, date):
                to_zone = tz.gettz('UTC')
                from_zone = tz.gettz(timezone)
                x = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                x = x.replace(tzinfo=from_zone)
                x = x.astimezone(to_zone)
                utc = x.astimezone(to_zone)
                return utc

            utc = convert_to_utc(timezone, date)
            

            
            if datetime.utcnow() > utc.replace(tzinfo=None):
                await ctx.send("Please pick a date in the future.")
                return
            else:
                user = str(ctx.author)
                
                print('Connecting to the PostgreSQL database...')
                id = ctx.author.id
                
                cur.execute('INSERT into remindme (userid, username, option, message, date) VALUES(%s, %s, %s, %s, %s)', (id, user, option, message, utc))
                print(f"inserted username: {user} option: {option} message: {message} date: {date}")
                await ctx.send(f"Congratulations **{ctx.author.mention}**, you have successfully set up a reminder for **{message}** @ **{month}/{day}/{year} {time}**")
                conn.close()
    except Exception as e:
        print(e)
        await ctx.send("Unable to add reminder. Please try again.")
        conn.close()
        return
        

@slash.slash(
    name='google',
    description="Retrieves top 5 links from google given a query.",
    guild_ids=[899440695671160912], 
    options=[
        create_option(name="google", description="Enter search query", required=True, option_type=3)
        ]
)
async def google(ctx, google):
    service = build("customsearch", "v1",
            developerKey=config.google_key)

    res = service.cse().list(
        q=google,
        cx='',
        ).execute()
    print("response", res) 
    try:
        items = res["items"]
        top_five_links = []
        for i in items:
            if(len(top_five_links)<5):
                top_five_links.append(i["link"])
        print(res["items"])
        print(top_five_links)
        
    except:
        return 
    msg = ""      
    for _ in top_five_links[:5]:
        msg += _ + '\n\n'
    
    await ctx.send(embed=discord.Embed(title=f"Top 5 links: ", 
            description=f"{msg}"))

@bot.command(name="gary",pass_context=True)
async def gary(ctx):
    await ctx.send(file=discord.File('gary.gif'))

@bot.command(name="shr00m",pass_context=True)
async def shr00m(ctx):
    await ctx.send(file=discord.File('shroom.gif'))

@slash.slash(
    name='profile',
    description="View a person's NFT collection.",
    guild_ids=[899440695671160912, 933093752417972275], 
    options=[
        create_option(name="address", description="Enter contract address or ENS name.", required=True, option_type=3)
        ]
)
async def profile(ctx, address):
    wallet_address = address

    print("wallet ", wallet_address)
    await ctx.defer()
    if ".eth" in wallet_address:
        try:
            w3 = Web3(Web3.HTTPProvider(INFURA))
            ns = ENS.fromWeb3(w3)
            wallet_address = ns.address(wallet_address)
            if wallet_address is None:
                await ctx.send("Unable to find a corresponding wallet address, please try different one.")
            print(wallet_address)
        except Exception as e:
            print(e)
    order_by = "sale_date"
    url = f"https://api.opensea.io/api/v1/assets?owner={wallet_address}&order_by={order_by}&order_direction=desc&offset=0&limit=50"
    
    try:
        response = requests.request("GET", url)
        if response.status_code == 400:
            await ctx.send("Unable to find wallet address. Please try again.")
    except Exception as e:
        print(e)
        await ctx.send("Unable to find wallet address. Please try again.")

    # print(response)
    x = json.loads(response.text)
    # print(x)

    for _ in range(len(x["assets"])):
        try:
            if str(x["assets"][_]["collection"]["hidden"]) == "True":
                del x["assets"][_]
        except Exception as e:
            pass

    
    num_assets = len(x["assets"])
    print(num_assets)
    if num_assets == 0:
        await ctx.send("Unable to find any assets. Please try a different address.")
    page_dict = {}
    
    for i in range(num_assets):
        try:
            hidden = x["assets"][i]["collection"]["hidden"]
            image_url = x["assets"][i]["image_url"]
            if ".svg" in image_url:
                image_url = "https://i.ibb.co/zX8Nm7D/on-chain-error.png"
            # print("image_url : ", image_url)
            name = x["assets"][i]["name"]
            if name is None:
                name = x["assets"][i]["asset_contract"]["name"]
                if "unidentified" in name.lower():
                    print(i)
                    json_formatted_str = json.dumps(x["assets"][i], indent=2)
                    raise Exception('Unidentified contract') 
                    print(json_formatted_str)
            if image_url is None:
                print("image url is none")
        
            page_dict[i] = discord.Embed (
            title = f'Page {i+1}/{num_assets}',
            description = f"""{name} | OS link: {x["assets"][i]["permalink"]}""",
            colour = discord.Colour.orange()
            ).set_image(url=image_url)
        except Exception as e:
            image_url = "https://i.ibb.co/1Xv5phJ/big-error.png"

            page_dict[i] = discord.Embed (
            title = f'Page {i+1}/{num_assets}',
            description = name,
            colour = discord.Colour.orange()
            ).set_image(url=image_url)
            print(e)
            pass
    
    
    i = 0
   
    message = await ctx.send(embed = page_dict[i])
    message_id = message.id

    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')

    def check(reaction, user):
        return user == ctx.author and reaction.message.id == message_id

    reaction = None
    while True:
        if str(reaction) == '⏮':
            i = 0
            await message.edit(embed = page_dict[i])
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = page_dict[i])
        elif str(reaction) == '▶':
            if i < num_assets - 1:
                i += 1
                await message.edit(embed = page_dict[i])
        elif str(reaction) == '⏭':
            i = num_assets - 1
            await message.edit(embed = page_dict[i])
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout = 3600.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!!')
    

@bot.command(name="vibe",pass_context=True)
async def vibe(ctx):
    await ctx.send("<a:ToadSquirtlevibe:900590197354397726> <a:ToadSquirtlevibe:900590197354397726> <a:ToadSquirtlevibe:900590197354397726> <a:ToadSquirtlevibe:900590197354397726> <a:ToadSquirtlevibe:900590197354397726>")

@slash.slash(
    name='stats',
    description='Retrieve OpenSea specific stats for a specific collection.',
    guild_ids=[899440695671160912, 933093752417972275,938306481760137216], 
    options=[
        create_option(name="slug", description="Enter a collection slug.", required=True, option_type=3)
        ]
)
async def stats(ctx, *, slug):
    collection_slug = slug.replace(" ", "-")
    print('slug: ', collection_slug)
    if "opensea.io" in collection_slug.lower():
        collection_slug = collection_slug.rsplit('/', 1)[-1]
    try:

        collection_stats_url = f"https://api.opensea.io/api/v1/collection/{collection_slug}/stats"
        collection_url = f"https://api.opensea.io/api/v1/collection/{collection_slug}"
        
        headers = {"Accept": "application/json"}
        response = requests.request("GET", collection_stats_url, headers=headers)
        response2 = requests.request("GET", collection_url, headers=headers)

        retry = 5
        
        for _ in range(retry):
            try:
                collection_stats_dict = json.loads(response.text)
                collection_dict = json.loads(response2.text)
                break
            except Exception as e:
                print(e)
                time.sleep(.5)
                continue
        # print(collection_dict)
        await ctx.defer()

        try:
            collection_image_url = collection_dict['collection']['primary_asset_contracts'][0]['image_url']
        except IndexError:
            try:
                collection_image_url = collection_dict['collection']['image_url']
            except Exception as e:
                collection_image_url = "https://www.russorizio.com/wp-content/uploads/2016/07/ef3-placeholder-image.jpg"

    
        if collection_image_url is None:
            collection_image_url = "https://www.russorizio.com/wp-content/uploads/2016/07/ef3-placeholder-image.jpg"
        
        def round_num(s):
            try:
                return "{:0.2f}".format(s)
            except:
                return ('---')

        floor_price, one_day_volume, one_day_change, one_day_sales, one_day_average_price, seven_day_volume, seven_day_change, seven_day_sales, seven_day_average_price, thirty_day_volume, thirty_day_change, thirty_day_sales, thirty_day_average_price, total_volume, total_sales, total_supply, num_owners, market_cap = (
            round_num(collection_stats_dict['stats'][key]) for key in (
                'floor_price',
                'one_day_volume',
                'one_day_change',
                'one_day_sales',
                'one_day_average_price',
                'seven_day_volume',
                'seven_day_change',
                'seven_day_sales',
                'seven_day_average_price',
                'thirty_day_volume',
                'thirty_day_change',
                'thirty_day_sales',
                'thirty_day_average_price',
                'total_volume',
                'total_sales',
                'total_supply',
                'num_owners',
                'market_cap',
            ))

       
        if one_day_volume == seven_day_volume == thirty_day_volume and one_day_change == seven_day_change == thirty_day_change and one_day_sales == seven_day_sales == thirty_day_sales:
            await ctx.send(embed=discord.Embed(title=f"Stats for {collection_slug} | Floor: {floor_price} Ξ", 
            description=f"""\n
            **One Day Volume:** {one_day_volume} Ξ
            **One Day Sales:** {one_day_sales} 
            **One Day Average Price:** {one_day_average_price} Ξ\n
            **Total Volume:** {total_volume} Ξ 
            **Total Sales:** {total_sales}  
            **Total Supply:** {total_supply}  
            **Number of Owners:** {num_owners} 
            **Market Cap:** {market_cap} Ξ
            **OpenSea:** https://opensea.io/collection/{collection_slug}
            """
            ).set_thumbnail(url=collection_image_url))
        else:
            await ctx.send(embed=discord.Embed(title=f"Stats for {collection_slug} | Floor: {floor_price} Ξ", 
            description=f"""\n
            **One Day:** 
            **Volume:** {one_day_volume} Ξ | **Sales:** {one_day_sales} | **Average Price:** {one_day_average_price} Ξ\n
            **Seven Day:** 
            **Volume:** {seven_day_volume} Ξ | **Sales:** {seven_day_sales} | **Average Price:** {seven_day_average_price} Ξ\n
            **Thirty Day:**
            **Volume:** {thirty_day_volume} Ξ | **Sales:** {thirty_day_sales} | **Average Price:** {thirty_day_average_price} Ξ\n
            **Total Volume:** {total_volume} Ξ | **Total Sales:** {total_sales} Ξ | **Total Supply:** {total_supply} | **Number of Owners:** {num_owners} | **Market Cap:** {market_cap} Ξ
            **OpenSea:** https://opensea.io/collection/{collection_slug}
            """
            ).set_thumbnail(url=collection_image_url))
    except Exception as e:
        print(e)
        await ctx.send(f"Unable to find **'{collection_slug}'**. Please try a different name, or append the opensea link directly.")


# wallet_address = "0x0c50ac8dc16b41901cdcfd65e3f0b149110ecdbe"
# order_by = "sale_date"

# url = f"https://api.opensea.io/api/v1/assets?owner={wallet_address}&order_by={order_by}&order_direction=desc&offset=0&limit=50"

# response = requests.request("GET", url)
# x = json.loads(response.text)

# num_assets = len(x["assets"])
# for x["assets"][16]["name"]
@loop(seconds=10)
async def gas():
    url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHERSCAN_TOKEN}"
    response = requests.request("GET", url)
    x = json.loads(response.text)
    print(x)
    safe_gas_price = x['result']['SafeGasPrice']
    proposed_gas_price = x['result']['ProposeGasPrice']
    fast_gas_price = x['result']['FastGasPrice']
    channel = bot.get_channel(900513205254783006)

    now_utc = datetime.now(timezone.utc)

    utc_ts = now_utc.strftime("%Y-%m-%d %H:%M:%S")
    #current_timestamp =` datetime.strptime(utc_ts , '%Y-%m-%d %H:%M:%S')

    await channel.send(embed=discord.Embed(title=f"test {utc_ts}", description=f"""{safe_gas_price} \n {proposed_gas_price} \n{fast_gas_price}"""))
            #.set_thumbnail(url=collection_image_url))
   

@gas.before_loop
async def before_gas():
    await bot.wait_until_ready()


gas.start()


@bot.command(name="events",pass_context=True)
async def events(ctx):
    conn = psycopg2.connect(
    host="localhost",
    database="a3w",
    user="postgres",
    password="")
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute("SELECT username, option, message, date from remindme where date > NOW() order by date ASC;")
        x = cur.fetchall()
        embed = discord.Embed(title="**Upcoming Events**", description="")
        for _ in x:
            print(f"0-{_[0]}  1-{_[1]}  2-{_[2]}  3-{_[3]}")
            print("BEFORE: ", _[3])
            adj_time = _[3]-timedelta(hours=1)
            print("AFTER: ", adj_time)
            embed.add_field(name='\u200b', value=f"- **{_[0]}** [{_[1]}] **{_[2]}** @ **{adj_time} UTC**", inline=False)

        await ctx.send(embed=embed)
        conn.close()
    except Exception as e:
        print(e)
        conn.close()
        return
    await ctx.send()

@loop(seconds=20)
async def poll():

    conn = psycopg2.connect(
    host="localhost",
    database="a3w",
    user="postgres",
    password="")
    conn.autocommit = True
    cur = conn.cursor()

    channel = bot.get_channel(900513205254783006)
    try:
        print("before execute")
        cur.execute("SELECT id, userid, username, option, message, date, started from remindme where date >NOW() and date  < (NOW() + '2 minute'::interval);")
        id, userid, username, option, message, date, started = cur.fetchone()
        print(f"id {id}, userid {userid}, username {username}, option {option}, message {message}, date {date}, started {started}")
    except Exception as e:
        print(e)
        conn.close()
        return

    if started == False:
        await channel.send(f"**<@{userid}>, [{str(option).upper()}] {message}** is about to start in ~ 2 minutes.")
        cur.execute("update remindme set started = true where id = %s;", [id] )
        print("updated started to true")
        conn.close()
            #.set_thumbnail(url=collection_image_url))
   

@poll.before_loop
async def before_poll():
    await bot.wait_until_ready()


@loop(seconds=1)
async def get_following():
    webhook = "https://discord.com/api/webhooks/948285200683630592/-p4E-TWA7XFODqEk7dRJYb-NKFK_Z7KH0zKM7XbSDKWyd5UCvbJVRD7UTOwOxkcbDr_F"
    webhook = Webhook.from_url(webhook, adapter=RequestsWebhookAdapter())
    webhook.send(file=discord.File('hackerpepe.png'))

    client = tweepy.Client(bearer_token = config.bearer_token)
    id = '1482745703877300230'
    tweet = client.get_users_tweets(id = id, max_results = 5)[0]


    channel = bot.get_channel(920128631253127249)
    userid= '504403562814504970'
    if tweet == None: 
        pass
    else:
        if tweet != bot.prev_tweet:
            print(f"prev tweet{bot.prev_tweet}")
            print(f"latest tweet{tweet}")
            
            print(tweet)
            bot.prev_tweet = tweet
            # await channel.send(f"**<@{userid}> {tweet}")
        else:
            print("no new tweet")

    conn = psycopg2.connect(
            host="localhost",
            database="origins",
            user="postgres",
            password="rishunika")
    conn.autocommit = True
    print('Connecting to the PostgreSQL database...')
    try:
        now_utc = datetime.now(timezone.utc)
        #use this
        utc_ts = now_utc.strftime("%Y-%m-%d %H:%M:%S")

        # current_ts = datetime.strptime(utc_ts , '%Y-%m-%d %H:%M:%S')

        embed = discord.Embed(
            color= discord.Colour.from_rgb(139, 0, 0),
            title=f"Followers since {utc_ts} (utc) "
        ).set_thumbnail(url="https://cdn.cms-twdigitalassets.com/content/dam/help-twitter/twitter_logo_blue.png.twimg.768.png")

        client = tweepy.Client(bearer_token = config.bearer_token)
        user = 'rishiiiiie'


        user_dict = {
        '973261472':'blknoiz06',   
        '4841112920': 'AamishQureshi',
        '1122211825452556288': 'theshamdooo',
        '1376640140429303810': 'manifoldxyz',
        '3005650652': 'seedphrase',
        '1227321079812837377': 'gaby_goldberg',
        '1351139954525696005': 'beanie_maxie',
        '1249460237913874433': 'statelayer',
        '13258512': 'dhof',
        '1009505839764377601': 'rishiiiiie',
        '1103379871458344962': 'jpatten__',
        '2621412174':'pranksy',
        "1388487332093997057":'punk6529',
        '1835943590':'OttoSuwenNFT',
        '5768872':'garyvee' ,
        '1265388355392593920':'VonMises14',
        '1376670936917811207':'hi_sighduck',
        '127646057':'DeezeFi',
        '178036598':'Anonymoux2311', 
        "1380417603013898241":'sartoshi_nft' 
        }
        user_list = [user_dict[id] for id in user_dict.keys()]
        cur = conn.cursor()

        def get_most_recent():
            cur.execute(
            'SELECT ts,id from %s WHERE ts >= ALL(select ts from %s)', 
            (AsIs(f"t{id}"), AsIs(f"t{id}"))
            )
            ts, db_id = cur.fetchone()
            print("MOST RECENT DB ID: ", db_id)
            return ts, db_id



        def is_following(db_id):
            for _ in range(len(x.data)):
                if db_id in str(x.data[_]['id']):
                    return True
            return False

        def match(id):
            num_new_followers = 0
            for _ in range(len(x.data)):
                # print("RE.SUB: ", re.sub("[^0-9]", "", str(x.data[_]['id'])))
                if id != re.sub("[^0-9]", "", str(x.data[_]['id'])):
                    # print("db id: ", id)
                    print("twitter id", x.data[_]['id'])
                    num_new_followers += 1
                    following_list.append(x.data[_]['username'])
                else:
                    print('matched')
                    return num_new_followers

        for i in range(len(user_list)):
            following_list = []

            id = user_list[i]
            print('id: ', id)
            x = client.get_users_following(id = id, max_results=50)
            num_new_followers = 0
            ts = ""
            
            ten_list = []

        
        
            ten = x.data[:10]

        
            most_recent_username = x.data[0]['username']
            most_recent_id = x.data[0]['id']


            try:
                ts, db_id = get_most_recent()
                print(ts, db_id)
            except Exception as e:
                print(e)
                pass
            
        

            MAX_RETRIES = 10
            retries = MAX_RETRIES

        
            while retries > 0:
                if is_following(db_id):
                    num_new_followers = match(db_id)
                    break
                else:
                    cur.execute(
                        'DELETE FROM %s WHERE id = %s', 
                        (AsIs(f"t{id}"),db_id)
                        )
                    ts, db_id = get_most_recent()
                    retries -= 1
                    print(f"~~~~~~ts: {ts} db_id: {db_id}~~~~~~")
                
            for _ in ten[::-1]:
                try:
                    cur.execute(
                    'INSERT into %s VALUES(%s, %s)', 
                    (AsIs(f"t{id}"),_['username'],_['id'])
                    )
                    print(f"inserted username: {_['username']} id: {_['id']}")
                except Exception as e:
                    continue

            if num_new_followers == None:
                num_new_followers = 0
            try:
                
                #     msg += f"**@{user_dict[id]}** - Following {num_new_followers} new person.\n"
                # else:
                #     msg += f"**@{user_dict[id]}** - Following {num_new_followers} new people.\n"

                if num_new_followers == 1:
                    embed.add_field(name='\u200b', value=f"**[@{user_dict[id]}](https://www.twitter.com/{user_dict[id]})** - Following {num_new_followers} new person.\n" + str([f"[{_}](https://www.twitter.com/{_})" for _ in following_list]), inline=False)
                elif num_new_followers == 0:
                    print("num followers 0")
                    pass
                else:
                    embed.add_field(name='\u200b', value=f"**[@{user_dict[id]}](https://www.twitter.com/{user_dict[id]})** - Following {num_new_followers} new people.\n" + str([f"[{_}](https://www.twitter.com/{_})" for _ in following_list]), inline=False)

                
                time.sleep(3)


            except Exception as e:
                print(e)

       
        channel = bot.get_channel(900513205254783006)

       

        # embed = discord.Embed(
        #     color= discord.Colour.from_rgb(139, 0, 0),
        #     title=f"Followers Since {utc_ts}: ", 
        #     description= msg + str([f"[{_}](https://www.twitter.com/{_})" for _ in following_list])
        # ).set_thumbnail(url="https://cdn.cms-twdigitalassets.com/content/dam/help-twitter/twitter_logo_blue.png.twimg.768.png")

        
        try:
            if len(embed.fields) == 0:
                embed.add_field(name='\u200b', value=f"**No new followers.**", inline=False)
                await channel.send(embed=embed)
            else:
                await channel.send(embed=embed)
        except Exception as e:
            print(e)

        conn.close()

    except Exception as e:
        if '429' in str(e):
            channel = bot.get_channel(900513205254783006)
            print("rate limit")
            time.sleep(20)
            conn.close()
        
  
@get_following.before_loop
async def before_get_following():
    print('waiting...')
    await bot.wait_until_ready()


get_following.start()
poll.start()
bot.run(TOKEN)



