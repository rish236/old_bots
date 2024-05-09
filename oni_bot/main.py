import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import utils
import random as r
from discord.ext.commands import has_permissions, MissingPermissions
import psycopg2
import config
import psycopg2
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from collections import Counter

TOKEN = config.oni_token #discord token

bot = commands.Bot(command_prefix='!')
slash = SlashCommand(bot, sync_commands=True)

#initial event
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!!')

#connect to pg database
def connect_pg():
    try:
        conn = psycopg2.connect(
                        host="localhost",
                        database=config.database,
                        user=config.user,
                        password=config.password)
        conn.autocommit = True
        
    except Exception as e:
        print("Unable to connect to the database. Please try again later.")
        
    return conn

#helper method to get user's team role
def get_common_role(ctx):
    try:
        void_role = discord.utils.get(ctx.guild.roles, id=976979763610660949) #change the ids here if the team roles change
        fire_role = discord.utils.get(ctx.guild.roles, id=976975408434118747)
        air_role = discord.utils.get(ctx.guild.roles, id=976979754651635752)
        water_role = discord.utils.get(ctx.guild.roles, id=976979748771201104)
        earth_role = discord.utils.get(ctx.guild.roles, id=976979770174763048)

        element_roles = [void_role, fire_role, air_role, water_role, earth_role]

        common = list(set(element_roles).intersection(ctx.author.roles))

        if common and len(common) == 1:
            team = common[0]
        else:
            team = None
    except Exception as e:
        print(e)
        team = None
    
    return team

@commands.cooldown(1, 86400, commands.BucketType.user) #user can use the command once every 24 hours (86400 seconds)
@bot.command(name="boo",pass_context=True)
async def boo(ctx):
    if ctx.channel.id != 930035995640987649: #change id here if the channel for !boo changes (just find and replace all instances of a channel/role id when needed)
        return
    #connect to db
    conn = connect_pg()
    cur = conn.cursor()

    try:
        #grab username/id
        username = ctx.author
        user_id = ctx.author.id
        
        team = get_common_role(ctx)
        points = 0
              
        oni_role = discord.utils.get(ctx.guild.roles, id=928221277800513546) #change ids here if any of these roles change
        scholar_role = discord.utils.get(ctx.guild.roles, id=980973650251513886)
        
        #check and assign points based on role
        if scholar_role in ctx.author.roles:
            points += 15
        if oni_role in ctx.author.roles:
            points += r.choice([3,4])
        else:
            points += r.choice([1,2])


        cur.execute(f"""INSERT INTO "users" (username, user_id, points, team) VALUES('{username}','{user_id}', {points}, '{team}') ON CONFLICT (user_id) DO UPDATE SET points = users.points + {points}, ts = now() at time zone 'utc'""")

        message_dict = {1:(f"spooked a fellow Oni, they gave {points} ᛋTsuki Runes","oni1.png"),
                        2:(f"visited the Oni Mansion, receive {points} ᛋTsukiRunes","house.png"),
                        3:(f"Trick or Treat! Collect {points} ᛋTsukiRunes","door.png"),
                        4:(f"assembled the squad, earn {points} ᛋTsukiRunes","oni3.png"),
                        5:(f"haunted a fren, you got {points} ᛋTsukiRunes","oni2.png")
        }
        x = r.randint(1,5)
        
        filename = message_dict[x][1]
        emb = discord.Embed(title=f"\u200b", description=f"**{username}** {message_dict[x][0]}")

        img_file = discord.File(f"/home/rish/onisquad_bot/{filename}", filename=filename)
        emb.set_thumbnail(url=f"attachment://{filename}")
        await ctx.send(embed=emb, file=img_file)

    except Exception as e:
        print(e)

    conn.close()


