from bs4 import BeautifulSoup
from requests import get
from typing import Final
import re
import google.generativeai as genai
from telegram import Update, BotCommand
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ConversationHandler,
    ApplicationBuilder,
)
from config import TELEGRAM_BOT_TOKEN, GEMINI_API_KEY  # Use GEMINI_API_KEY
from utils.keyword_generator import generate_keywords

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Constants
MAIN_LINK: Final = "https://databox.com/ppc-industry-benchmarks"
HTML_TAG_WHERE_DATA_IS_STORED: Final = "tbody"

GOOGLE_ADS_IMPRESSIONS_INDEX: Final = 0
FACEBOOK_IMPRESSIONS_INDEX: Final = 1
LINKEDIN_IMPRESSIONS_INDEX: Final = 2

GOOGLE_ADS_CLICKS_INDEX: Final = 3
FACEBOOK_ADS_CLICKS_INDEX: Final = 4
LINKEDIN_ADS_CLICKS_INDEX: Final = 5

GOOGLE_ADS_CTR_INDEX: Final = 6
FACEBOOK_ADS_CTR_INDEX: Final = 7
LINKEDIN_ADS_CTR_INDEX: Final = 8

GOOGLE_ADS_CPC_INDEX: Final = 9
FACEBOOK_ADS_CPC_INDEX: Final = 10
LINKEDIN_ADS_CPC_INDEX: Final = 11

# Conversation states
INDUSTRY, OBJECTIVE, WEBSITE, SOCIAL_MEDIA, PPC, AUDIENCE, LOCATION = range(7)

# Caching for repeated requests
cached_trends = {}

Response__ = get(MAIN_LINK)
Soup__ = BeautifulSoup(Response__.content, "html.parser")
Content__ = Soup__.find_all(HTML_TAG_WHERE_DATA_IS_STORED)

def RefineValue(__value: str) -> float:
    if not __value:
        return 0

    value_to_multiply_with = 1
    if __value[-1].lower() == 'k':
        value_to_multiply_with = 1000
    elif __value[-1].lower() == 'm':
        value_to_multiply_with = 1000000

    final_value = ""
    for i in __value:
        if i == '$':
            continue
        if i != '.' and not i.isdigit():
            break
        final_value += i

    if not final_value:
        return 0
    return float(final_value) * value_to_multiply_with


def ExtractData(__data_index: int) -> dict[str, float]:
    if __data_index < 0 or __data_index >= len(Content__):
        raise IndexError(f"Index not within range. The length of Content is limited within 0 and {len(Content__) - 1}")

    data_dict = {}
    rows = Content__[__data_index].find_all('tr')

    for row in rows[1:]:  # skipping the header row
        columns = row.find_all('td')
        key = columns[0].text.strip()
        value = columns[1].text.strip()
        data_dict[key] = RefineValue(value)
    return data_dict


# CTC formula = (Cpc*clicks)+other_cost
def CalculateCTC(__industry_name: str) -> float:
    cpc = 0
    for i in range(9, 12):
        cpc += ExtractData(i).get(__industry_name, 0)

    clicks = 0
    for i in range(3, 6):
        clicks += ExtractData(i).get(__industry_name, 0)

    return cpc * clicks

# FAQ responder
def respond_to_faq(question):
    """
    Uses Google Gemini to generate a response for a marketing FAQ.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')  # Initialize Gemini model
        prompt = f"Answer this marketing question: {question}"
        response = model.generate_content(prompt)  # Call Gemini to generate a response

        if response.text:
            return response.text.strip()
        else:
            return "Sorry, I couldn't generate a response. Please try again later."

    except Exception as e:
        # Log the error and return a fallback message
        print(f"Error: {e}")
        return "Sorry, I couldn't generate a response. Please try again later."


def fetch_trends(industry: str) -> str:
    """
    Fetches specific marketing trends (e.g., CPC, CTC) for a given industry.
    Scrapes PPC benchmark data from databox.com.
    """

    try:
        cpc_value = ExtractData(GOOGLE_ADS_CPC_INDEX).get(industry, "Not Found")
        ctc_value = CalculateCTC(industry)

        if cpc_value != "Not Found":
            trends_data = f"Trends for {industry}:\n"
            trends_data += f"CPC: {cpc_value:.2f}\n"
            trends_data += f"CTC: {ctc_value:.2f}\n"  # Format CTC as a float
        else:
           trends_data = f"No specific trends found for the industry '{industry}'."
    except Exception as e:
      print(f"Error fetching trends: {e}")
      return "Unable to fetch trends at this time. Please try again later."
    
    return trends_data


# Conversation handlers (no changes needed)
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Welcome to the Marketing Bot! Let's get started with some questions.\n"
        "What industry is your business in?"
    )
    return INDUSTRY

async def collect_industry(update: Update, context: CallbackContext) -> int:
    context.user_data['industry'] = update.message.text
    await update.message.reply_text("What's your business objective?")
    return OBJECTIVE

async def collect_objective(update: Update, context: CallbackContext) -> int:
    context.user_data['objective'] = update.message.text
    await update.message.reply_text("Do you have a website? If yes, please provide the URL.")
    return WEBSITE

async def collect_website(update: Update, context: CallbackContext) -> int:
    context.user_data['website'] = update.message.text
    await update.message.reply_text("Do you have any social media platforms? If yes, provide the URL(s).")
    return SOCIAL_MEDIA

async def collect_social_media(update: Update, context: CallbackContext) -> int:
    context.user_data['social_media'] = update.message.text
    await update.message.reply_text("Do you use PPC campaigns? If yes, provide details.")
    return PPC

async def collect_ppc(update: Update, context: CallbackContext) -> int:
    context.user_data['ppc'] = update.message.text
    await update.message.reply_text("Who are you trying to reach? (e.g., young adults, professionals)")
    return AUDIENCE

async def collect_audience(update: Update, context: CallbackContext) -> int:
    context.user_data['audience'] = update.message.text
    await update.message.reply_text("What location would you like to target?")
    return LOCATION

async def collect_location(update: Update, context: CallbackContext) -> int:
    context.user_data['location'] = update.message.text
    keywords = generate_keywords(context.user_data)
    await update.message.reply_text(f"Here are some keywords for your business:\n{', '.join(keywords)}")
    return ConversationHandler.END

# Command handlers (no changes needed)
async def trends(update: Update, context: CallbackContext) -> None:
    industry = context.args[0] if context.args else None
    if not industry:
        await update.message.reply_text("Please specify an industry to fetch trends. Example: /trends Retail")
        return
    trends_data = fetch_trends(industry)
    await update.message.reply_text(f"{trends_data}")


async def faq(update: Update, context: CallbackContext) -> None:
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("Please ask a question. Example: /faq How do I improve my ad performance?")
        return
    answer = respond_to_faq(question)
    await update.message.reply_text(answer)

# Main function to start the bot (no changes needed)
def main() -> None:

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        INDUSTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_industry)],
        OBJECTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_objective)],
        WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_website)],
        SOCIAL_MEDIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_social_media)],
        PPC: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_ppc)],
        AUDIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_audience)],
        LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_location)],
    },
    fallbacks=[CommandHandler('start', start)],)
    
    application.add_handler(conv_handler)

    application.add_handler(CommandHandler('trends', trends))
    
    application.add_handler(CommandHandler('faq', faq))
    
    application.run_polling(poll_interval=0.5)

if __name__ == '__main__':
    main()