import telebot
from telebot import types
import requests
import json
import qrcode
import io
import os

API_TOKEN = '8598168936:AAEahaNSDiHwN7WnEtkLxg3hzi43jrsiifM'
SMM_API_KEY = 'cmk0xopwx000004l1bu5058uv'
ADMIN_ID = 5855744754

bot = telebot.TeleBot(API_TOKEN)

user_balances = {}
user_states = {}
pending_orders = {}

VIEW_PRICE = 0.02063
REACTION_PRICE = 0.14211

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('🛍️ Buy Services')
    btn2 = types.KeyboardButton('➕ Add Funds')
    btn3 = types.KeyboardButton('👛 My Balance')
    btn4 = types.KeyboardButton('📞 Contact')
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard

def services_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📊 Telegram Views')
    btn2 = types.KeyboardButton('❤️ Telegram Reactions')
    btn3 = types.KeyboardButton('🔙 Back')
    keyboard.add(btn1, btn2, btn3)
    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    welcome_text = f"""Welcome to SMM BOT 🚀

Hello {username},
Boost your social media presence with our premium & high-speed services.

✨ Fast Delivery
💎 High Quality
💰 Affordable Prices

Select an option from the menu or buttons below to start! 👇"""
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())
    
    if user_id not in user_balances:
        user_balances[user_id] = 0.0

@bot.message_handler(commands=['addbalance'])
def add_balance_command(message):
    user_id = message.from_user.id
    
    if str(user_id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "⚠️ This command is only for admin!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❌ Invalid Format")
            return
        
        target_user_id = int(parts[1])
        amount = float(parts[2])
        
        if target_user_id not in user_balances:
            user_balances[target_user_id] = 0.0
        
        user_balances[target_user_id] += amount
        
        bot.send_message(message.chat.id, f"✅ Balance added successfully!\nUser ID: {target_user_id}\nAdded Amount: ₹{amount:.2f}\nNew Balance: ₹{user_balances[target_user_id]:.2f}")
        
        try:
            bot.send_message(target_user_id, f"💰 Balance Updated!\n✅ ₹{amount:.2f} has been added to your account.\nNew Balance: ₹{user_balances[target_user_id]:.2f}")
        except:
            pass
            
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid format")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text
    
    if text == '🛍️ Buy Services':
        bot.send_message(message.chat.id, "Select service type:", reply_markup=services_keyboard())
    
    elif text == '➕ Add Funds':
        send_payment_info(message)
    
    elif text == '👛 My Balance':
        show_balance(message)
    
    elif text == '📞 Contact':
        contact_admin(message)
    
    elif text == '📊 Telegram Views':
        ask_for_link(message, 'views')
    
    elif text == '❤️ Telegram Reactions':
        ask_for_link(message, 'reactions')
    
    elif text == '🔙 Back':
        bot.send_message(message.chat.id, "Main Menu", reply_markup=main_keyboard())
    
    elif user_id in user_states:
        handle_user_state(message)
    
    else:
        bot.send_message(message.chat.id, "Use buttons for navigation", reply_markup=main_keyboard())

def contact_admin(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="📱 Contact Admin",
            url=f"https://t.me/Unknownboy927"
        )
    )
    bot.send_message(message.chat.id, "Click below to contact admin:", reply_markup=keyboard)

def send_payment_info(message):
    caption = """PAY ON THIS QR AND CLICK ON SEND SS ✅ TO ADD YOUR BALANCE ✅

UPI ID: `paytm.s1h51x8@pty`
Pay via any UPI app: Google Pay, PhonePe, Paytm, etc.

ALL PAYMENT METHOD ACCEPTED
    
⚠️ After payment, click 'SEND SS' button to send payment screenshot"""
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(
            text="✅ SEND SS ✅",
            url=f"https://t.me/Unknownboy927"
        )
    )
    
    try:
        # Generate QR code
        upi_id = "paytm.s1h51x8@pty"
        upi_url = f"upi://pay?pa={upi_id}&pn=SMM Bot&mc=0000&tid=123456&tr=123456789&tn=Payment for SMM Bot&am=&cu=INR"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Send photo
        bot.send_photo(
            chat_id=message.chat.id,
            photo=img_byte_arr,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=markup
        )
        
    except Exception as e:
        print(f"Error generating QR code: {e}")
        # Fallback: send text
        bot.send_message(
            message.chat.id,
            caption + "\n\n⚠️ QR Code generation failed. Please send payment to UPI ID: `paytm.s1h51x8@pty`",
            parse_mode='Markdown',
            reply_markup=markup
        )

