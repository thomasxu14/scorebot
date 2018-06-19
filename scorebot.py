### Scoreboard bot. Python 3.5+

# Install the discord.py package with the command: 
# python3 -m pip install -U https://github.com/Rapptz/discord.py/archive/rewrite.zip
import discord
from discord.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import increment

# Loads the database and its tables. Initializes the database if it doesn't exist yet.
db = TinyDB('db.json')
users = db.table("users")
comments = db.table("comments")
results = db.table("results")

# Initializes the bot. Its commands are triggered by command_prefix.
bot = commands.Bot(command_prefix='!', description='A bot that counts wins and losses.')

token = "" ### INSERT BOT TOKEN HERE

color = 0x18e1be

@bot.event # What the bot prints in the console when it's ready.
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)
    print('Bot user ID:')
    print(bot.user.id)
    print('------')
    

@bot.command()
async def info(ctx): # Gives the different commands to call the bot.
    # Creates an embedded message, to which we add text fields.
    embed = discord.Embed(title="Bot Guide", description="Commands are called using the prefix '!'.", color=color)

    embed.add_field(name="!win", value=
            "Use this when you want to register a win against another player. The comment is optional.\nExample: *!win {0} Good bot.*"
            .format(bot.user.mention))
    embed.add_field(name="!loss", value="Use this when you want to register a loss. Same format as !win")
    embed.add_field(name="!stat", value="Use this to see a player's stat.\nExample: *!stat {0}*".format(bot.user.mention))

    await ctx.send(embed=embed)
    
@bot.command()
async def win(ctx, member: discord.Member, *, comment=None):
    # Catches bad use cases such as a comment that's too long, or a user playing against themselves.
    if comment is not None and len(comment) > 80:
        embed = discord.Embed(description="Your comment should be under 80 characters.", color=color)
        await ctx.send(embed = embed)     
    if member.id == ctx.author.id:
        embed = discord.Embed(description="You cannot play against yourself.", color=color)
        await ctx.send(embed=embed)
        
    else:
        author_id, author_name = str(ctx.author.id), ctx.author.name
        member_id, member_name = str(member.id), member.name
        User = Query()
        author_profile = users.get(User.id == author_id)
        if author_profile is None:
            users.insert({"id": author_id, "name": author_name, "wins": 0, "losses": 0})
        member_profile = users.get(User.id == member_id)
        if member_profile is None:
            users.insert({"id": member_id, "name": member_name, "wins": 0, "losses": 0})
            
        users.update(increment("wins"), User.id == author_id)
        users.update(increment("losses"), User.id == member_id)
        if comment is not None:
            comments.insert({"content": comment, "author_id": author_id, "member_id": member_id})
        
        Result = Query()
        match_up_res  = results.get(Result.player1 == author_id and Result.player2 == member_id)
        if match_up_res is None:
            results.insert({"player1": author_id, "player2": member_id, "player1wins": 0, "player2wins": 0})
            results.insert({"player1": member_id, "player2": author_id, "player1wins": 0, "player2wins": 0})
        results.update(increment("player1wins"), Result.player1 == author_id and Result.player2 == member_id)
        results.update(increment("player2wins"), Result.player1 == member_id and Result.player2 == author_id)
        member_profile = users.get(User.id == member_id)
        embed = discord.Embed(title="Result", description="{0} has won against {1}.\nHere is a quick summary for {1}:".format(ctx.author.mention, member.mention), color=color)
        embed.add_field(name="Overview", value="Wins: {0} | Losses: {1}".format(member_profile["wins"], member_profile["losses"]))
         
        match_up_res  = results.get(Result.player1 == author_id and Result.player2 == member_id)
        embed.add_field(name="Head-to-head matchup", value="You are currently {0}-{1} against {2}".format(match_up_res["player1wins"], match_up_res["player2wins"], member.mention))
        
        Comment = Query()
        member_last_comments = comments.search(Comment.member_id == member_id)[-5:]
        comment_string = "\n-".join([comment["content"] for comment in member_last_comments])
        if comment_string == "":
            comment_string = "No comment yet."
        embed.add_field(name="Last 5 comments", value="*-"+comment_string+"*")
        
        all_results = results.search(Result.player1 == member_id)
        nb_opponents = len(all_results)
        matched_played = member_profile["wins"] + member_profile["losses"]
        embed.add_field(name="Games played", value="{0} game(s) played against {1} user(s).".format(matched_played, nb_opponents))
        await ctx.send(embed = embed)
        
        
