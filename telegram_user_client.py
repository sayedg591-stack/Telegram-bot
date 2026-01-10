"""
Telegram User Account Client
Telethon দিয়ে user account login এবং QuotexPartnerBot থেকে data fetch
⚠️ Warning: Personal use only. Use at your own risk.
"""

from telethon import TelegramClient, events
from telethon.tl.types import User
import asyncio
import re
import os
import json
import re
from datetime import datetime

# ============================================================
# 🔧 Configuration - এখানে শুধু এই দুটি জিনিস দিন
# ============================================================

# 1. আপনার Telegram Phone Number (country code সহ)
PHONE_NUMBER = "+8801754944895"

# 2. QuotexPartnerBot এর URL (affiliate code সহ)
QUOTEX_BOT_URL = "https://t.me/QuotexPartnerBot?start=348134_ad429428de0db361d06b"

# ============================================================
# 🔐 Telegram API Credentials
# https://my.telegram.org থেকে নিন (একবার দিলেই হবে)
# ============================================================

# ✅ সঠিক API Credentials set করা হয়েছে!
USE_DEMO_MODE = False  # Real mode enabled

if not USE_DEMO_MODE:
    API_ID = 37420315  # আপনার API ID
    API_HASH = "83befeca8572f0d118f519a3d0c486b0"  # আপনার API Hash
else:
    # Demo mode - API credentials ছাড়া test করার জন্য
    API_ID = None
    API_HASH = None
    print("⚠️  DEMO MODE: API credentials required for real functionality")

# ============================================================
# 🤖 Auto-extracted from URL (manually set করার দরকার নেই)
# ============================================================

def extract_bot_info(url):
    """URL থেকে bot username এবং start parameter extract করুন"""
    try:
        # Extract bot username
        bot_match = re.search(r't\.me/([^?]+)', url)
        bot_username = bot_match.group(1) if bot_match else "QuotexPartnerBot"
        
        # Extract start parameter
        start_match = re.search(r'start=([^&]+)', url)
        start_param = start_match.group(1) if start_match else ""
        
        return bot_username, start_param
    except:
        return "QuotexPartnerBot", "348134_ad429428de0db361d06b"

QUOTEX_BOT_USERNAME, START_PARAMETER = extract_bot_info(QUOTEX_BOT_URL)

# Session file name
SESSION_NAME = "quotex_session"