@bot.command(name="water",pass_context=True, aliases=['plant', 'mine', 'moon'])
async def water(ctx):
    #                   harvest            mine               moon    
    channel_list = [981616145318694922,981616250474086480,981616280446599199]
    if ctx.channel.id not in channel_list:
        return

    user_id = ctx.author.id
    username = ctx.author

    moon_types = ["wolf", "snow", "worm", "pink", "flower", "strawberry", "buck", "sturgeon", "harvest", "hunter", "beaver", "cold"]
    moon_type = r.choice(moon_types)
    item_dict = {
            1:(["Shooting season has ended, time to cut a bamboo", "Bamboo clumps are flourishing, pruning time has arrived", "From shoot, to clum, to cane, to harvest", "Your bamboo garden is particularly flourishing", "Manami admires the bamboo plant for its pliable, yet sturdy composition"], "bamboo.png"),
            2:(["Fertilize your bonsai, it's thriving", "Trim your bonsai, it's thriving", "As you prune your bonsai, you marvel at its lush foliage and delicate branches", "You feel at peace carefully tending to your bonsai's flowering branches", "Satsuki once read that bonsais can pass down their magical energies from generation to generation"], "bonsai.png"),
            3:(["Fertilize the sakura, a bud starts to flower", "It's spring, and a sakura flower blossoms", "Pink-petaled cherry blossoms flutter and dance around you...", "Is anything more resplendent than spring's cherry blossom symphony?", "Clara's favorite flower is elegant and beautiful, but tragically fleeting"], "sakura.png"),
            4:(["Your planted seeds have grown, harvest a shiso leaf", "Fertilize the garden, a shiso leaf starts to sprout", "Sow your seeds and harvest a shiso leaf", "Weeding helps a shiso to germinate", "The shiso is sprouting, trim a leaf"],"shisho.png"),
            5:(["Weeding helps a wasabi to germinate", "Fertilize the garden, a wasabi starts to grow", "Your planted seeds have grown, harvest a wasabi"], "wasabi.png"),
            6:(["Yuzus are sprouting, harvest a fruit", "Sow your seeds and harvest a yuzu", "Fertilize the garden, a yuzu is ripe", "Weeding helps a yuzu to germinate", "Yuzu fruits are popular among the conservatory students for basic potions and as a citrus garnish"], "yuzu.png"),
            7:([f"**{username}** went digging and found a rare pyrite"],"pyrite.png"),
            8:([f"**{username}** went diving and discovered a lustrous pearl"],"pearl.png"),
            9:([f"**{username}** went digging and uncovered a gemstone quality amethyst"],"amethyst.png"),
            10:([f"**{username}** went digging and found a high-quality calcite"],"Calcite.png"),
            11:([f"**{username}** unearthed an imperial jade"],"jade.png"),
            12:([f"**{username}** went digging and discovered a radiant clear quartz"],"quartz.png"),
            13:(["Take action on this first quarter moon"],"Firstquarter.png"),
            14:([f"It's time to harvest the fruits of your labor during this {moon_type} moon"],f"{moon_type}.png"),
            15:(["This lunar eclipse is a blood moon and will cause cosmic chaos", "This lunar eclipse is a blood moon and will cause cosmic chaos", "This lunar eclipse is a blood moon and will cause cosmic chaos", "This lunar eclipse is a blood moon and will cause cosmic chaos"],"lunareclipse.png"),
            16:(["It's a new moon, new beginnings!"],"newmoon.png"),
            17:(["It's time to harvest the fruits of your labor during this super moon"],"Supermoon.png"),
            18:(["Clear out what no longer serves you during the third quarter"],"thirdquarter.png"),
            19:(["Intense energy arises from this total eclipse", "Intense energy arises from this total eclipse", "Intense energy arises from this total eclipse", "Intense energy arises from this total eclipse"],"Totaleclipse.png"),
            20:(["Reflect and rest during the last cycle of the moon"],"Waningcrescent.png"),
            21:(["As the light of the moon wanes, express gratitude for mother nature and reap the fruits of your labor"], "Waninggibbous.png"),
            22:(["Start setting your intentions during this waxing crescent night"],"waxingcrescent.png"),
            23:(["Take your final steps during this waxing gibbous evening"],"waxinggibbous.png")
        }

    conn = connect_pg()
    cur = conn.cursor()
    if (ctx.channel.id == 981616145318694922 and ctx.invoked_with == "water") or (ctx.channel.id == 981616145318694922 and ctx.invoked_with == "plant"):
        
        rand_item = r.choices(list(item_dict.keys())[:6], weights=(5, 5, 5, 5, 3, 5))[0]

    elif ctx.channel.id == 981616250474086480 and ctx.invoked_with == "mine":
        rand_item = r.choice(list(item_dict.keys())[6:12])
    
    elif ctx.channel.id == 981616280446599199 and ctx.invoked_with == "moon":
        try:
            cur.execute(f"""SELECT points FROM "users" where user_id='{user_id}'""")
            prev_points = cur.fetchone()[0]
        except Exception as e:
            prev_points = 0

        if prev_points <= 150:
            rand_item = r.choices(list(item_dict.keys())[12:23], weights=(1, 12, 0, 1, 1, 1, 0, 1, 1, 1, 1))[0]
        else:
            rand_item = r.choices(list(item_dict.keys())[12:23], weights=(1, 12, 4, 1, 1, 1, 4, 1, 1, 1, 1))[0]

    try:
        username = ctx.author
        user_id = ctx.author.id
                
        team = get_common_role(ctx)
        cur.execute(f"""INSERT INTO "users" (username, user_id, points, team) VALUES('{username}','{user_id}', 0, '{team}') ON CONFLICT (user_id) DO NOTHING""")
        cur.execute(f"""INSERT INTO "inventory" (user_id, item_id) VALUES('{user_id}','{rand_item}')""")

        img_name = item_dict[rand_item][1]
        img_file = discord.File(f"/home/rish/onisquad_bot/{img_name}", filename=img_name)

        emb = discord.Embed(title=f"\u200b", description=f"{r.choice(item_dict[rand_item][0])}").set_thumbnail(url=f"attachment://{img_name}")
        await ctx.send(embed=emb, file=img_file)

        
    except Exception as e:
        print(e)

    conn.close()


