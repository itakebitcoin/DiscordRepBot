import discord
from discord import app_commands
import json
from utils import ensure_ratings_file_exists

async def review(interaction: discord.Interaction, user: discord.Member, good_transaction: bool, comment: str, target_channel_id, ratings_file):
    if interaction.channel_id != target_channel_id:
        await interaction.response.send_message("This command can only be used in the target channel.", ephemeral=True)
        return  # Ignore commands from other channels

    if interaction.user == user:
        await interaction.response.send_message("You can't rate yourself!", ephemeral=True)
        return

    # Calculate reputation change
    rep_change = 1 if good_transaction else -1

    # Store the rating
    ensure_ratings_file_exists(ratings_file)
    with open(ratings_file, 'r') as file:
        ratings = json.load(file)

    if str(user.id) not in ratings:
        ratings[str(user.id)] = {"rep": 0, "reviews": []}

    ratings[str(user.id)]["rep"] += rep_change
    ratings[str(user.id)]["reviews"].append({
        'author': str(interaction.user.id),
        'good_transaction': good_transaction,
        'comment': comment,
        'timestamp': interaction.created_at.strftime('%Y-%m-%d')  # Format the timestamp to only include the date
    })

    with open(ratings_file, 'w') as file:
        json.dump(ratings, file)

    await interaction.response.send_message(f'Review submitted! {user.mention} now has {ratings[str(user.id)]["rep"]} rep.', ephemeral=True)

async def ratings(interaction: discord.Interaction, user: discord.Member, ratings_file):
    # Load the ratings from the file
    ensure_ratings_file_exists(ratings_file)
    with open(ratings_file, 'r') as file:
        ratings = json.load(file)

    user_ratings = ratings.get(str(user.id), {"rep": 0, "reviews": []})

    response_message = f"{user.mention} has {user_ratings['rep']} rep."

    await interaction.response.send_message(response_message, ephemeral=True)