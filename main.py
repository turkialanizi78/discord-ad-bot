import discord
from discord.ext import commands, tasks
from discord import ui
import math
import asyncio
import json
import io
import aiohttp
import logging
from datetime import datetime, timedelta
import random
from PIL import Image, ImageDraw, ImageFont
import base64
import re
from urllib.parse import urlparse
from PIL import Image
from discord import app_commands
 
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('discord_bot')

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

def random_pastel_color():
    return "#{:02X}{:02X}{:02X}".format(
        random.randint(127, 255),
        random.randint(127, 255),
        random.randint(127, 255)
    )

# Function to add a frame to an image
async def add_frame_to_image(image_bytes, color):
    logger.info(f"Adding frame to image with color: {color}")
    with Image.open(io.BytesIO(image_bytes)) as img:
        # Create a new image with padding for the frame
        frame_width = 10
        new_size = (img.width + 2*frame_width, img.height + 2*frame_width)
        framed_img = Image.new('RGBA', new_size, color)
        
        # Paste the original image onto the new image
        framed_img.paste(img, (frame_width, frame_width))
        
        # Save the framed image to a bytes object
        img_byte_arr = io.BytesIO()
        framed_img.save(img_byte_arr, format='PNG')
        logger.info("Image framed successfully")
        return img_byte_arr.getvalue()
    
# Function to extract URLs from text
def extract_urls(text):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

 
async def is_github_image_url(url):
    github_image_patterns = [
        r'https://github\.com/[^/]+/[^/]+/blob/[^/]+/.+\.(png|jpg|jpeg|gif|webp)',
        r'https://github\.com/[^/]+/[^/]+/raw/[^/]+/.+\.(png|jpg|jpeg|gif|webp)'
    ]
    return any(re.match(pattern, url) for pattern in github_image_patterns)

async def is_image_url(url):
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    return any(url.lower().endswith(ext) for ext in image_extensions) or '/raw/' in url

 


async def fetch_github_repo_info(url):
    # Extract owner and repo from GitHub URL
    match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
    if not match:
        return None
    
    owner, repo = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    user_url = f"https://api.github.com/users/{owner}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                repo_data = await response.json()
                
                # Fetch user info
                async with session.get(user_url) as user_response:
                    user_data = await user_response.json() if user_response.status == 200 else {}
                
                return {
                    'name': repo_data['name'],
                    'full_name': repo_data['full_name'],
                    'description': repo_data['description'],
                    'stars': repo_data['stargazers_count'],
                    'forks': repo_data['forks_count'],
                    'language': repo_data['language'],
                    'owner_name': user_data.get('name', owner),
                    'owner_avatar': user_data.get('avatar_url', ''),
                    'owner_bio': user_data.get('bio', ''),
                    'html_url': repo_data['html_url']
                }
    return None

async def get_github_image_urls(urls):
    image_urls = []
    for url in urls:
        if 'github.com' in url and '/raw/' in url:
            # The URL is already in the correct format for raw content
            image_urls.append(url)
        elif 'github.com' in url and '/blob/' in url:
            # Convert blob URLs to raw URLs
            raw_url = url.replace('/blob/', '/raw/')
            image_urls.append(raw_url)
    return image_urls


def get_youtube_video_id(url):
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    match = re.match(youtube_regex, url)
    return match.group(6) if match else None

async def create_ad_message(title, description, color, urls, image_files):
    formatted_message = f"**{title}**\n\n"
    formatted_message += f"{description}\n\n"
    
    youtube_url = None
    github_info = None
    image_urls = []   

    for url in urls:
        if video_id := get_youtube_video_id(url):
            youtube_url = url
            formatted_message += f"📺 **فيديو يوتيوب:** {url}\n\n"
        elif 'github.com' in url:
            if '/blob/' not in url and '/raw/' not in url:
                repo_info = await fetch_github_repo_info(url)
                if repo_info:
                    github_info = (
                        f"🐙 **مستودع GitHub**\n"
                        f"{repo_info['full_name']}: {repo_info['html_url']}\n"
                        f"{repo_info['description']}\n"
                        f"🌟 STARS: {repo_info['stars']} | 🍴 FORKS: {repo_info['forks']} | "
                        f"💻 LANGUAGE: {repo_info['language']}\n"
                        f"👤 **OWNER**: {repo_info['owner_name']}\n"
                        f"{repo_info['owner_bio']}\n\n"
                    )
                    formatted_message += github_info
        elif await is_image_url(url):
            image_urls.append(url)

    formatted_message += "تم الإنشاء بواسطة ❤️ Your !WWR"

    return formatted_message, youtube_url, image_urls


