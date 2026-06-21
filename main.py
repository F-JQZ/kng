import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

# ======== قراءة التوكن ========
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة.")
    exit()

# ======== إعدادات البوت ========
ALLOWED_ROLE_NAME = "k"  # اسم الرتبة المسموح لها
STREAM_LINK = "https://www.twitch.tv/king"  # رابط قناتك
STREAM_NAME = "KING LIVE!"  # اسم البث

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # لازم عشان يجيب كل الأعضاء

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ============================================
# دالة التحقق من الصلاحية
# ============================================
def has_allowed_role(interaction: discord.Interaction) -> bool:
    return any(role.name == ALLOWED_ROLE_NAME for role in interaction.user.roles)

# ============================================
# أمر اختبار (Slash Command)
# ============================================
@tree.command(
    name="test_dm",
    description="إرسال رسالة اختبارية لك فقط (في الخاص)"
)
@app_commands.describe(message="النص الذي تريد إرساله (اختياري)")
async def test_dm(interaction: discord.Interaction, message: str = None):
    if not has_allowed_role(interaction):
        await interaction.response.send_message(
            f"❌ ليس لديك الصلاحية المطلوبة. تحتاج إلى رتبة `{ALLOWED_ROLE_NAME}`.",
            ephemeral=True
        )
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
# أمر الإرسال للجميع (في الخاص)
# ============================================
@tree.command(
    name="send_all",
    description="إرسال رسالة لجميع أعضاء السيرفر (في الخاص)"
)
@app_commands.describe(message="النص الذي تريد إرساله (اختياري)")
async def send_all(interaction: discord.Interaction, message: str = None):
    if not has_allowed_role(interaction):
        await interaction.response.send_message(
            f"❌ ليس لديك الصلاحية المطلوبة. تحتاج إلى رتبة `{ALLOWED_ROLE_NAME}`.",
            ephemeral=True
        )
        return

    total_members = len(interaction.guild.members)
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
        f"📨 سيتم إرسالها لـ **{total_members}** عضو في الخاص.\n"
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

    await interaction.followup.send(f"✅ جارٍ الإرسال إلى {total_members} عضو... قد يستغرق هذا بضع دقائق.", ephemeral=True)

    success = 0
    failed = 0

    for member in interaction.guild.members:
        if member.bot:
            continue

        try:
            await member.send(message)
            success += 1
            await asyncio.sleep(0.5)  # تفادي حظر السرعة
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
# أمر الإرسال في قناة (مع منشن)
# ============================================
@tree.command(
    name="send_channel",
    description="إرسال رسالة في قناة معينة مع منشن للجميع"
)
@app_commands.describe(
    channel="القناة المراد الإرسال فيها",
    message="النص الذي تريد إرساله"
)
async def send_channel(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str
):
    if not has_allowed_role(interaction):
        await interaction.response.send_message(
            f"❌ ليس لديك الصلاحية المطلوبة. تحتاج إلى رتبة `{ALLOWED_ROLE_NAME}`.",
            ephemeral=True
        )
        return

    # تأكيد قبل الإرسال
    await interaction.response.send_message(
        f"⚠️ هل أنت متأكد من إرسال هذه الرسالة في قناة #{channel.name}؟\n"
        f"```\n{message[:500]}...\n```\n"
        f"اكتب `confirm` خلال 30 ثانية.",
        ephemeral=True
    )

    def confirm_check(m):
        return m.author == interaction.user and m.content.lower() == "confirm"

    try:
        await bot.wait_for("message", timeout=30.0, check=confirm_check)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ تم الإلغاء.", ephemeral=True)
        return

    # إرسال الرسالة في القناة مع منشن
    await channel.send(f"@everyone\n\n{message}")
    await interaction.followup.send(f"✅ تم إرسال الرسالة في قناة #{channel.name}!", ephemeral=True)

# ============================================
# تشغيل البوت مع حالة Streaming بنفسجية
# ============================================
@bot.event
async def on_ready():
    await tree.sync()
    
    # تعيين حالة البوت إلى Streaming (بنفسجي)
    await bot.change_presence(
        activity=discord.Streaming(
            name=STREAM_NAME,
            url=STREAM_LINK
        )
    )
    
    print(f"[+] Bot is ready as {bot.user}")
    print(f"[+] Slash commands synced!")
    print(f"[+] Streaming: {STREAM_NAME} -> {STREAM_LINK}")

# ============================================
# تشغيل البوت
# ============================================
bot.run(TOKEN)
