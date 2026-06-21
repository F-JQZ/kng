import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

# ======== قراءة التوكن من متغير البيئة ========
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة.")
    exit()

# ======== إعدادات البوت ========
YOUR_USER_ID = 123456789012345678  # ضع ID حسابك هنا

# استخدام الصلاحيات الأساسية فقط (بدون Privileged Intents)
intents = discord.Intents.default()
intents.message_content = True  # ضروري لقراءة رسائل التأكيد
# ملاحظة: لن يتمكن البوت من جلب قائمة الأعضاء إذا لم يُفعّل SERVER MEMBERS INTENT

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ============================================
# أمر اختبار (Slash Command)
# ============================================
@tree.command(
    name="test_dm",
    description="إرسال رسالة اختبارية لك فقط (في الخاص)"
)
@app_commands.describe(message="النص الذي تريد إرساله (اختياري)")
async def test_dm(interaction: discord.Interaction, message: str = None):
    if interaction.user.id != YOUR_USER_ID:
        await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        return

    await interaction.response.send_message("📨 جاري إرسال الرسالة لك في الخاص...", ephemeral=True)

    if message is None:
        await interaction.followup.send("📝 **اكتب النص الذي تريد إرساله (خلال 60 ثانية):**", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", timeout=60.0, check=check)
            message = msg.content
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ تم الإلغاء (انتهى الوقت).", ephemeral=True)
            return

    try:
        await interaction.user.send(message)
        await interaction.followup.send("✅ تم إرسال الرسالة لك في الخاص.", ephemeral=True)
    except:
        await interaction.followup.send("❌ فشل الإرسال. تأكد من أنك تسمح بالرسائل الخاصة.", ephemeral=True)

# ============================================
# أمر الإرسال للجميع (Slash Command)
# ============================================
@tree.command(
    name="send_all",
    description="إرسال رسالة مخصصة لجميع أعضاء السيرفر"
)
@app_commands.describe(message="النص الذي تريد إرساله للجميع (اختياري)")
async def send_all(interaction: discord.Interaction, message: str = None):
    if interaction.user.id != YOUR_USER_ID:
        await interaction.response.send_message("❌ ليس لديك صلاحية.", ephemeral=True)
        return

    # جلب الأعضاء (يعمل فقط إذا كان SERVER MEMBERS INTENT مفعّلاً)
    try:
        total_members = len(interaction.guild.members)
    except:
        total_members = "غير معروف (فعّل SERVER MEMBERS INTENT)"
    
    await interaction.response.send_message(f"📊 **عدد أعضاء السيرفر:** {total_members}", ephemeral=True)

    if message is None:
        await interaction.followup.send("📝 **اكتب النص الذي تريد إرساله للجميع (خلال 120 ثانية):**", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", timeout=120.0, check=check)
            message = msg.content
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ تم الإلغاء (انتهى الوقت).", ephemeral=True)
            return

    preview = message[:500] + ("..." if len(message) > 500 else "")
    await interaction.followup.send(
        f"⚠️ **معاينة الرسالة:**\n```\n{preview}\n```\n"
        f"📨 سيتم إرسالها لـ **{total_members}** عضو.\n"
        f"هل أنت متأكد؟ اكتب `confirm` خلال 30 ثانية.",
        ephemeral=True
    )

    def confirm_check(m):
        return m.author == interaction.user and m.content.lower() == "confirm"

    try:
        await bot.wait_for("message", timeout=30.0, check=confirm_check)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ تم الإلغاء.", ephemeral=True)
        return

    await interaction.followup.send(f"✅ جارٍ الإرسال إلى {total_members} عضو...", ephemeral=True)

    success = 0
    failed = 0

    for member in interaction.guild.members:
        if member.bot:
            continue

        try:
            await member.send(message)
            success += 1
            await asyncio.sleep(0.5)
        except:
            failed += 1

        if (success + failed) % 50 == 0:
            print(f"[*] تقدم: {success + failed}/{total_members}")

    await interaction.followup.send(
        f"✅ **تم الانتهاء!**\n"
        f"✅ نجح: {success}\n"
        f"❌ فشل: {failed}\n"
        f"📊 المجموع: {total_members}",
        ephemeral=True
    )

# ============================================
# حدث تسجيل الأوامر عند تشغيل البوت
# ============================================
@bot.event
async def on_ready():
    await tree.sync()
    print(f"[+] Bot is ready as {bot.user}")
    print(f"[+] Slash commands synced!")

# ============================================
# تشغيل البوت
# ============================================
bot.run(TOKEN)