@commands.cooldown(1, 86400, commands.BucketType.user)
@bot.command(name="shokan",pass_context=True)
async def shokan(ctx):
    if ctx.channel.id != 981616308598738964:
        return
    user_id = ctx.author.id
    username = ctx.author
    conn = connect_pg()     
    cur = conn.cursor()


    try:
        cur.execute(f"""SELECT id,item_id from "inventory" where user_id = '{user_id}'""")

        res = set([row for row in cur.fetchall()])

        items_list = [x[1] for x in res]
        id_list = [y[0] for y in res]
     
        if len(items_list) < 3:
            emb = discord.Embed(title=f"\u200b", description=f"You need a crop, a mineral, and moonlight to summon. Go quest now.")
            await ctx.send(embed=emb)
            conn.close()
            return

        harvest = False
        mine = False
        moon = False

        for i,_ in enumerate(items_list):
            if harvest == True and mine == True and moon == True:
                break
            if 1 <= _ <= 6:
                harvest = True
                harvest_item = _
                harvest_id = id_list[i]
            if 7 <= _ <= 12:
                mine = True
                mine_item = _
                mine_id = id_list[i]
            if 13 <= _ <= 23:
                moon = True
                moon_item = _
                moon_id = id_list[i]
        

        if harvest == True and mine == True and moon == True:
            final_ids = (harvest_id, mine_id, moon_id)

            moon_dict = {
                13:(f"**{username}** crafted a potion during the first quarter, earn 5 ᛋTsukiRunes.", 5, "Rune_void.png"),
                14:(f"**{username}'s** inscribed ema has been received by the Kami Gods under the full moon, gain 10 ᛋTsukiRunes.", 10, "Rune_wind.png"),
                15:(f"Something bad is happening during this lunar eclipse, a blood moon has appeared. Lose 10 ᛋTsukiRunes.", -10, "Rune_earth.png"),
                16:(f"**{username}** performed a bokusen divination ritual during the new moon, accept 5 ᛋTsukiRunes.", 5, "Rune_earth.png"),
                17:(f"**{username}** harnessed the energy of the super full moon to make an offering and received a great blessing (大吉) omikuji, secure 15 ᛋTsukiRunes.", 15, "Rune_earth.png"),
                18:(f"**{username}** created an ofuda for protection during this third quarter, collect 5 ᛋTsukiRunes.", 5, "Rune_void.png"),
                19:(f"A spell has gone awry from the chaotic energy of the eclipse. 10 ᛋTsukiRunes squandered.", -10, "Rune_wind.png"),
                20:(f"**{username}** performed a kagura dance during this waning crescent. Acquire 5 ᛋTsukiRunes.", 5, "Rune_water.png"),
                21:(f"**{username}** performed a misogi purification ritual during the waning gibbous, get 5 ᛋTsukiRunes.", 5, "Rune_fire.png"),
                22:(f"**{username}** received a takusen oracle during the waxing crescent, get 5 ᛋTsukiRunes.", 5, "Rune_fire.png"), 
                23:(f"**{username}** crafted an elixir, receive 5 ᛋTsukiRunes.", 5, "Rune_water.png")
            }

            points = moon_dict[moon_item][1]

            if mine_item == 7 or harvest_item == 5:
                points += 2

            team = get_common_role(ctx)

            cur.execute(f"""INSERT INTO "users" (username, user_id, points, team) VALUES('{username}','{user_id}', {points}, '{team}') ON CONFLICT (user_id) DO UPDATE SET points = users.points + {points}, ts = now() at time zone 'utc'""")
            cur.execute(f""" DELETE FROM "inventory" where id in {final_ids}""")

            if mine_item == 7:
                img_name = "Rune_fire.png"
                img_file = discord.File(f"/home/rish/onisquad_bot/{img_name}", filename=img_name)
                emb = discord.Embed(title=f"\u200b", description=f"Your rare pyrite granted a bonus of {points} ᛋTsukiRunes.").set_thumbnail(url=f"attachment://{img_name}")
                await ctx.send(embed=emb, file=img_file)


            elif harvest_item ==5:
                img_name = "Rune_void.png"
                img_file = discord.File(f"/home/rish/onisquad_bot/{img_name}", filename=img_name)
                emb = discord.Embed(title=f"\u200b", description=f"Your harvested wasabi awarded a bonus of {points} ᛋTsukiRunes.").set_thumbnail(url=f"attachment://{img_name}")
                await ctx.send(embed=emb, file=img_file)

            else:
                img_name = moon_dict[moon_item][2]
                img_file = discord.File(f"/home/rish/onisquad_bot/{img_name}", filename=img_name)

                emb = discord.Embed(title=f"\u200b", description=f"{moon_dict[moon_item][0]}").set_thumbnail(url=f"attachment://{img_name}")
                await ctx.send(embed=emb, file=img_file)

            
        else:
            emb = discord.Embed(title=f"\u200b", description=f"You need a crop, a mineral, and moonlight to summon. Go quest now.")
            await ctx.send(embed=emb)


    except Exception as e:
        print(e)
        
    conn.close()