@bot.command()
async def loss(ctx, member: discord.Member, *, comment=None):
    
    if comment is not None and len(comment) > 80:
        embed = discord.Embed(description="Your comment should be under 80 characters!", color=color)
        await ctx.send(embed = embed)
        
    if member.id == ctx.author.id:
        embed = discord.Embed(description="You cannot play against yourself.", color=color)
        await ctx.send(embed=embed)
        
    else:
        author_id, author_name = str(ctx.author.id), ctx.author.name
        member_id, member_name = str(member.id), member.name
        User = Query()
        author_profile = users.get(User.id == author_id)
        if author_profile is None:
            users.insert({"id": author_id, "name": author_name, "wins": 0, "losses": 0})
        member_profile = users.get(User.id == member_id)
        if member_profile is None:
            users.insert({"id": member_id, "name": member_name, "wins": 0, "losses": 0})
            
        users.update(increment("losses"), User.id == author_id)
        users.update(increment("wins"), User.id == member_id)
        if comment is not None:
            comments.insert({"content": comment, "author_id": author_id, "member_id": member_id})
        
        Result = Query()
        match_up_res  = results.get(Result.player1 == author_id and Result.player2 == member_id)
        if match_up_res is None:
            results.insert({"player1": author_id, "player2": member_id, "player1wins": 0, "player2wins": 0})
            results.insert({"player1": member_id, "player2": author_id, "player1wins": 0, "player2wins": 0})
        results.update(increment("player2wins"), Result.player1 == author_id and Result.player2 == member_id)
        results.update(increment("player1wins"), Result.player1 == member_id and Result.player2 == author_id)
        member_profile = users.get(User.id == member_id)
        embed = discord.Embed(title="Result", description="{0} has lost against {1}.\nHere is a quick summary for {1}:".format(ctx.author.mention, member.mention), color=color)
        embed.add_field(name="Overview", value="Wins: {0} | Losses: {1}".format(member_profile["wins"], member_profile["losses"]))
        
        match_up_res  = results.get(Result.player1 == author_id and Result.player2 == member_id)
        embed.add_field(name="Head-to-head matchup", value="You are currently {0}-{1} against {2}".format(match_up_res["player1wins"], match_up_res["player2wins"], member.mention))
        
        Comment = Query()
        member_last_comments = comments.search(Comment.member_id == member_id)[-5:]
        comment_string = "\n-".join([comment["content"] for comment in member_last_comments])
        if comment_string == "":
            comment_string = "No comment yet."
        embed.add_field(name="Last 5 comments", value="*-"+comment_string+"*")
        
        all_results = results.search(Result.player1 == member_id)
        nb_opponents = len(all_results)
        matched_played = member_profile["wins"] + member_profile["losses"]
        embed.add_field(name="Games played", value="{0} game(s) played against {1} user(s).".format(matched_played, nb_opponents))
        await ctx.send(embed = embed)
        

@bot.command()
async def stat(ctx, member: discord.Member):
        
    member_id, member_name = str(member.id), member.name
    User = Query()
    member_profile = users.get(User.id == member_id)
    if member_profile is None:
        users.insert({"id": member_id, "name": member_name, "wins": 0, "losses": 0})
    
    Result = Query()
    member_profile = users.get(User.id == member_id)
    embed = discord.Embed(description="{0}'s profile: ".format(member.mention), color=color)
    embed.add_field(name="Overview", value="Wins: {0} | Losses: {1}".format(member_profile["wins"], member_profile["losses"]))
    
    if ctx.author.id != member.id:
        match_up_res  = results.get(Result.player1 == ctx.author.id and Result.player2 == member_id)
        if match_up_res is not None:
            match_up_res  = results.get(Result.player1 == ctx.author.id and Result.player2 == member_id)
            embed.add_field(name="Head-to-head matchup", value="You are currently {0}-{1} against {2}".format(match_up_res["player1wins"], match_up_res["player2wins"], member.mention))
        
    Comment = Query()
    member_last_comments = comments.search(Comment.member_id == member_id)[-5:]
    comment_string = "\n-".join([comment["content"] for comment in member_last_comments])
    if comment_string == "":
        comment_string = "No comment yet."
    embed.add_field(name="Last 5 comments", value="*-"+comment_string+"*")
    
    all_results = results.search(Result.player1 == member_id)
    nb_opponents = len(all_results)
    matched_played = member_profile["wins"] + member_profile["losses"]
    embed.add_field(name="Games played", value="{0} game(s) played against {1} user(s).".format(matched_played, nb_opponents))
    await ctx.send(embed = embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed = discord.Embed(description="Could not find that member. Correct format:\n!<command> <@membername> <comment>[for win or loss, optional]", color=color)
        await ctx.send(embed=embed)
    else:
        print(error)
    
    
bot.run(token)