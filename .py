import discord
from discord.ext import commands
import json
from flask import Flask
from threading import Thread

TOKEN ="MTM1MDU3NjkzMzI0NjYwMzI4NA.GU6nWM.4FLSttOLK6Q7MXafkKb3p90_Sf6OCtxN3iZoMw"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Flask server to keep bot alive
app = Flask(__name__)


@app.route('/')
def home():
    return "✅ Bot is alive!"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# Load or initialize leaderboard data
try:
    with open("leaderboard.json", "r") as f:
        leaderboard = json.load(f)
except FileNotFoundError:
    leaderboard = {}


# Save leaderboard function
def save_leaderboard():
    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard, f)


# Tweet Panel View
class TweetView(discord.ui.View):

    def __init__(self, tweet_url):
        super().__init__()
        self.add_item(
            discord.ui.Button(label="🔁 Retweet (Bonus)",
                              url=tweet_url,
                              style=discord.ButtonStyle.link))

    @discord.ui.button(label="❤️ Like", style=discord.ButtonStyle.green)
    async def like_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        user = interaction.user
        leaderboard[user.name] = leaderboard.get(user.name, 0) + 100
        save_leaderboard()
        await interaction.response.send_message(
            f"{user.mention} liked the tweet! (+100 Points)", ephemeral=True)

    @discord.ui.button(label="💬 Comment", style=discord.ButtonStyle.blurple)
    async def comment_button(self, interaction: discord.Interaction,
                             button: discord.ui.Button):
        user = interaction.user
        leaderboard[user.name] = leaderboard.get(user.name, 0) + 100
        save_leaderboard()
        await interaction.response.send_message(
            f"{user.mention} commented on the tweet! (+100 Points)",
            ephemeral=True)


# Tweet Command
@bot.command()
async def tweet(ctx, tweet_link: str):
    view = TweetView(tweet_link)
    message = await ctx.send(f"🚀 **Engage with this tweet!** 🚀\n{tweet_link}",
                             view=view)
    await message.reply("@everyone")


# Leaderboard Command
@bot.command()
async def leaderboard(ctx):
    sorted_leaderboard = sorted(leaderboard.items(),
                                key=lambda x: x[1],
                                reverse=True)
    if not sorted_leaderboard:
        await ctx.send(
            "🏆 **Leaderboard is empty! Start engaging to earn points.** 🏆")
        return

    message = "🏆 **Leaderboard** 🏆\n\n"
    for rank, (user, points) in enumerate(sorted_leaderboard, start=1):
        message += f"**{rank}. {user}** - {points} Points\n"
    msg = await ctx.send(f"{message}")
    await msg.reply("@everyone")


# Reset Leaderboard Command
@bot.command()
async def reset_leaderboard(ctx):
    global leaderboard
    leaderboard = {}
    save_leaderboard()
    msg = await ctx.send("🔄 **Leaderboard has been reset!** 🔄")
    await msg.reply("@everyone")


# Keep bot alive
keep_alive()

bot.run(TOKEN)