@bot.command(name="tally",pass_context=True)
async def tally(ctx):
    if ctx.channel.id != 981616585632514078:
        return

    conn = connect_pg()
    cur = conn.cursor()

    try:

        user_id = ctx.author.id
        cur.execute(f"""SELECT points,rank FROM (SELECT *, RANK() OVER(ORDER BY points DESC) as rank FROM users) ranks WHERE user_id = '{user_id}';""")

        res = cur.fetchone()
        print(res)
        points = res[0]
        rank = res[1]
        emb = discord.Embed(title=f"\u200b", description=f"Your ᛋTsukiRune balance is ***{points}***, and you are rank ***#{rank}***")
        img_file = discord.File(f"/home/rish/onisquad_bot/tsuki.png", filename="tsuki.png")
        emb.set_thumbnail(url="attachment://tsuki.png")
        await ctx.send(embed=emb, file=img_file)
    except Exception as e:
        emb = discord.Embed(title=f"\u200b", description=f"Unable to retrieve your ᛋTsukiRune balance. Please try again later.")
        await ctx.send(embed=emb)
        print(e)
    

    conn.close()

@bot.command(name="classrank",pass_context=True)
async def classrank(ctx):
    if ctx.channel.id != 981616585632514078:
        return

    conn = connect_pg()
    cur = conn.cursor()

    try:
        cur.execute("""SELECT username, points from (SELECT *, dense_rank() OVER (ORDER BY points DESC) as rank_number FROM "users") subquery WHERE rank_number<=10;""")
        res = cur.fetchall()

        emb = discord.Embed(title="**Class Rank**", description="")
        for i,_ in enumerate(res): 
            emb.add_field(name='\u200b', value=f"{i+1}) **{_[0]}** | **{_[1]}** ᛋTsukiRunes", inline=False)
        
        img_file = discord.File(f"/home/rish/onisquad_bot/topten.png", filename="topten.png")
        emb.set_thumbnail(url="attachment://topten.png")
        await ctx.send(embed=emb, file=img_file)

    except Exception as e:
        emb = discord.Embed(title=f"\u200b", description=f"Unable to retrieve Class Rank. Please try again later.")
        await ctx.send(embed=emb)
        print(e)

    conn.close()

