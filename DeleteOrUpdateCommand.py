import discord
from discord import app_commands
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

# Remove a specific command
@bot.tree.command()
@app_commands.checks.has_permissions(administrator=True)
async def remove_command(interaction: discord.Interaction, command_name: str):
    command = bot.tree.get_command(command_name)
    if command:
        bot.tree.remove_command(command_name)
        await bot.tree.sync()
        await interaction.response.send_message(f"Command '{command_name}' has been removed.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Command '{command_name}' not found.", ephemeral=True)

# Update a command (example with create_ad)
@bot.tree.command(name="create_ad", description="Create a new advertisement (updated)")
@app_commands.checks.has_permissions(administrator=True)
async def create_ad(interaction: discord.Interaction):
    # Updated implementation
    await interaction.response.send_message("This is the updated create_ad command.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Command tree synced with Discord")

bot.run("Add_Your_Bot_Token") # Add your bot token

 
 # طريقة استخدام امر الحذف
 # /remove_command command_name:create_ad