class TelegramUserClient:
    """Telegram User Account Client"""
    
    def __init__(self):
        self.client = None
        self.is_connected = False
    
    async def initialize(self):
        """Client initialize এবং login করুন"""
        try:
            # Check if demo mode
            if USE_DEMO_MODE or not API_ID or not API_HASH:
                print("="*60)
                print("⚠️  DEMO MODE ACTIVE")
                print("="*60)
                print("\n❌ Telegram API credentials না থাকায় real login সম্ভব নয়")
                print("\n📋 API credentials পেতে:")
                print("   1. https://my.telegram.org এ যান")
                print("   2. +8801754944895 দিয়ে login করুন")
                print("   3. API Development Tools > Create App")
                print("   4. API ID এবং API Hash copy করুন")
                print("   5. telegram_user_client.py তে update করুন")
                print("\n⚠️  Bot এখন mock data দিয়ে চলবে")
                print("="*60)
                self.is_connected = False
                return False
            
            print("="*60)
            print("🔧 Telegram User Client Initializing...")
            print("="*60)
            
            # Create client
            self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
            
            # Connect
            await self.client.connect()
            
            # Check if already logged in
            if not await self.client.is_user_authorized():
                print(f"\n📱 Telegram Login Required")
                print(f"📞 Phone: {PHONE_NUMBER}")
                print("-"*60)
                
                # Send code request
                print("📤 OTP পাঠানো হচ্ছে...")
                await self.client.send_code_request(PHONE_NUMBER)
                print(f"✅ OTP পাঠানো হয়েছে {PHONE_NUMBER} এ")
                
                # Get OTP from user
                code = input("\n📲 OTP code enter করুন: ").strip()
                
                try:
                    await self.client.sign_in(PHONE_NUMBER, code)
                    print("✅ OTP verified successfully!")
                except Exception as e:
                    # If 2FA enabled
                    if "password" in str(e).lower() or "2FA" in str(e):
                        print("\n🔐 2FA Enabled - Password required")
                        password = input("🔐 2FA Password enter করুন: ").strip()
                        await self.client.sign_in(password=password)
                        print("✅ 2FA verified successfully!")
                    else:
                        raise e
            else:
                print("\n✅ Already logged in (session found)")
            
            self.is_connected = True
            me = await self.client.get_me()
            
            print("\n" + "="*60)
            print(f"✅ Login Successful!")
            print(f"👤 Name: {me.first_name}")
            print(f"📱 Phone: {me.phone}")
            if me.username:
                print(f"🔗 Username: @{me.username}")
            print("="*60)
            
            return True
        
        except Exception as e:
            print(f"\n❌ Login error: {e}")
            return False
    
    async def start_quotex_bot(self):
        """QuotexPartnerBot কে /start করুন affiliate code সহ"""
        try:
            print(f"\n🤖 Connecting to {QUOTEX_BOT_USERNAME}...")
            
            # Get bot
            bot = await self.client.get_entity(QUOTEX_BOT_USERNAME)
            
            # Send /start with parameter
            print(f"📤 Sending: /start {START_PARAMETER}")
            await self.client.send_message(
                bot,
                f"/start {START_PARAMETER}"
            )
            
            print(f"✅ {QUOTEX_BOT_USERNAME} started successfully!")
            print(f"🔗 Affiliate code: {START_PARAMETER}")
            
            # Wait for response
            await asyncio.sleep(2)
            
            return True
        
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
            return False
    
    async def check_trader(self, trader_id):
        """
        QuotexPartnerBot এ trader ID পাঠিয়ে data fetch করুন
        
        Args:
            trader_id (str): Trader ID
        
        Returns:
            dict: Parsed trader data
        """
        try:
            # Get bot
            bot = await self.client.get_entity(QUOTEX_BOT_USERNAME)
            
            print(f"\n📤 Sending trader ID: {trader_id} to @{QUOTEX_BOT_USERNAME}")
            
            # Get current message count before sending
            old_messages = await self.client.get_messages(bot, limit=1)
            old_msg_id = old_messages[0].id if old_messages else 0
            
            # Send trader ID
            await self.client.send_message(bot, str(trader_id))
            
            print(f"⏳ Waiting for response from @{QUOTEX_BOT_USERNAME}...")
            
            # Wait for response (longer wait time)
            await asyncio.sleep(5)
            
            # Get new messages after our request
            messages = await self.client.get_messages(bot, limit=5)
            
            if not messages:
                print("❌ No response received")
                return {"status": "error", "message": "No response from bot"}
            
            # Find the response message (newer than our request)
            response_text = None
            for msg in messages:
                if msg.id > old_msg_id and msg.message:
                    response_text = msg.message
                    break
            
            if not response_text:
                print("❌ Could not find response message")
                return {"status": "error", "message": "No response from bot"}
            
            print(f"📥 Received response from @{QUOTEX_BOT_USERNAME}")
            print(f"📝 Response preview: {response_text[:100]}...")
            
            # Parse response
            trader_data = self.parse_quotex_response(response_text, trader_id)
            
            return trader_data
        
        except Exception as e:
            print(f"❌ Error checking trader: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    def parse_quotex_response(self, response_text, trader_id):
        """
        QuotexPartnerBot এর response parse করুন
        
        Response format:
        Trader # 78351542
        Country: Bangladesh
        (Registration Date: 10.01.2026)
        Balance: $ 0.00
        Deposits Count: 0
        Deposits Sum: $ 0.00
        ...
        """
        try:
            # Check if trader not found
            if "was not found" in response_text or "not found" in response_text:
                return {
                    "status": "not_found",
                    "trader_id": trader_id,
                    "message": "Trader not found"
                }
            
            # Parse data
            data = {
                "status": "found",
                "trader_id": trader_id,
                "country": "N/A",
                "registration_date": "N/A",
                "balance": 0.0,
                "deposits_count": 0,
                "deposits_sum": 0.0,
                "withdrawals_sum": 0.0,
                "turnover_all": 0.0,
                "raw_response": response_text
            }
            
            lines = response_text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Country
                if 'Country:' in line:
                    data['country'] = line.split('Country:')[1].strip()
                
                # Registration date
                elif 'Registration Date:' in line:
                    date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', line)
                    if date_match:
                        data['registration_date'] = date_match.group(1)
                
                # Balance
                elif 'Balance:' in line:
                    balance_match = re.search(r'\$\s*([\d.]+)', line)
                    if balance_match:
                        data['balance'] = float(balance_match.group(1))
                
                # Deposits Count
                elif 'Deposits Count:' in line:
                    count_match = re.search(r':\s*(\d+)', line)
                    if count_match:
                        data['deposits_count'] = int(count_match.group(1))
                
                # Deposits Sum
                elif 'Deposits Sum:' in line:
                    sum_match = re.search(r'\$\s*([\d.]+)', line)
                    if sum_match:
                        data['deposits_sum'] = float(sum_match.group(1))
                
                # Withdrawals Sum
                elif 'Withdrawals Sum:' in line:
                    sum_match = re.search(r'\$\s*([\d.]+)', line)
                    if sum_match:
                        data['withdrawals_sum'] = float(sum_match.group(1))
                
                # Turnover All
                elif 'Turnover All:' in line:
                    turnover_match = re.search(r'\$\s*([\d.]+)', line)
                    if turnover_match:
                        data['turnover_all'] = float(turnover_match.group(1))
            
            print(f"✅ Successfully parsed trader data")
            return data
        
        except Exception as e:
            print(f"❌ Parse error: {e}")
            return {
                "status": "error",
                "trader_id": trader_id,
                "message": f"Parse error: {str(e)}",
                "raw_response": response_text
            }
    
    async def disconnect(self):
        """Disconnect client"""
        if self.client and self.is_connected:
            await self.client.disconnect()
            print("👋 Disconnected from Telegram")


# Global client instance
telegram_client = TelegramUserClient()


async def get_trader_data(trader_id):
    """
    Main function to get trader data
    
    Usage:
        data = await get_trader_data("78351542")
    """
    global telegram_client
    
    # Initialize if not connected
    if not telegram_client.is_connected:
        success = await telegram_client.initialize()
        if not success:
            return {"status": "error", "message": "Failed to connect"}
        
        # Start QuotexPartnerBot with affiliate code
        await telegram_client.start_quotex_bot()
    
    # Check trader
    trader_data = await telegram_client.check_trader(trader_id)
    
    return trader_data


# Test function
async def test():
    """Test করার জন্য"""
    print("\n" + "="*60)
    print("🧪 Testing Telegram User Client")
    print("="*60)
    
    print(f"\n📋 Configuration:")
    print(f"   Phone: {PHONE_NUMBER}")
    print(f"   Bot: {QUOTEX_BOT_USERNAME}")
    print(f"   Code: {START_PARAMETER}")
    
    # Test trader IDs
    test_ids = ["78351542", "36314853"]
    
    for trader_id in test_ids:
        print(f"\n📊 Checking Trader ID: {trader_id}")
        print("-"*60)
        
        data = await get_trader_data(trader_id)
        
        print(f"\n✅ Result:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("-"*60)
        
        await asyncio.sleep(3)
    
    # Disconnect
    await telegram_client.disconnect()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Quotex Telegram User Client")
    print("="*60)
    print(f"\n📱 Phone: {PHONE_NUMBER}")
    print(f"🤖 Bot URL: {QUOTEX_BOT_URL}")
    print(f"\n⏳ Starting...\n")
    
    # Run test
    asyncio.run(test())
