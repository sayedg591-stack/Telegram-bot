"""
Quotex Affiliate Bot - Async Version
Fully async implementation to work properly with Telethon
"""

import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

# Import Telegram User Client
from telegram_user_client import get_trader_data, telegram_client

# Bot Configuration
BOT_TOKEN = "8441476926:AAGWc1_v-BDSxx3yKUw0Dh6vbft5sVhLP9I"
AFFILIATE_CODE = "348134_ad429428de0db361d06b"
AFFILIATE_ID = "1709029"
QUOTEX_SIGNUP_LINK = f"https://broker-qx.pro/sign-up/?lid={AFFILIATE_ID}"
VIP_GROUP_LINK = "https://t.me/+vKxDAerqzntiODFl"
SUPPORT_USERNAME = "@traderjisanx"

# Image paths (absolute)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(BASE_DIR, "Photo")
WELCOME_IMAGE = os.path.join(PHOTO_DIR, "1.jpg")
BALANCE_LOW_IMAGE = os.path.join(PHOTO_DIR, "2.jpg")
NOT_FOUND_IMAGE = os.path.join(PHOTO_DIR, "3.png")

# Minimum balance required
MIN_BALANCE = 10.0

# Stats tracking
stats = {
    "total_checks": 0,
    "found_accounts": 0,
    "not_found_accounts": 0
}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """স্টার্ট কমান্ড"""
    user = update.effective_user
    full_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

    welcome_text = f"""👋 <b>Hello, {full_name}</b>

👋 <b>Welcome to Jisan X — Daily Private Quotex Class Access Bot</b>

💰 <b>Step 1: Create Your Quotex Account</b>

<b>Create your trading account using our turnover link:</b>
👉 {QUOTEX_SIGNUP_LINK}

<b>Minimum deposit: $10 (required for class access)</b>

🎯 <b>What You'll Get (Class Benefits)</b>

• <b>High Accuracy Signal Bot I Will Give You Free.</b>

• <b>Daily Free Signal 20-50.</b>

• <b>Be 100% sure that I will make you $50 profit every day.</b>

📌 <b>Step 2:</b>

<b>Send your Quotex Trader ID here.</b>

⏱️ <b>After verification, you'll get Private Class Group Access in 10-20 Second</b>

<b>For any help, contact →</b> {SUPPORT_USERNAME}"""

    keyboard = [
        [InlineKeyboardButton("📝 Create Account", url=QUOTEX_SIGNUP_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send with photo if available
    if os.path.exists(WELCOME_IMAGE):
        with open(WELCOME_IMAGE, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=welcome_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            welcome_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """হেল্প কমান্ড"""
    help_text = f"""📞 <b>Need Help?</b>

<b>For any issues or questions, please contact our admin:</b>

👤 <b>Admin: {SUPPORT_USERNAME}</b>

<b>We're here to help you 24/7!</b> 💬"""
    await update.message.reply_text(help_text, parse_mode='HTML')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistics"""
    stats_text = f"""📊 <b>Bot Statistics</b>

📈 <b>Total Checks:</b> <b>{stats['total_checks']}</b>
✅ <b>Verified Accounts:</b> <b>{stats['found_accounts']}</b>
❌ <b>Not Found:</b> <b>{stats['not_found_accounts']}</b>

🔄 <b>Real-time verification via @QuotexPartnerBot</b>"""
    await update.message.reply_text(stats_text, parse_mode='HTML')


async def check_trader_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trader ID চেক করুন"""
    trader_id = update.message.text.strip()
    user = update.effective_user
    full_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

    # Update stats
    stats['total_checks'] += 1

    # Loading message
    loading_msg = await update.message.reply_text(
        "🔍 <b>Checking your account...</b>\n⏳ <b>Please wait 5-10 seconds...</b>",
        parse_mode='HTML'
    )

    try:
        # Get real-time data from QuotexPartnerBot
        trader_data = await get_trader_data(trader_id)

        # Delete loading message
        await loading_msg.delete()

        if trader_data["status"] == "not_found":
            # Not found
            stats['not_found_accounts'] += 1

            not_found_text = f"""<b>Dear {full_name},</b>

<b>⚠️ This Quotex account was not created using our link.</b>

<b>To join our private live classes, please:</b>

<b>1️⃣ Delete your current Quotex account.</b>

<b>2️⃣ Create a new account using our link:</b>
👉 {QUOTEX_SIGNUP_LINK}

<b>Deposit Minimum $10</b>

<b>After depositing, send your Trader ID to this bot — you will automatically receive the class group link.</b>

<b>For any help, contact →</b> {SUPPORT_USERNAME}"""

            keyboard = [
                [InlineKeyboardButton("📝 Create New Account", url=QUOTEX_SIGNUP_LINK)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send with photo
            if os.path.exists(NOT_FOUND_IMAGE):
                with open(NOT_FOUND_IMAGE, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=not_found_text,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
            else:
                await update.message.reply_text(
                    not_found_text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )

        elif trader_data["status"] == "found":
            # Found
            stats['found_accounts'] += 1

            balance = trader_data.get('balance', 0)
            deposits_sum = trader_data.get('deposits_sum', 0)
            country = trader_data.get('country', 'N/A')
            reg_date = trader_data.get('registration_date', 'N/A')

            # Check if balance is sufficient
            if balance < MIN_BALANCE:
                # Balance too low
                emoji = "😞"

                low_balance_text = f"""<b>Dear {full_name},</b>

<b>❤️❤️ Thank You For Create An Account From Our Link.</b>

<b>⚠️ Your balance is less than ${MIN_BALANCE:.0f}</b>

<b>Kindly deposit Minimum ${MIN_BALANCE:.0f} or More to join Tradearn — Daily Private Quotex Highest Accuracy Signal Bot.</b>

<b>Now Your Balance: ${balance:.2f} {emoji}</b>

📊 <b>Account Info:</b>
<b>Country:</b> {country}
<b>Registration Date:</b> {reg_date}
<b>Total Deposits:</b> ${deposits_sum:.2f}

💰 <b>Please deposit at least ${MIN_BALANCE:.0f} and send your Trader ID again to get access!</b>

<b>For any help, contact →</b> {SUPPORT_USERNAME}"""

                keyboard = [
                    [InlineKeyboardButton("💰 Deposit Now", url="https://market-qx.trade/en/trade")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Send with photo
                if os.path.exists(BALANCE_LOW_IMAGE):
                    with open(BALANCE_LOW_IMAGE, 'rb') as photo:
                        await update.message.reply_photo(
                            photo=photo,
                            caption=low_balance_text,
                            parse_mode='HTML',
                            reply_markup=reply_markup
                        )
                else:
                    await update.message.reply_text(
                        low_balance_text,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )

            else:
                # Balance sufficient - give group access
                emoji = "😊"

                success_text = f"""🎉 <b>Congratulations {full_name}!</b>

✅ <b>Your account has been verified successfully!</b>

👤 <b>Trader ID:</b> <b>{trader_id}</b>
🌍 <b>Country:</b> <b>{country}</b>
📅 <b>Registration:</b> <b>{reg_date}</b>
💰 <b>Balance:</b> <b>${balance:.2f} {emoji}</b>
💵 <b>Total Deposits:</b> <b>${deposits_sum:.2f}</b>

🎉 <b>You have successfully met the requirements!</b>

👇 <b>Click below to join our Private Class Group:</b>"""

                keyboard = [
                    [InlineKeyboardButton("⭐ Join VIP Class Group", url=VIP_GROUP_LINK)],
                    [InlineKeyboardButton("📈 Start Trading", url="https://qxbroker.com/")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    success_text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )

        else:
            # Error
            error_text = f"""⚠️ <b>Temporary Issue</b>

<b>Sorry, we couldn't verify your account right now.</b>

<b>Error:</b> {trader_data.get('message', 'Unknown')}

<b>Please try again in a few moments.</b>

<b>For any help, contact →</b> {SUPPORT_USERNAME}"""

            await update.message.reply_text(error_text, parse_mode='HTML')

    except Exception as e:
        # Delete loading message
        try:
            await loading_msg.delete()
        except:
            pass

        error_text = f"""❌ <b>Error Occurred</b>

<b>Sorry! An error occurred while checking your account.</b>

<b>Error:</b> {str(e)}

<b>Please try again or contact →</b> {SUPPORT_USERNAME}"""

        await update.message.reply_text(error_text, parse_mode='HTML')


async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অন্যান্য messages"""
    user = update.effective_user
    full_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

    error_text = f"""<b>Dear {full_name},</b>

<b>⚠️ This Quotex account was not created using our link.</b>

<b>To join our private live classes, please:</b>

<b>1️⃣ Delete your current Quotex account.</b>

<b>2️⃣ Create a new account using our link:</b>
👉 {QUOTEX_SIGNUP_LINK}

<b>Deposit Minimum $10</b>

<b>After depositing, send your Trader ID to this bot — you will automatically receive the class group link.</b>

<b>For any help, contact →</b> {SUPPORT_USERNAME}"""

    keyboard = [
        [InlineKeyboardButton("📝 Create Account", url=QUOTEX_SIGNUP_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send with photo
    if os.path.exists(NOT_FOUND_IMAGE):
        with open(NOT_FOUND_IMAGE, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=error_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            error_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )


async def main():
    """Main function"""
    print("\n" + "="*60)
    print("🤖 Quotex Affiliate Bot - Async Version")
    print("="*60)

    # Initialize Telegram User Client
    print("\n🔧 Step 1: Initializing Telegram User Client...")
    print("-"*60)

    try:
        result = await telegram_client.initialize()

        if result:
            print("\n🔧 Step 2: Starting QuotexPartnerBot...")
            print("-"*60)
            await telegram_client.start_quotex_bot()

            print("\n✅ All systems ready!")
        else:
            print("\n⚠️ Failed to initialize Telegram User Client")
            print("⚠️ Bot will start but may not fetch real data")

    except Exception as e:
        print(f"\n⚠️ Client initialization warning: {e}")
        print("⚠️ Bot will start in limited mode")

    print("\n" + "="*60)
    print("🚀 Starting Telegram Bot...")
    print("="*60)
    print(f"📊 Real-time data fetch: {'ENABLED' if telegram_client.is_connected else 'DISABLED'}")
    print(f"⚡ Bot listening for messages...")
    print(f"⚠️  Press Ctrl+C to stop\n")

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.Regex(r'^\d+$'), check_trader_id))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other_messages))

    # Start bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    finally:
        await application.stop()
        await telegram_client.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
