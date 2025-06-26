# RedBoot - AI Cybersecurity Assistant for Telegram

![Logo](logo.jpg) RedBoot is a sophisticated chatbot on Telegram that answers questions about cybersecurity. It is built with Google's Gemini AI large language model and provides details on vulnerabilities, methods of protection, and security tools.

## Core Features

- Context-based replies: The bot can remember recent chat history, so the answers are more accurate and relevant.
- Smooth streaming replies: Responses will appear to be typed smoothly, with a "typing" effect to improve the user's experience.
- Wide reaching knowledge: It covers a wide range of topics, including XSS, SQL injection, network security, cryptography, and a multitude more.
- AI persona: The bot takes on the persona of a host of a knowledgeable cybersecurity expert at the developer's command.
- Session management: It has a `/clear` command to wipe the memory.

## Tech Stack

- Programming Language: Python
- Telegram Library: `python-telegram-bot`
- AI tool: Google Gemini 1.5 Flash
- Where it's hosted: not currently

## CHALLENGES & SOLUTIONS

During the course of development, I encountered a few issues that were crucial towards the development of the completion of the project.

1. AI Formatting was problematic: The bot would return plaintext in very strange formats not supported by Telegram itself, which would crash the bot or cause the bot to have janky text content. So I created a two step processing pipeline using the code language Python. The first step is a "translator" module, which identifies any Markdown syntax ( i.e. (**bold** and `` `code` `` ) ) and translates it to full HTML (i.e. <b>bold</b> and <code>code</code>). The second step is a "sanitizer" module that sanitizes the HTML by only allowing Telegram tags and sanitizing special characters. This allowed me to assure that the ultimate output connectivity formatting was 100% reliable regardless of the AI's inconsistent rendering.

2.  API Rate limits & Errors: Seeing the bot crash because it had eaten the free-tier's rate limits on the Gemini API was disappointing. I thought I had improved my exception handler block (`try...except`) to catch these behaviours. I was still able to add exception handling but for catching these specific API errors to avoid crashing at all. Instead, my bot can inform the user of the temporary problems (e.g. hitting a rate limit) and simply carry on running.

## How to Run

1.  Clone the repository:
    git clone https://github.com/yaqness/redboot_tgbot.git
    cd RedBoot
2.  Install dependencies: pip install python-telegram-bot google-generativeai
3.  Set up your environment variables. You will need to change the following: `TELEGRAM_TOKEN` and `GEMINI_API_KEY`
4.  Run the script: python3 bot_ai.py

## Additional info
Please note that the comments in the file are mostly in Russian. Additionally, this project is under active development, so more and more features will be added in the near future!