@bot.command(name="essence",pass_context=True)
async def essence(ctx):
    if ctx.channel.id != 981616585632514078:
        return

    conn = connect_pg()
    cur = conn.cursor()

    try:
        user_id = ctx.author.id
        cur.execute(f"SELECT name FROM items INNER JOIN inventory ON inventory.item_id = items.id where user_id = '{user_id}';")
        res = [row[0] for row in cur.fetchall()]
        counter = Counter(res).items()
        final_items = ["%s : **%s**" % x for x in counter]

        if len(res) == 0:
            img_file = discord.File(f"/home/rish/onisquad_bot/inventory.png", filename="inventory.png")
            emb = discord.Embed(title=f" Essence Inventory", description=f"You don't have any essence yet. Go quest now!").set_thumbnail(url=f"attachment://inventory.png")
            await ctx.send(embed=emb, file=img_file)    
            conn.close()
            return

        final_items = '\n'.join(final_items) 
        img_file = discord.File(f"/home/rish/onisquad_bot/inventory.png", filename="inventory.png")
        emb = discord.Embed(title=f"Essence Inventory", description=f"{final_items}").set_thumbnail(url=f"attachment://inventory.png")
        await ctx.send(embed=emb, file=img_file)
        
    except Exception as e:
        emb = discord.Embed(title=f"\u200b", description=f"Unable to retrieve your inventory. Please try again later.")
        await ctx.send(embed=emb)
        print(e)

    conn.close()

@bot.command(name="elements",pass_context=True)
async def elements(ctx):
    if ctx.channel.id != 981616585632514078:
        return

    conn = connect_pg()
    cur = conn.cursor()

    try:
        cur.execute("""SELECT SUM(points), team FROM "users" GROUP BY team;""")
        res = cur.fetchall()
        fire_points = 0
        water_points = 0
        earth_points = 0
        air_points = 0
        void_points = 0
    
        for _ in res: 
            if 'Fire' in _:
                fire_points = _[0]
    
            if 'Void' in _:
                void_points = _[0]
    
            if 'Wind' in _:
                air_points = _[0]
 
            if 'Earth' in _:
                earth_points = _[0]
      
            if 'Water' in _:
                water_points = _[0]

        emb = discord.Embed(title="**Elements House Tally**", description=f"**Fire** | **{fire_points}** ᛋTsukiRunes\n**Water** | **{water_points}** ᛋTsukiRunes\n**Earth** | **{earth_points}** ᛋTsukiRunes\n**Wind** | **{air_points}** ᛋTsukiRunes\n**Void** | **{void_points}** ᛋTsukiRunes\n")
        img_file = discord.File(f"/home/rish/onisquad_bot/elements.png", filename="elements.png")
        emb.set_thumbnail(url="attachment://elements.png")
        await ctx.send(embed=emb, file=img_file)

    except Exception as e:
        emb = discord.Embed(title=f"\u200b", description=f"Unable to retrieve Elements House Tally. Please try again later.")
        await ctx.send(embed=emb)
        print(e)

    conn.close()


@slash.slash(
    name='addrunes',
    description='Add runes to a user.',
    guild_ids=[780942381326925874, 980004526520164352], 
    options=[
        create_option(name="user_id", description="Enter the user's ID. (not their username)", required=True, option_type=3),
        create_option(name="runes", description="Enter the amount of runes you want to add.", required=True, option_type=4),
        ]
)
@has_permissions(administrator=True)
async def add_runes(ctx:SlashContext, user_id:str, runes:int):
    conn = connect_pg()
    cur = conn.cursor()

    try:
        cur.execute(f"""UPDATE "users" SET points = points + {runes} WHERE user_id = '{user_id}' RETURNING points""")
        points = cur.fetchone()[0]

        emb = discord.Embed(title=f"\u200b", description=f"ᛋTsuki Runes successfully updated. The user now has **{points}** ᛋTsuki Runes")
        await ctx.send(embed=emb)

    except TypeError as e:
        print(e)
        emb = discord.Embed(title=f"\u200b", description=f"Unable to find user. Please try again.")
        await ctx.send(embed=emb)
    

@add_runes.error
async def add_runes_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("**You do not have permission to use this command**")



@boo.error
async def boo_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        seconds = int(error.retry_after)
        print(seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        em = discord.Embed(title=f"You can only use !boo once every 24 hours.",description=f"Try again after {h}h {m}m {s}s")
        await ctx.send(embed=em)


@shokan.error
async def shokan_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        seconds = int(error.retry_after)
        print(seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        em = discord.Embed(title=f"You can only use !shokan once every 24 hours.",description=f"Try again after {h}h {m}m {s}s")
        await ctx.send(embed=em)

bot.run(TOKEN)

