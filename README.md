# RedBoot: The AI Cybersecurity Assistant for Telegram


![Logo](assets/logo.png)


RedBoot is an advanced chatbot running on Telegram that provides answers to questions about cybersecurity. It uses Google's Gemini AI large language model to provide information about vulnerabilities, protective measures, and security tools.


## 🚀 Key Features

- **Contextual Conversations:** The bot continues to maintain the last few messages in your chat which means answers will both be more accurate and relevant. 
- **Streaming Replies:** The way the reply is constructed is so that it appears, as if it is being tepidly typed, all together to give the user a smoother experience.
- **Wide-Reaching Knowledge:** It covers a wide range of topics, including XSS, SQL injection, network security, cryptography, and a multitude more.
- **AI Persona:** The bot takes on the persona of a knowledgeable cybersecurity expert at the developer's command.
- **Session Management:** It has a `/clear` command to wipe the conversation memory.
- **Domain/IP Reputation Check (`/check`):** Instantly check for the reputation of any domain or IP address against VirusTotal's malware reputation, as reported by security vendors.
- **Daily News Digest (`/subscribe`):** Subscribe, for free, to receive a daily digest of the most recent events in the security world, parsed from the RSS feed of The Hacker News.
- **Multilingual:** This bot supports English and Russian languages, and supports switching between them at any time using `/language`.
- **Admin Commands for Owner Only:** The bot has privileged commands, such as `/stats` to look at the subscriber information, and `/testdigest` to trigger the news digest as the original user for testing.

## 🛠️ Tech Stack

- **Programming Language:** Python
- **Telegram Library:** `python-telegram-bot`
- **AI Model:** Google Gemini 1.5 Flash
- **External APIs:** VirusTotal API, CIRCL.LU CVE Search
- **Scheduling:** APScheduler for daily tasks
- **Data Parsing:** BeautifulSoup, Feedparser
- **Database:** SQLite for subscriber management
- **Deployment:** Oracle Cloud (Always Free Tier)

## Spotlight Feature: Hybrid CVE Analysis

The `/cve` command is RedBoot's core utility and works quickly because RedBoot retrieves data in two distinct steps.

1.  **Primary API Call:** The bot first communicates with the fast API located at `cve.circl.lu`, fetching structured JSON data. The bot will also return quickly on any of the described known vulnerabilities.

2.  **Web Scraping Fallback:** If the first API does not return a complete description or a current CVSS v3 score, the bot will set up and launch a web scraper. The bot will grab the official NIST National Vulnerability Database page, it will parse the HTML with BeautifulSoup, and then intelligently grab the missing data, with v2 and v3 scores as well as the tried and tested summary for the common vulnerabilities in the original NIST data format.

And, finally, the technical summary is sent off to the Gemini AI to produce an accurate, concise explanation of what the vulnerability does and what risks it may have. This gives you the fastest overall response and the best information that is accurate and complete.

## CHALLENGES & SOLUTIONS

During the course of development, I encountered a few issues that were crucial towards the development of the completion of the project.

1.  **AI Formatting was problematic:** The bot would return plaintext in very strange formats not supported by Telegram itself, which would crash the bot or cause the bot to have janky text content. So I created a two-step processing pipeline using the code language Python. The first step is a "translator" module, which identifies any Markdown syntax ( i.e. (**bold** and `` `code` `` ) ) and translates it to full HTML (i.e. <b>bold</b> and <code>code</code>). The second step is a "sanitizer" module that sanitizes the HTML by only allowing Telegram tags and sanitizing special characters. This allowed me to assure that the ultimate output connectivity formatting was 100% reliable regardless of the AI's inconsistent rendering.

2.  **API Rate limits & Errors:** When I saw the bot crash because it had consumed the free-tier's rate limits on the Gemini API, my heart sank. I'd thought that I had improved my exception handler block (`try...except`) sufficiently to catch these behaviours.  I was able to still add exception handling but for the specific API errors to avoid failing at all. Now, when the bot gets rate limited, it can inform the user of the temporary problems (i.e., hitting a rate limit), and just carry on running.

## ⚙️ How to Run

1.  Clone the repository:
    ```bash
    git clone [https://github.com/nasibius/redboot](https://github.com/nasibius/redboot)
    cd redboot
    ```
2.  Install dependencies:
    ```bash
    pip install requirements.txt
    ```
3.  Set up your environment variables. You will need:
    - `TELEGRAM_TOKEN`
    - `GEMINI_API_KEY`
    - `VIRUSTOTAL_API_KEY`
    - `OWNER_ID` (your personal Telegram User ID)
4.  Run the script:
    ```bash
    python3 bot_ai.py
    ```

## Additional Info
Please note that the comments in the file are mostly in Russian. Additionally, this project is under active development, so more and more features will be added in the near future!
