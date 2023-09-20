import requests
from twilio.rest import Client

STOCK = 'TSLA'
COMPANY_NAME = 'Tesla Inc'
STOCK_ENDPOINT = 'https://www.alphavantage.co/query'
STOCK_API_KEY = 'W8O22CET3WHACUHR'
NEWS_ENDPOINT = 'https://newsapi.org/v2/everything'
NEWS_API_KEY = 'e4e3b8191a5149d69f71c3eae97b0ce0'
TWILIO_ACCOUNT_SID = 'ACa2e5c9541d9bc7e55e5eb8f083c85415'
TWILIO_AUTH_TOKEN = 'd30eafd2879e0d4b705788a0c6bfcd98'
TWILIO_PHONE_NUMBER = '+16606285102'
MY_PHONE_NUMBER = '+40753640800'

# STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
stock_params = {
    'function': 'TIME_SERIES_INTRADAY',
    'symbol': STOCK,
    'interval': '60min',
    'apikey': STOCK_API_KEY
}

stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
stock_data = stock_response.json()['Time Series (60min)']
stock_data_list = [value for (key, value) in stock_data.items()]

yesterday_data = stock_data_list[15]
yesterday_closing_price = yesterday_data['4. close']

day_before_data = stock_data_list[16]
day_before_closing_price = day_before_data['4. close']

difference = float(yesterday_closing_price) - float(day_before_closing_price)

if difference < 0:
    trend = '🔺'
else:
    trend = '🔻'

difference_percent = round((abs(difference) / float(yesterday_closing_price)) * 100)

# STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 
if difference_percent >= 1:
    news_params = {
        'q': COMPANY_NAME,
        'searchIn': 'title,description,content',
        'language': 'en',
        'sortBy': 'relevancy,popularity',
        'apiKey': NEWS_API_KEY
    }

    news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_data = news_response.json()
    articles_list = news_data['articles']
    top_articles = articles_list[:3]

    # STEP 3: Use https://www.twilio.com
    # Send a seperate message with the percentage change and each article's title and description to your phone number.
    # Optional: Format the SMS message like this:
    """
    TSLA: 🔺2%
    Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
    Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required 
    to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, 
    near the height of the coronavirus market crash.
    or
    "TSLA: 🔻5%
    Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
    Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required 
    to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, 
    near the height of the coronavirus market crash.
    """
    formatted_articles = [f"{STOCK}: {trend}{difference_percent}%\n" 
                          f"Headline: {article['title']}.\n"
                          f"Brief: {article['description']}" for article in top_articles]

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    for formatted_article in formatted_articles:
        message = client.messages.create(
            body=formatted_article,
            from_=TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER
        )
