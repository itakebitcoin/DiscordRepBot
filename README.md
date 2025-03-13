# Discord Rep Bot

Discord Rep Bot. This bot is meant to serve as a way for people to review one another after transactions, affecting their reputation based on the reviews.

## Prerequisites

- Python 3.8 or higher
- `discord.py` library
- `discord-py-interactions` library

## Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/BAGOReview.git
cd BAGOReview
```

2. Create a virtual environment and activate it:

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required libraries:

```sh
pip install -r requirements.txt
```

## Configuration

Create a `config.json` file in the root directory of the project with the following content:

```json
{
    "bot_token": "YOUR_BOT_TOKEN",
    "target_channel_id": 1074172277828100126,
    "ratings_file": "ratings.json"
}
```

Replace `YOUR_BOT_TOKEN` with your actual Discord bot token and `1074172277828100126` with the ID of the target channel where the bot will listen for commands.

## Running the Bot

To run the bot, execute the following command:

```sh
python bagoreview.py
```

## Usage

The bot provides the following commands:

### `/review @user good_transaction: true or false comment:`

Submit a review for a user. The `good_transaction` should be `true` or `false`, and `comment` is a string containing the review comment. If the transaction is good, the user gains +1 rep; if bad, the user loses -1 rep.

### `/ratings @user`

View a user's total reputation. This command will display the total rep for the specified user.

### Example

```sh
/review @JohnDoe good_transaction: true comment: "Great job!"
/ratings @JohnDoe
```

## Project Structure

```
BAGOReview/
├── bagoreview.py
├── commands.py
├── config.json
├── requirements.txt
└── utils.py
```

### `bagoreview.py`

The main script that initializes the bot, loads the configuration, and defines the commands.

```python
import discord
from discord.ext import commands
from discord import app_commands
from utils import load_config, ensure_ratings_file_exists
from commands import review, ratings

# Load configuration from config.json
config = load_config()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)
tree = app_commands.CommandTree(bot)

TARGET_CHANNEL_ID = config['target_channel_id']
RATINGS_FILE = config['ratings_file']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await tree.sync()
    # Create the ratings file if it doesn't exist
    ensure_ratings_file_exists(RATINGS_FILE)

@tree.command(name="review", description="Submit a review")
async def review_command(interaction: discord.Interaction, user: discord.Member, good_transaction: bool, comment: str):
    await review(interaction, user, good_transaction, comment, TARGET_CHANNEL_ID, RATINGS_FILE)

@tree.command(name="ratings", description="View a user's ratings and comments")
async def ratings_command(interaction: discord.Interaction, user: discord.Member):
    await ratings(interaction, user, RATINGS_FILE)

bot.run(config['bot_token'])
```

### `commands.py`

Contains the command handler functions for the bot.

```python
import discord
from discord import app_commands
import json
from utils import ensure_ratings_file_exists

async def review(interaction: discord.Interaction, user: discord.Member, good_transaction: bool, comment: str, target_channel_id, ratings_file):
    if interaction.channel_id != target_channel_id:
        embed = discord.Embed(description="This command can only be used in the target channel.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return  # Ignore commands from other channels

    if interaction.user == user:
        embed = discord.Embed(description="You can't rate yourself!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
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

    # Assign roles based on reputation
    rep = ratings[str(user.id)]["rep"]
    role_name = f'{rep} Rep'
    role = discord.utils.get(interaction.guild.roles, name=role_name)

    if role is None:
        role = await interaction.guild.create_role(name=role_name)

    await user.add_roles(role)

    embed = discord.Embed(description=f'Review submitted! {user.mention} now has {rep} rep and has been assigned the role {role_name}.', color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def ratings(interaction: discord.Interaction, user: discord.Member, ratings_file):
    # Load the ratings from the file
    ensure_ratings_file_exists(ratings_file)
    with open(ratings_file, 'r') as file:
        ratings = json.load(file)

    user_ratings = ratings.get(str(user.id), {"rep": 0, "reviews": []})

    embed = discord.Embed(title=f"Ratings for {user.display_name}", color=discord.Color.blue())
    embed.add_field(name="Total Rep", value=user_ratings["rep"], inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)
```

### `config.json`

The configuration file that contains the bot token, target channel ID, and the name of the ratings file.

```json
{
    "bot_token": "YOUR_BOT_TOKEN",
    "target_channel_id": 1074172277828100126,
    "ratings_file": "ratings.json"
}
```

### `requirements.txt`

Lists all the dependencies required for the project.

```
discord.py
discord-py-interactions
```

### `utils.py`

Utility functions for loading configuration and handling file operations.

```python
import json
import os

def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

def ensure_ratings_file_exists(ratings_file):
    if not os.path.exists(ratings_file):
        with open(ratings_file, 'w') as file:
            json.dump({}, file)
```

## License

This project is licensed under the MIT License.

