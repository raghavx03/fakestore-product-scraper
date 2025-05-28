import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import re

def clean_price(price_str):
    price_str = price_str.replace("₹", "").replace(",", "").strip()
    price = re.findall(r"[\d.]+", price_str)
    return float(price[0]) if price else 0.0

def scrape_flipkart_search(query, limit=30):
    search_query = query.replace(" ", "%20")
    url = f"https://www.flipkart.com/search?q={search_query}"

    service = Service("/opt/homebrew/bin/chromedriver")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(3)

    products = []

    items = driver.find_elements(By.CSS_SELECTOR, "div._1AtVbE")[:limit]

    for box in items:
        try:
            title = box.find_element(By.CSS_SELECTOR, "div._4rR01T").text
        except:
            continue  # Skip empty box

        try:
            price = box.find_element(By.CSS_SELECTOR, "div._30jeq3").text
            price = clean_price(price)
        except:
            price = 0.0

        try:
            rating = box.find_element(By.CSS_SELECTOR, "div._3LWZlK").text
        except:
            rating = ""

        try:
            link = box.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            link = ""

        products.append({
            "Title": title,
            "Price": price,
            "Rating": rating,
            "URL": link,
            "Source": "Flipkart"
        })

    driver.quit()
    return products

# 🔹 MAIN EXECUTION
if __name__ == "__main__":
    product = input("Enter product to search on Flipkart: ")
    results = scrape_flipkart_search(product)

    if results:
        df = pd.DataFrame(results)
        df.to_excel("flipkart_detailed_products.xlsx", index=False)
        print("✅ Data saved to 'flipkart_detailed_products.xlsx'")
    else:
        print("❌ No products found.")