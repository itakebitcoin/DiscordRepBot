import discord
from discord.ext import commands
from discord import app_commands
from utils import load_config, ensure_ratings_file_exists, get_user_reputation
from commands import review, ratings

# Load configuration from config.json
config = load_config()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

TARGET_CHANNEL_ID = config['target_channel_id']
RATINGS_FILE = config['ratings_file']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()  # Use the existing command tree
    # Create the ratings file if it doesn't exist
    ensure_ratings_file_exists(RATINGS_FILE)

@bot.tree.command(name="review", description="Submit a review")
async def review_command(interaction: discord.Interaction, user: discord.Member, good_transaction: bool, comment: str):
    await review(interaction, user, good_transaction, comment, TARGET_CHANNEL_ID, RATINGS_FILE)
    
    # Get the user's total reputation
    user_reputation, _ = get_user_reputation(user.id, RATINGS_FILE)
    
    # Create an embed for the review
    embed = discord.Embed(title="New Review", color=discord.Color.green() if good_transaction else discord.Color.red())
    embed.add_field(name="Reviewer", value=interaction.user.mention, inline=True)
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Comment", value=comment, inline=False)
    embed.set_footer(text=f"Good Transaction | Total Rep: {user_reputation}" if good_transaction else f"Bad Transaction | Total Rep: {user_reputation}")
    
    # Send the embed to the target channel
    target_channel = bot.get_channel(TARGET_CHANNEL_ID)
    await target_channel.send(embed=embed)

@bot.tree.command(name="ratings", description="View a user's ratings and comments")
async def ratings_command(interaction: discord.Interaction, user: discord.Member):
    user_reputation, comments = get_user_reputation(user.id, RATINGS_FILE)
    
    # Create an embed for the ratings
    embed = discord.Embed(title="User Ratings", color=discord.Color.blue())
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Total Reputation", value=user_reputation, inline=True)
    
    # Summarize comments
    comments_summary = "\n".join(comments) if comments else "No comments available."
    embed.add_field(name="Comments", value=comments_summary, inline=False)
    
    # Send the embed to the interaction channel
    await interaction.response.send_message(embed=embed)

bot.run(config['bot_token'])