import requests
import pandas as pd

def fetch_products():
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = []
        for item in data:
            products.append({
                "Title": item['title'],
                "Price": item['price'],
                "Rating": item['rating']['rate'],
                "Description": item['description'],
                "Image": item['image']
            })
        return products
    else:
        print("❌ Failed to fetch data from API.")
        return []

if __name__ == "__main__":
    results = fetch_products()
    if results:
        df = pd.DataFrame(results)
        df.to_excel("fakestore_products.xlsx", index=False)
        print("✅ Data saved to 'fakestore_products.xlsx'")
        print(f"🔢 Total products: {len(results)}")
    else:
        print("❌ No products found.")
