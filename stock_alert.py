import requests
from twilio.rest import Client
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

load_dotenv()

STOCK_API_KEY = os.getenv("STOCK_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

stock_params ={
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}
# --------STEP-1: Work with the Stock API----------
# Get yesterday's closing stock price
response = requests.get(STOCK_ENDPOINT, params=stock_params)
data = response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data["4. close"]
# print(yesterday_closing_price)

# Get day before yesterday's closing stock price
day_before_yesterday_data = data_list[1]
day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]
# print(day_before_yesterday_closing_price)

# Get the positive difference between the closing prices
difference = round(float(yesterday_closing_price) - float(day_before_yesterday_closing_price), 2)
# print(difference)
up_down = None
if difference>0:
    up_down = "🔺"
else:
    up_down = "🔻"

# Work out the percentage difference
diff_percent = round((difference/float(yesterday_closing_price)) * 100)
# print(diff_percent)

# ------------STEP-2: Fetch the news articles----------
# Use the news API to get articles
if abs(diff_percent) > 2:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]

    # Get the first three articles
    three_articles = articles[:3]

# -----------STEP-3: Send the Message-----------
    # -------Using Twilio-----------------
    # Create a new list of the first 3 articles heading and description using list comprehension
    formatted_articles = [f"{STOCK_NAME}: {up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]

    # Send the message via Twilio
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_="+16813083548", # Bhattacharjeerenesha32@gamil.com
            to="+91 96785 89928",
        )
        print(f"Message sent: {message.sid}")

    # ------------Using Gmail------------
        with smtplib.SMTP("smtp.gmail.com", 587) as connect:
            connect.starttls()
            connect.login(EMAIL, PASSWORD)
            email_msg = MIMEText(article)
            email_msg["Subject"] = f"{STOCK_NAME} Stock Alert"
            email_msg["From"] = EMAIL
            email_msg["To"] = RECEIVER_EMAIL
            connect.send_message(email_msg)
            print(f"Email sent to: {RECEIVER_EMAIL} ")