async def send_advertisement(bot, channel, title, details, color, image_files):
    logger.info(f"Starting to send advertisement: {title}")
    logger.info(f"Received color: {color}")
    
    urls = extract_urls(details)
    
    message_content, youtube_url, url_images = await create_ad_message(title, details, color, urls, image_files)

    files = []

    # معالجة الصور المرفقة والصور من الروابط
    all_images = image_files.copy()
    for url in url_images:
        logger.info(f"Downloading image from URL: {url}")
        image_data = await download_image(url)
        if image_data:
            all_images.append(image_data)
            logger.info(f"Successfully downloaded image from {url}")
        else:
            logger.warning(f"Failed to download image from {url}")

    for i, image_bytes in enumerate(all_images):
        if image_bytes:
            logger.info(f"Processing image {i+1}")
            try:
                framed_image_bytes = await add_frame_to_image(image_bytes, f"#{color:06x}")
                logger.info(f"Successfully framed image {i+1}")
                files.append(discord.File(io.BytesIO(framed_image_bytes), filename=f'framed_image{i}.png'))
            except Exception as e:
                logger.error(f"Error framing image {i+1}: {str(e)}")

    try:
        # إرسال الرسالة مع الصور المؤطرة
        ad_message = await channel.send(content=message_content, files=files)
        logger.info("Advertisement sent successfully")

    except Exception as e:
        logger.error(f"Error sending advertisement: {str(e)}")
        raise

 
     

    # إضافة ردود الفعل للتفاعل
    reactions = ["👍", "👎", "❤️", "🔥", "🎉"]
    for reaction in reactions:
        await ad_message.add_reaction(reaction)

    return ad_message



# Make sure to keep the download_image function:
async def download_image(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                logger.info(f"Attempting to download image from {url}. Status code: {response.status}")
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    logger.info(f"Content-Type for {url}: {content_type}")
                    if 'image' in content_type:
                        return await response.read()
                    else:
                        logger.warning(f"URL {url} does not point to an image. Content-Type: {content_type}")
                else:
                    logger.warning(f"Failed to download image from {url}. Status code: {response.status}")
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {str(e)}")
    return None

async def handle_reactions(bot, message, embeds):
    def check(reaction, user):
        return user != bot.user and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

    current_page = 0

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "➡️" and current_page < len(embeds) - 1:
                current_page += 1
                await message.edit(embed=embeds[current_page])
            elif str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=embeds[current_page])

            await message.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            break



class AdForm(ui.Modal, title='إنشاء إعلان'):
    ad_title = ui.TextInput(label='العنوان', placeholder='ضع عنوان الموضوع...')
    ad_details = ui.TextInput(label='الوصف', style=discord.TextStyle.paragraph, placeholder='أكتب الوصف والموضوع كاملا...')

    def __init__(self, bot, channel_id):
        super().__init__()
        self.bot = bot
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
   
        await interaction.followup.send("لقد تم استلام محتوى موضوعك. يرجى تحميل الصور لموضوعك الآن (حتى 10 صور)، أو اكتب 'تم' عند الانتهاء. اكتب 'تخطي' لنشر الموضوع بدون صور.", ephemeral=True)

        image_files = []
        
        while len(image_files) < 10:
            def check(m):
                return m.author == interaction.user and (m.attachments or m.content.lower() in ['تم', 'تخطي']) and m.channel == interaction.channel

            try:
                response = await self.bot.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                if not image_files:
                    await interaction.followup.send("لم يتم استلام أي صور خلال 60 ثانية. سيتم نشر الإعلان بدون صور.", ephemeral=True)
                break
            else:
                if response.content.lower() in ['تخطي', 'تم']:
                    break
                elif response.attachments:
                    for attachment in response.attachments:
                        image_bytes = await attachment.read()
                        image_files.append(image_bytes)
                    await interaction.followup.send(f"تم استلام {len(response.attachments)} صورة (صور). الإجمالي: {len(image_files)}. قم برفع المزيد أو اكتب 'تم'.", ephemeral=True)

        channel = self.bot.get_channel(self.channel_id)
        color = int(random_pastel_color()[1:], 16)
        logger.info(f"Generated color for advertisement: #{color:06x}")
        
        try:
            ad_message = await send_advertisement(self.bot, channel, self.ad_title.value, self.ad_details.value, color, image_files)
            await interaction.followup.send(f"تم إرسال الإعلان بنجاح إلى {channel.mention}! [عرض الإعلان]({ad_message.jump_url})", ephemeral=True)
        except discord.errors.Forbidden:
            await interaction.followup.send(f"فشل في إرسال الإعلان. يرجى التأكد من أن البوت لديه صلاحية إرسال الرسائل والمرفقات في {channel.mention}.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in AdForm submission: {str(e)}")
            await interaction.followup.send(f"حدث خطأ أثناء إرسال الإعلان: {str(e)}", ephemeral=True)

        # Удаление сообщений с ответами в приватном канале
        async for message in interaction.channel.history(limit=None, after=interaction.message):
            if message.author == interaction.user:
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass




