import os
import language_tool_python
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Initialize LanguageTool Public API for English
# (Does not require Java on Railway)
tool = language_tool_python.LanguageToolPublicAPI('en-US')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    km_welcome = (
        "សួស្តី! ខ្ញុំជា ប៊តត្រួតពិនិត្យអក្ខរាវិរុទ្ធ (Grammar Checker Bot) 📝\n\n"
        "សូមផ្ញើសារ ឬល្បះជាភាសាអង់គ្លេសមកកាន់ខ្ញុំ ខ្ញុំនឹងជួយពិនិត្យ និងកែសម្រួលវេយ្យាករណ៍ជូនអ្នក!\n\n"
        "បញ្ជា (Commands):\n"
        "/start - ចាប់ផ្តើមឡើងវិញ\n"
        "/help - របៀបប្រើប្រាស់"
    )
    await update.message.reply_text(km_welcome)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    km_help = (
        "ℹ️ **របៀបប្រើប្រាស់:**\n\n"
        "១. វាយ ឬផ្ញើអត្ថបទភាសាអង់គ្លេសដែលអ្នកចង់ត្រួតពិនិត្យ។\n"
        "២. Bot នឹងបង្ហាញកំហុសវេយ្យាករណ៍ និងផ្តល់នូវអត្ថបទដែលបានកែប្រែរួចរាល់។"
    )
    await update.message.reply_text(km_help, parse_mode="Markdown")

async def check_grammar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()

    if not user_text:
        await update.message.reply_text("❌ សូមផ្ញើអត្ថបទជាភាសាអង់គ្លេសដើម្បីពិនិត្យ។")
        return

    # Send typing status indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Check grammar matches and get corrected text
        matches = tool.check(user_text)
        
        if not matches:
            response = "✅ **អត្ថបទរបស់អ្នកត្រឹមត្រូវឥតខ្ចោះ! គ្មានកំហុសវេយ្យាករណ៍ទេ។**"
        else:
            corrected_text = tool.correct(user_text)
            
            # Format suggestions overview
            error_details = []
            for match in matches[:3]: # Limit to top 3 issues for readability
                rule_msg = match.message
                error_details.append(f"• {rule_msg}")
            
            errors_str = "\n".join(error_details)

            response = (
                "🔍 **លទ្ធផលនៃការត្រួតពិនិត្យវេយ្យាករណ៍:**\n\n"
                f"❌ **អត្ថបទដើម:**\n`{user_text}`\n\n"
                f"✅ **អត្ថបទដែលបានកែប្រែ:**\n`{corrected_text}`\n\n"
                f"📌 **ចំណុចត្រូវកែសម្រួល ({len(matches)}):**\n{errors_str}"
            )

        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception:
        await update.message.reply_text("⚠️ មានបញ្ហាក្នុងការត្រួតពិនិត្យវេយ្យាករណ៍។ សូមព្យាយាមម្តងទៀត!")

if __name__ == '__main__':
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN missing!")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_grammar))

    print("Grammar Checker Bot is running...")
    app.run_polling()
