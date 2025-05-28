from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import re

def clean_text(text):
    return text.strip().replace('\n', ' ') if text else ''

def clean_price(price_str):
    if not price_str:
        return 0.0
    price_str = price_str.replace("₹", "").replace(",", "").strip()
    price_num = re.findall(r'[\d.]+', price_str)
    return float(price_num[0]) if price_num else 0.0

def scrape_flipkart_details(url, driver):
    try:
        driver.get(url)
        time.sleep(3)

        title = clean_text(driver.find_element(By.CSS_SELECTOR, "span.B_NuCI").text)

        try:
            price_raw = clean_text(driver.find_element(By.CSS_SELECTOR, "div._30jeq3._16Jk6d").text)
            price = clean_price(price_raw)
        except:
            price = 0.0

        try:
            rating = clean_text(driver.find_element(By.CSS_SELECTOR, "div._3LWZlK").text)
        except:
            rating = ""

        try:
            discount = clean_text(driver.find_element(By.CSS_SELECTOR, "div._3Ay6Sb span").text)
        except:
            discount = ""

        return {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Discount": discount,
            "URL": url,
            "Source": "Flipkart"
        }

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

def main():
    df = pd.read_excel("flipkart_results.xlsx")
    # Check if flipkart_results.xlsx is empty or invalid
    if df.empty or "Link" not in df.columns:
        print("⚠️ No links found in flipkart_results.xlsx. Trying to regenerate links...")

        service = Service("/opt/homebrew/bin/chromedriver")  # ✅ Update path if needed
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)

        driver.get("https://www.flipkart.com/laptops-store")
        time.sleep(3)
        for _ in range(3):  # scroll down 3 times
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        anchors = driver.find_elements(By.CSS_SELECTOR, "a")
        product_links = set()
        for a in anchors:
            link = a.get_attribute("href")
            if link and "/p/" in link and "flipkart.com" in link:
                product_links.add(link)

        driver.quit()
        print(f"Found {len(product_links)} unique product links.")
        df = pd.DataFrame({"Link": list(product_links)})
        df.to_excel("flipkart_results.xlsx", index=False)
    urls = df["Link"].dropna().tolist()

    service = Service("/usr/local/bin/chromedriver")  # ✅ Update path if needed
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)

    results = []
    for url in urls:
        print(f"🔍 Scraping: {url}")
        data = scrape_flipkart_details(url, driver)
        if data:
            results.append(data)

    driver.quit()

    df_out = pd.DataFrame(results)
    df_out.to_excel("flipkart_detailed_products.xlsx", index=False)
    print("✅ Saved to flipkart_detailed_products.xlsx")

def merge_data():
    amazon_df = pd.read_excel("products_amazon.xlsx")
    flipkart_df = pd.read_excel("flipkart_detailed_products.xlsx")

    # Add 'Source' column if missing
    if 'Source' not in amazon_df.columns:
        amazon_df['Source'] = 'Amazon'

    if 'Discount' not in amazon_df.columns:
        amazon_df['Discount'] = ''

    amazon_df = amazon_df.rename(columns={
        'Price (₹)': 'Price',
        'Product Link': 'URL'
    })

    # Align both dataframes
    amazon_df = amazon_df[['Title', 'Price', 'Rating', 'Discount', 'URL', 'Source']]
    flipkart_df = flipkart_df[['Title', 'Price', 'Rating', 'Discount', 'URL', 'Source']]

    combined_df = pd.concat([amazon_df, flipkart_df], ignore_index=True)
    combined_df.to_excel("combined_products.xlsx", index=False)
    print("✅ All data combined into 'combined_products.xlsx'")

if __name__ == "__main__":
    main()
    merge_data()