class ScheduleForm(ui.Modal, title='جدولة الإعلان'):
    ad_title = ui.TextInput(label='العنوان', placeholder='أدخل عنوان الإعلان هنا...')
    ad_details = ui.TextInput(label='التفاصيل', style=discord.TextStyle.paragraph, placeholder='أدخل تفاصيل الإعلان هنا...')
    schedule_time = ui.TextInput(label='وقت الجدولة (YYYY-MM-DD HH:MM)', placeholder='اتركه فارغاً للإرسال بعد 10 ثوان', required=False)
    def __init__(self, channel_id):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Parse the scheduled time or set to 10 seconds from now if empty
        if self.schedule_time.value.strip():
            try:
                scheduled_time = datetime.strptime(self.schedule_time.value, "%Y-%m-%d %H:%M")
            except ValueError:
                await interaction.followup.send("صيغة التاريخ غير صحيحة. يرجى استخدام الصيغة YYYY-MM-DD HH:MM", ephemeral=True)
                return
        else:
            scheduled_time = datetime.now() + timedelta(seconds=10)

        # Ask for image attachments
        await interaction.followup.send("تم استلام محتوى إعلانك. يرجى رفع الصور لإعلانك الآن (حتى 10 صور)، أو اكتب 'تم' عند الانتهاء. اكتب 'تخطي' للنشر بدون صور.", ephemeral=True)
        
        image_files = []
        
        while len(image_files) < 10:
            def check(m):
                return m.author == interaction.user and (m.attachments or m.content.lower() in ['تم', 'تخطي']) and m.channel == interaction.channel

            try:
                response = await bot.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                if not image_files:
                    await interaction.followup.send("لم يتم استلام أي صور خلال 60 ثانية. سيتم جدولة الإعلان بدون صور.", ephemeral=True)
                break
            else:
                if response.content.lower() == 'تخطي':
                    break
                elif response.content.lower() == 'تم':
                    break
                elif response.attachments:
                    for attachment in response.attachments:
                        image_bytes = await attachment.read()
                        # Convert image bytes to base64 string for storage
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        image_files.append(image_base64)
                    await interaction.followup.send(f"تم استلام {len(response.attachments)} صورة (صور). الإجمالي: {len(image_files)}. قم برفع المزيد أو اكتب 'تم'.", ephemeral=True)

        # Schedule the advertisement
        ad_data = {
            'channel_id': self.channel_id,
            'title': self.ad_title.value,
            'details': self.ad_details.value,
            'images': image_files,
            'scheduled_time': scheduled_time.isoformat(),
            'color': random_pastel_color()
        }
        
        scheduled_ads.append(ad_data)
        save_scheduled_ads()

        await interaction.followup.send(f"تمت جدولة الإعلان بنجاح ليتم نشره في {scheduled_time.strftime('%Y-%m-%d %H:%M')}!", ephemeral=True)

        # Delete the response messages in the private channel
        async for message in interaction.channel.history(limit=None, after=interaction.message):
            if message.author == interaction.user:
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass

class ChannelPaginationView(ui.View):
    def __init__(self, bot, ctx, is_scheduling=False):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
        self.is_scheduling = is_scheduling
        self.current_page = 0
        self.channels = [channel for channel in ctx.guild.text_channels if channel.permissions_for(ctx.guild.me).send_messages]
        self.max_pages = math.ceil(len(self.channels) / 25)
        self.update_options()

    @ui.select(placeholder="قم بإختيار غرفة المحادثة", min_values=1, max_values=1)
    async def select_channel(self, interaction: discord.Interaction, select: ui.Select):
        channel_id = int(select.values[0])
        if self.is_scheduling:
            ad_form = ScheduleForm(self.bot, channel_id)
        else:
            ad_form = AdForm(self.bot, channel_id)
        await interaction.response.send_modal(ad_form)

    @ui.button(label="المجموعة السابقة", style=discord.ButtonStyle.gray)
    async def previous_button(self, interaction: discord.Interaction, button: ui.Button):
        self.current_page = max(0, self.current_page - 1)
        self.update_options()
        await interaction.response.edit_message(view=self)

    @ui.button(label="المجموعة التالية", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: ui.Button):
        self.current_page = min(self.max_pages - 1, self.current_page + 1)
        self.update_options()
        await interaction.response.edit_message(view=self)

    def update_options(self):
        start_idx = self.current_page * 25
        end_idx = start_idx + 25
        current_channels = self.channels[start_idx:end_idx]

        self.select_channel.options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in current_channels
        ]

        self.previous_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page == self.max_pages - 1)

