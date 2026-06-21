import discord
from discord.ext import commands
import asyncio
import os

# ======== إعدادات البوت ========
TOKEN = os.getenv('DISCORD_TOKEN')  # التوكن من متغير البيئة
if TOKEN is None:
    print("خطأ: لم يتم العثور على  في متغيرات البيئة.")
    exit()

YOUR_USER_ID = 123456789012345678  # ضع ID حسابك هنا
SERVER_ID = 123456789012345678  # ضع ID السيرفر هنا (اختياري)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# ============================================
# أمر الاختبار: يرسل لك رسالة خاصة
# ============================================
@bot.command()
async def test_dm(ctx, *, message_text=None):
    """إرسال رسالة اختبارية لك فقط (في الخاص)"""
    if ctx.author.id != YOUR_USER_ID:
        await ctx.send("❌ ليس لديك صلاحية.")
        return

    if message_text is None:
        await ctx.send("📝 **اكتب النص التجريبي (خلال 60 ثانية):**")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            msg = await bot.wait_for("message", timeout=60.0, check=check)
            message_text = msg.content
        except asyncio.TimeoutError:
            await ctx.send("❌ تم الإلغاء (انتهى الوقت).")
            return

    # إرسال الرسالة لك في الخاص
    await ctx.author.send(message_text)
    await ctx.send("✅ تم إرسال الرسالة لك في الخاص. تحقق من رسائلك المباشرة.")

# ============================================
# أمر الإرسال للجميع
# ============================================
@bot.command()
async def send_all(ctx, *, message_text=None):
    """إرسال رسالة مخصصة لجميع أعضاء السيرفر"""
    if ctx.author.id != YOUR_USER_ID:
        await ctx.send("❌ ليس لديك صلاحية لهذا الأمر.")
        return

    # جلب عدد الأعضاء
    total_members = len(ctx.guild.members)
    await ctx.send(f"📊 **عدد أعضاء السيرفر:** {total_members}")

    # طلب النص إذا لم يكتب مع الأمر
    if message_text is None:
        await ctx.send("📝 **اكتب النص الذي تريد إرساله للجميع (خلال 120 ثانية):**")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            msg = await bot.wait_for("message", timeout=120.0, check=check)
            message_text = msg.content
        except asyncio.TimeoutError:
            await ctx.send("❌ تم الإلغاء (انتهى الوقت).")
            return

    # عرض معاينة وطلب تأكيد
    preview = message_text[:500] + ("..." if len(message_text) > 500 else "")
    await ctx.send(f"⚠️ **معاينة الرسالة:**\n```\n{preview}\n```\n📨 سيتم إرسالها لـ **{total_members}** عضو.\nهل أنت متأكد؟ اكتب `confirm` خلال 30 ثانية.")

    def confirm_check(m):
        return m.author == ctx.author and m.content.lower() == "confirm"

    try:
        await bot.wait_for("message", timeout=30.0, check=confirm_check)
    except asyncio.TimeoutError:
        await ctx.send("❌ تم الإلغاء.")
        return

    # بدء الإرسال
    await ctx.send(f"✅ جارٍ الإرسال إلى {total_members} عضو... قد يستغرق هذا بضع دقائق.")

    success = 0
    failed = 0

    for member in ctx.guild.members:
        if member.bot:
            continue  # تخطي البوتات

        try:
            await member.send(message_text)
            success += 1
            await asyncio.sleep(0.5)  # تفادي حظر السرعة
        except:
            failed += 1

        # عرض تقدم كل 50 عضو
        if (success + failed) % 50 == 0:
            print(f"[*] تقدم: {success + failed}/{total_members}")

    # التقرير النهائي
    await ctx.send(
        f"✅ **تم الانتهاء!**\n"
        f"✅ نجح: {success}\n"
        f"❌ فشل: {failed}\n"
        f"📊 المجموع: {total_members}"
    )

# ============================================
# تشغيل البوت
# ============================================
bot.run(TOKEN)
