import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def amazon_scraper(search_query):
    search_query = search_query.replace(" ", "+")
    url = f"https://www.amazon.in/s?k={search_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/113.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    for _ in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, headers=headers)  # No proxies parameter
            response.raise_for_status()
            break
        except requests.exceptions.HTTPError as e:
            if response.status_code == 503:
                print("Amazon is blocking the request. Retrying...")
                time.sleep(random.uniform(5, 10))  # Random delay between retries
            else:
                print(f"Request failed: {e}")
                return

    soup = BeautifulSoup(response.content, "html.parser")

    titles, prices, ratings = [], [], []

    results = soup.find_all("div", {"data-component-type": "s-search-result"})[:10]
    for item in results:
        title_tag = item.h2
        price_whole = item.find("span", class_="a-price-whole")
        price_fraction = item.find("span", class_="a-price-fraction")
        rating_tag = item.find("span", class_="a-icon-alt")

        if title_tag and price_whole:
            title = title_tag.text.strip()
            price = price_whole.text.strip()
            if price_fraction:
                price += price_fraction.text.strip()
            price = price + " ₹"
            rating = rating_tag.text.strip() if rating_tag else "No Rating"

            titles.append(title)
            prices.append(price)
            ratings.append(rating)

        # Add a random delay between processing items
        time.sleep(random.uniform(1, 3))

    if titles:
        df = pd.DataFrame({
            "Title": titles,
            "Price": prices,
            "Rating": ratings
        })

        df.to_excel("amazon_products.xlsx", index=False)
        print("Amazon data saved to 'amazon_products.xlsx'")
    else:
        print("No products found. Please try a different search query.")

if __name__ == "__main__":
    keyword = input("Enter product to search: ")
    amazon_scraper(keyword)
    print("✅ amazon_products.xlsx created!")