import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import aiohttp
from io import BytesIO
import datetime
import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# الألوان والخلفية
BACKGROUND_COLOR = (32, 34, 37)  # #202225
ACCENT_COLOR = (114, 137, 218)    # #7289da
TEXT_COLOR = (255, 255, 255)
SUB_TEXT_COLOR = (150, 150, 150)

# ID قناة الترحيب حقك
WELCOME_CHANNEL_ID = 1126668886985670699

async def get_user_avatar_url(user, size=256):
    return user.avatar.url if user.avatar else user.default_avatar.url

async def create_welcome_image(member, inviter=None):
    """
    إنشاء صورة ترحيب بنفس شكل ProBot
    """
    # حجم الصورة
    width, height = 600, 300
    img = Image.new('RGB', (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # جلب صورة البروفايل
    avatar_url = await get_user_avatar_url(member, 128)
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            avatar_data = await resp.read()
    
    avatar = Image.open(BytesIO(avatar_data)).convert('RGBA')
    avatar = avatar.resize((100, 100))
    
    # عمل دائرة للصورة (Mask)
    mask = Image.new('L', (100, 100), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 100, 100), fill=255)
    
    # وضع الصورة على الخلفية
    img.paste(avatar, (50, 50), mask)
    
    # رسم دائرة حول الصورة
    draw.ellipse((48, 48, 102, 102), outline=ACCENT_COLOR, width=3)
    
    # اسم العضو
    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # اسم المستخدم
    name = member.name[:20] + '...' if len(member.name) > 20 else member.name
    draw.text((180, 55), name, font=font_title, fill=TEXT_COLOR)
    
    # تاق المستخدم
    draw.text((180, 95), f"@{member.name}", font=font_sub, fill=SUB_TEXT_COLOR)
    
    # تاريخ إنشاء الحساب
    created_at = member.created_at
    days_ago = (datetime.datetime.utcnow() - created_at).days
    years_ago = days_ago // 365
    
    draw.text((180, 140), "Create Discord:", font=font_small, fill=ACCENT_COLOR)
    draw.text((180, 160), f"{years_ago} years ago", font=font_small, fill=SUB_TEXT_COLOR)
    
    # الرقم التسلسلي
    member_number = member.guild.members.index(member) + 1
    draw.text((180, 195), "Number:", font=font_small, fill=ACCENT_COLOR)
    draw.text((180, 215), f"#{member_number}", font=font_small, fill=SUB_TEXT_COLOR)
    
    # من دعاه
    if inviter:
        inviter_name = inviter.name[:20]
        draw.text((180, 250), "Invited By:", font=font_small, fill=ACCENT_COLOR)
        draw.text((180, 270), f"@{inviter_name}", font=font_small, fill=SUB_TEXT_COLOR)
    else:
        draw.text((180, 250), "Invited By:", font=font_small, fill=ACCENT_COLOR)
        draw.text((180, 270), "Direct Join", font=font_small, fill=SUB_TEXT_COLOR)
    
    # حفظ الصورة
    img_path = f"welcome_{member.id}.png"
    img.save(img_path)
    return img_path

@bot.event
async def on_member_join(member):
    """
    عند دخول عضو جديد - يرسل ترحيب في الروم 1126668886985670699
    """
    # البحث عن من دعاه (إذا كان متاح)
    inviter = None
    try:
        async for entry in member.guild.audit_logs(action=discord.AuditLogAction.invite_create, limit=10):
            if entry.target == member:
                inviter = entry.user
                break
    except:
        pass
    
    # إنشاء صورة الترحيب
    img_path = await create_welcome_image(member, inviter)
    
    # جلب قناة الترحيب
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    if channel:
        embed = discord.Embed(
            title=f"✨ Welcome To {member.guild.name}",
            description=f"**Member:** {member.mention}\n"
                       f"**Create Discord:** {member.created_at.strftime('%Y-%m-%d')}\n"
                       f"**Number:** #{member.guild.members.index(member) + 1}\n"
                       f"**Invited By:** {inviter.mention if inviter else 'Direct Join'}",
            color=ACCENT_COLOR
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Total Members: {member.guild.member_count}")
        
        file = discord.File(img_path, filename="welcome.png")
        embed.set_image(url="attachment://welcome.png")
        
        await channel.send(file=file, embed=embed)
        
        # حذف الصورة بعد الإرسال
        os.remove(img_path)
        print(f"[✓] تم إرسال ترحيب للعضو {member.name} في الروم {WELCOME_CHANNEL_ID}")
    else:
        print(f"[✗] لم يتم العثور على قناة الترحيب ID: {WELCOME_CHANNEL_ID}")

@bot.event
async def on_ready():
    print(f"[✓] البوت شغال كـ {bot.user.name}")
    print(f"[✓] في {len(bot.guilds)} سيرفرات")
    
    # التحقق من وجود قناة الترحيب
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        print(f"[✓] تم العثور على قناة الترحيب: #{channel.name}")
    else:
        print(f"[✗] تحذير: ما لقيت قناة بالـ ID {WELCOME_CHANNEL_ID}")

# تشغيل البوت
TOKEN = os.environ.get("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN غير موجود. أضفه في .env")