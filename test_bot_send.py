from telegram import Bot

TELEGRAM_TOKEN = '7443495110:AAG1u7E8ZQnmgGuzHpvpbm7wLbjw1B7e-qg'
CHAT_ID = '6641217424'  # 这是你的 Chat ID

bot = Bot(token=TELEGRAM_TOKEN)

try:
    bot.send_message(chat_id=CHAT_ID, text="✅ 测试通知：如果你看到这条消息，Bot 已成功连接。")
    print("消息发送成功！请查看 Telegram。")
except Exception as e:
    print(f"❌ 消息发送失败，错误信息：{e}")