# Define multiple authorized role IDs
AUTHORIZED_ROLE_IDS = [1164466837505970176,1251298120176898138, 1219669909366116463]  # Add more role IDs as needed 
def has_authorized_role():
    async def predicate(interaction: discord.Interaction):
        for role_id in AUTHORIZED_ROLE_IDS:
            role = interaction.guild.get_role(role_id)
            if role is not None and role in interaction.user.roles:
                return True
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return False
    return app_commands.check(predicate)

@bot.tree.command(name="create_ad", description="فتح واجهة لعمل اعلان او موضوع جديد ونشره")
@has_authorized_role()
async def create_ad(interaction: discord.Interaction):
    """فتح واجهة إنشاء الموضوع."""
    view = ChannelPaginationView(bot, interaction, is_scheduling=False)
    await interaction.response.send_message(
                   "إنشاء موضوع جديد:\n\n"
                   "1. اختر قناة من القائمة المنسدلة.\n"
                   "2. املأ العنوان والتفاصيل في النموذج الذي سيظهر.\n"
                   "3. بعد إرسال النموذج، ستتم مطالبتك بإرفاق صورة إذا رغبت في ذلك.\n"
                   "4. سيتم إرسال موضوعك إلى القناة المختارة!", 
                   view=view, ephemeral=True)
    
 
@create_ad.error
async def create_ad_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have the necessary permissions to use this command.", ephemeral=True)
    else:
        logger.error(f"An error occurred: {str(error)}")
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
    
# Global list to store scheduled advertisements
scheduled_ads = []

def save_scheduled_ads():
    with open('scheduled_ads.json', 'w') as f:
        json.dump(scheduled_ads, f, default=str)

def load_scheduled_ads():
    try:
        with open('scheduled_ads.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@tasks.loop(seconds=5)
async def check_scheduled_ads():
    current_time = datetime.now()
    ads_to_remove = []

    for ad in scheduled_ads:
        scheduled_time = datetime.fromisoformat(ad['scheduled_time'])
        if current_time >= scheduled_time:
            channel = bot.get_channel(int(ad['channel_id']))
            if channel:
                color = ad['color']
                embed = discord.Embed(title=ad['title'], description=ad['details'], color=int(color[1:], 16))
                
                if ad['images']:
                    # Process and send images
                    for i, image_data in enumerate(ad['images']):
                        try:
                            # Check if image_data is a dictionary or a string
                            if isinstance(image_data, dict):
                                image_base64 = image_data.get('bytes', '')
                            else:
                                image_base64 = image_data

                            image_bytes = base64.b64decode(image_base64)
                            framed_image_bytes = await add_frame_to_image(image_bytes, color)
                            file = discord.File(io.BytesIO(framed_image_bytes), filename=f'image_{i+1}.png')
                            
                            if i == 0:
                                # Send the first image with the embed
                                message = await channel.send(file=file, embed=embed)
                                embed.set_image(url=message.attachments[0].url)
                            else:
                                # Send additional images and add them to the embed
                                image_message = await channel.send(file=file)
                                embed.add_field(name=f'Image {i+1}', value=f'[View]({image_message.attachments[0].url})', inline=True)
                        except Exception as e:
                            logger.error(f"Error processing image {i+1} for ad '{ad['title']}': {str(e)}")
                            continue
                    
                    # Edit the original message to include links to all images
                    if 'message' in locals():
                        await message.edit(embed=embed)
                else:
                    await channel.send(embed=embed)
                
                logger.info(f"Scheduled advertisement posted: {ad['title']}")
            else:
                logger.error(f"Failed to post scheduled advertisement. Channel not found: {ad['channel_id']}")
            
            ads_to_remove.append(ad)

    for ad in ads_to_remove:
        scheduled_ads.remove(ad)
    
    save_scheduled_ads()






@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    global scheduled_ads
    scheduled_ads = load_scheduled_ads()
    check_scheduled_ads.start()
    
    # Sync the command tree with Discord
    await bot.tree.sync()
    logger.info("Command tree synced with Discord")

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("You don't have the necessary permissions to use this command.", ephemeral=True)
    else:
        logger.error(f"An error occurred: {str(error)}")
        await ctx.send(f"An error occurred: {str(error)}", ephemeral=True)

bot.run(config['TOKEN'])