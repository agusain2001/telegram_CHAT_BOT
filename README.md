# Telegram_CHAT_BOT: Marketing Assistant Bot

Telegram_CHAT_BOT is an AI-powered marketing assistant bot designed to help businesses optimize their marketing strategies. It uses the Google Gemini API for natural language responses and provides PPC (Pay-Per-Click) industry benchmark trends by scraping data from Databox. The bot also generates business-specific keywords based on user inputs.

## Features

1. **Conversational Marketing Assistant:**
   - Collects business details like industry, objectives, website, social media platforms, PPC campaigns, audience, and target location through an interactive chat interface.

2. **PPC Benchmark Trends:**
   - Scrapes PPC industry benchmark data from Databox and provides insights such as CPC (Cost Per Click) and CTC (Cost To Customer) for specific industries.

3. **FAQ Responder:**
   - Answers marketing-related questions using the Google Gemini API.

4. **Keyword Generator:**
   - Suggests relevant business keywords based on user-provided inputs.

## Technologies Used

- **Python Libraries:**
  - `bs4` and `requests`: For web scraping.
  - `google.generativeai`: To interact with the Google Gemini API.
  - `telegram` and `telegram.ext`: For Telegram bot functionalities.

- **External APIs:**
  - Google Gemini API for AI-generated FAQ responses.

## Prerequisites

- Python 3.9 or later
- A valid Telegram Bot token from [Telegram BotFather](https://core.telegram.org/bots#botfather)
- Google Gemini API key

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure the environment variables:
   - Add your Telegram Bot Token and Google Gemini API key to the `config.py` file.

   ```python
   TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
   GEMINI_API_KEY = "your-google-gemini-api-key"
   ```

4. Run the bot:

   ```bash
   python bot.py
   ```

## How to Use

1. Start the bot by sending the `/start` command in Telegram.
2. Follow the bot's questions to provide your business details.
3. Use the `/trends` command followed by your industry name to fetch PPC trends. Example:

   ```
   /trends Retail
   ```

4. Use the `/faq` command to ask marketing-related questions. Example:

   ```
   /faq How do I improve my ad performance?
   ```

## Bot Commands

- `/start` - Start the conversation with the bot.
- `/trends <industry>` - Fetch PPC trends for a specific industry.
- `/faq <question>` - Ask a marketing-related question.

## File Structure

- `bot.py`: Main script for running the bot.
- `config.py`: Configuration file for API keys.
- `utils/keyword_generator.py`: Utility script for generating keywords.

## Limitations

- Data scraping is dependent on the structure of the target website (Databox). Changes to the website may break functionality.
- Google Gemini API usage is limited by API quotas and requires a valid API key.

## Future Enhancements

- Add support for more marketing tools and data sources.
- Enable sentiment analysis for better FAQ responses.
- Implement advanced error handling and logging.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

Developed with ❤️ by Ashish Gusain

