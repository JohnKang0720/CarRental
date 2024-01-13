from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import asyncio

#TODO
#implement async

car_names = []#
prices = []#
ratings = []#
reviews = []#
used_mi = []#
locations = []#
price_drops = []
deals = []#
model = []

df = pd.DataFrame()

URL = "https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=&list_price_min=&maximum_distance=all&mileage_max=&monthly_payment=&page=1&page_size=20&sort=best_match_desc&stock_type=cpo&year_max=&year_min=&zip="

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US, en;q=0.5",
}

def get_soup(url):
    try:
        response = requests.get(url, HEADERS)
    except:
        print("Unable to fetch!")
        pass
    soup = BeautifulSoup(response.text, 'html.parser')
    
    return soup

def scrape_car_data(url) -> None:
    soup = get_soup(url)
    
    all_cards = soup.find_all("div", class_="vehicle-card")
    
    for d in all_cards:
        car_name = d.find("h2", class_="title").get_text()
        mileage = d.find("div", class_="mileage").get_text()
        price = d.find("span", class_="primary-price").text
        price_change = d.find("span", attrs={"data-qa": "price-drop"})
        deal = d.find("span", class_="sds-badge__label").text.strip()
        review = d.find("span", class_="sds-rating__count")
        review_count = d.find("span", class_="test1")
        location = d.find("div", class_="miles-from").get_text().strip()
        car_model = d.find("p", class_="stock-type").get_text()
        
        car_names.append(car_name)
        prices.append(price)
        if review is not None:
            ratings.append(review.text.strip())
        else:
            ratings.append(0)
        if review_count is not None:
            reviews.append(review_count.text.strip())
        else:
            reviews.append("0")
        locations.append(location)
        used_mi.append(mileage)
        if price_change is not None:
            price_drops.append(price_change.text.strip())
        else:
            price_drops.append("0")
        deals.append(deal)
        model.append(car_model)
    pass

def scrape_next_page(url):
    s = get_soup(url=url)
    pages = s.find("div", class_="sds-pagination__controls")
    next_btn = pages.find("a", attrs={"aria-label": "Next page"})
    if not next_btn:
        return
    else:
        href = next_btn['href']
        new_url = url + href
        
    return scrape_car_data(new_url)

#num_pages = pages you want to webscrape
def scrape_pages(num_page, url) -> None:
    if num_page == 1:
            scrape_car_data(url)
    else:
        for i in range(1, num_page+1):
            scrape_next_page(url)
            print(f"Successfully scraped page: {i}.")
    pass

scrape_pages(200, URL)

df["Name"] = car_names
df["Price"] = prices
df["Rating"] = ratings
df["Reviews"] = reviews
df["Mileage"] = used_mi
df["Location"] = locations
df["Price_change"] = price_drops
df["Deals"] = deals
df["Model"] = model

df.reset_index()
df["Price"] = df["Price"].apply(lambda p: int(str(p).strip("$").replace(",", "")))
df["Reviews"] = df["Reviews"].apply(lambda r: r.split(" ")[0].strip("(").replace(",",""))
df["Mileage"] = df["Mileage"].transform(lambda m: m.split(" ")[0].replace(",",""))
df["Price_change"] = df["Price_change"].apply(lambda p: int(p.split(" ")[0].strip("$").replace(",","")))
df["Deals"] = df["Deals"].apply(lambda x: x.split(" |")[0])
# df = df.drop_duplicates()

df.to_csv("car_deals.csv",encoding="utf-8", header=True, index_label="id")