def show_balance(message):
    user_id = message.from_user.id
    balance = user_balances.get(user_id, 0.0)
    
    balance_text = f"""👛 Wallet Dashboard

🆔 User ID: `{user_id}`
💵 Main Balance: ₹{balance:.2f}
"""
    
    bot.send_message(message.chat.id, balance_text, parse_mode='Markdown')

def ask_for_link(message, service_type):
    user_id = message.from_user.id
    user_states[user_id] = {'state': 'awaiting_link', 'service': service_type}
    
    price = VIEW_PRICE if service_type == 'views' else REACTION_PRICE
    service_name = "Views" if service_type == 'views' else "Reactions"
    
    bot.send_message(
        message.chat.id,
        f"📊 Telegram {service_name}\n\n"
        f"💰 Rate: ₹{price:.5f} per 100\n"
        f"📦 Min Order: 10\n\n"
        f"🔗 Please send Telegram Post link"
    )

def handle_user_state(message):
    user_id = message.from_user.id
    state_info = user_states[user_id]
    
    if state_info['state'] == 'awaiting_link':
        if 'http' in message.text and 't.me' in message.text:
            state_info['link'] = message.text
            state_info['state'] = 'awaiting_quantity'
            
            service_type = state_info['service']
            price = VIEW_PRICE if service_type == 'views' else REACTION_PRICE
            
            bot.send_message(
                message.chat.id, 
                f"✅ Link received!\n\n"
                f"How many {service_type} do you want?\n"
                f"📦 Minimum: 10\n"
                f"💰 Rate: ₹{price:.5f} per 100"
            )
        else:
            bot.send_message(message.chat.id, "❌ Invalid link! Please send a valid Telegram link starting with https://t.me/")
    
    elif state_info['state'] == 'awaiting_quantity':
        try:
            quantity = int(message.text)
            
            if quantity < 10:
                bot.send_message(message.chat.id, "❌ Minimum order is 10. Please enter 10 or more.")
                return
            
            service_type = state_info['service']
            price_per_100 = VIEW_PRICE if service_type == 'views' else REACTION_PRICE
            total_cost = (price_per_100 * quantity) / 100
            
            user_balance = user_balances.get(user_id, 0.0)
            
            # Create confirmation keyboard
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(
                types.InlineKeyboardButton("✅ Confirm Order", callback_data=f"confirm_{service_type}_{quantity}_{total_cost}"),
                types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_order")
            )
            
            state_info['total_cost'] = total_cost
            state_info['quantity'] = quantity
            
            bot.send_message(
                message.chat.id,
                f"📋 Order Summary:\n\n"
                f"📊 Service: Telegram {service_type.capitalize()}\n"
                f"🔗 Link: {state_info['link']}\n"
                f"📦 Quantity: {quantity}\n"
                f"💰 Cost: ₹{total_cost:.2f}\n"
                f"👛 Your Balance: ₹{user_balance:.2f}\n\n"
                f"Please confirm your order:",
                reply_markup=keyboard
            )
            
        except ValueError:
            bot.send_message(message.chat.id, "❌ Please enter a valid number (e.g., 100, 500, 1000)")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    
    if call.data == "cancel_order":
        bot.delete_message(chat_id, message_id)
        if user_id in user_states:
            del user_states[user_id]
        bot.send_message(chat_id, "❌ Order cancelled.", reply_markup=main_keyboard())
        bot.answer_callback_query(call.id)
    
    elif call.data.startswith("confirm_"):
        parts = call.data.split("_")
        if len(parts) >= 4:
            service_type = parts[1]
            quantity = int(parts[2])
            total_cost = float(parts[3])
            
            if user_id not in user_states:
                bot.answer_callback_query(call.id, "Session expired. Please start again.")
                return
            
            user_balance = user_balances.get(user_id, 0.0)
            
            if user_balance < total_cost:
                bot.answer_callback_query(call.id, "❌ Insufficient balance!")
                bot.send_message(
                    chat_id,
                    f"❌ Insufficient Balance!\n"
                    f"Required: ₹{total_cost:.2f}\n"
                    f"Available: ₹{user_balance:.2f}",
                    reply_markup=main_keyboard()
                )
                return
            
            # Process the order
            link = user_states[user_id]['link']
            service_id = 14195 if service_type == 'views' else 15644
            
            api_url = f"https://smmashu.com/api/v1?key={SMM_API_KEY}&action=add&service={service_id}&link={link}&quantity={quantity}"
            
            try:
                response = requests.get(api_url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'order' in data:
                        user_balances[user_id] -= total_cost
                        
                        # Delete the confirmation message
                        bot.delete_message(chat_id, message_id)
                        
                        # Send success message
                        success_msg = f"""✅ Order Placed Successfully!

📊 Service: Telegram {service_type.capitalize()}
🔗 Link: {link}
📦 Quantity: {quantity}
💰 Cost: ₹{total_cost:.2f}
👛 Remaining Balance: ₹{user_balances[user_id]:.2f}

🆔 Order ID: {data.get('order', 'N/A')}
⏱️ Delivery: Started (usually within minutes)

Thank you for your order!"""
                        
                        bot.send_message(chat_id, success_msg)
                        
                        # Notify admin
                        try:
                            admin_msg = f"🆕 New Order!\n\nUser: {user_id}\nService: {service_type}\nQuantity: {quantity}\nAmount: ₹{total_cost:.2f}"
                            bot.send_message(ADMIN_ID, admin_msg)
                        except:
                            pass
                    else:
                        bot.answer_callback_query(call.id, "❌ Order failed. Try again.")
                        bot.send_message(chat_id, "❌ Failed to create order. Please try again later.")
                else:
                    bot.answer_callback_query(call.id, "❌ API Error")
                    bot.send_message(chat_id, "❌ Service temporarily unavailable. Please try again.")
            
            except Exception as e:
                print(f"API Error: {e}")
                bot.answer_callback_query(call.id, "❌ Connection Error")
                bot.send_message(chat_id, "❌ Service temporarily unavailable. Please try again.")
            
            # Clean up user state
            if user_id in user_states:
                del user_states[user_id]
            
            bot.send_message(chat_id, "Main Menu", reply_markup=main_keyboard())
        
        bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id
    
    if message.caption and 'ss' in message.caption.lower():
        try:
            # Forward to admin
            bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
            bot.send_message(
                ADMIN_ID,
                f"📸 Payment SS received from User ID: {user_id}\n"
                f"Name: {message.from_user.first_name}\n"
                f"Username: @{message.from_user.username}"
            )
            
            bot.send_message(
                message.chat.id,
                "✅ Payment screenshot received!\n"
                "Our team will verify and add balance within 15-30 minutes.\n"
                "Thank you! 🙏"
            )
        except Exception as e:
            bot.send_message(message.chat.id, "❌ Failed to forward screenshot. Please contact admin directly.")

# Admin commands
@bot.message_handler(commands=['users'])
def list_users(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    
    if not user_balances:
        bot.send_message(message.chat.id, "No users yet.")
        return
    
    users_list = "📊 Registered Users:\n\n"
    for uid, balance in user_balances.items():
        users_list += f"🆔 {uid}: ₹{balance:.2f}\n"
    
    bot.send_message(message.chat.id, users_list)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Usage: /broadcast <message>")
        return
    
    broadcast_msg = parts[1]
    success = 0
    failed = 0
    
    for user_id in user_balances.keys():
        try:
            bot.send_message(user_id, f"📢 Announcement:\n\n{broadcast_msg}")
            success += 1
        except:
            failed += 1
    
    bot.send_message(message.chat.id, f"✅ Broadcast complete!\nSuccess: {success}\nFailed: {failed}")

if __name__ == '__main__':
    print("Bot is running...")
    print(f"Admin ID: {ADMIN_ID}")
    bot.polling(none_stop=True, interval=0, timeout=20)