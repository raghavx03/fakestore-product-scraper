from serpapi import GoogleSearch
import pandas as pd

def get_flipkart_products(query, api_key):
    params = {
        "engine": "google",
        "q": f"{query} site:flipkart.com",
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    products = []
    for result in results.get("organic_results", []):
        title = result.get("title")
        link = result.get("link")
        snippet = result.get("snippet", "")
        products.append({"Title": title, "Link": link, "Snippet": snippet})

    if products:
        df = pd.DataFrame(products)
        df.to_excel("flipkart_results.xlsx", index=False)
        print("✅ Data saved to 'flipkart_results.xlsx'")
    else:
        print("❌ No products found.")

if __name__ == "__main__":
    api_key = "db55a1d508ef02b90ec6c9af477265f65fcc1891b407c566a659fd5695259c77"
    keyword = input("Enter product to search on Flipkart: ")
    get_flipkart_products(keyword, api_key)