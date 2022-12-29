import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os

load_dotenv(".env")

ZILLOW_LINK = "https://www.zillow.com/san-francisco-ca/rentals/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C" \
             "%22mapBounds%22%3A%7B%22north%22%3A37.84608530611633%2C%22east%22%3A-122.32758609179687%2C%22south%22" \
             "%3A37.70443074814723%2C%22west%22%3A-122.53907290820312%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22" \
             "%3Atrue" \
             "%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D" \
             "%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22auc%22%3A%7B%22value" \
             "%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%" \
             "22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%" \
             "22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22regionSelection%22%3A%5B%7B%22region" \
             "Id%22%3A20330%2C%22regionType%22%3A6%7D%5D%7D"

GOOGLE_FORM_URL = os.getenv("FORM_URL")

HEADER = {
    "Accept-Language": "en-ZA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 11  0.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}


# Get html data from Zillow
def get_html_page():
    # Make a request and return data
    response = requests.get(url=ZILLOW_LINK, headers=HEADER)
    contents = response.text

    beautiful_soup = BeautifulSoup(contents, "html.parser")

    return beautiful_soup


# Populate answers into google form
def fill_in_form(address_input, price_input, link_input):
    chrome_driver_path = r"C:\Users\Mary\chromedriver_win32\chromedriver.exe"

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    driver.get(GOOGLE_FORM_URL)
    time.sleep(10)

    # Find all input fields and the submit button, enter the answers and submit them.
    address_answer = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/'
                                                   'div/div[1]/div/div[1]/input')
    price_answer = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]'
                                                 '/div/div[1]/input')
    link_answer = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/'
                                                'div[1]/div/div[1]/input')
    submit_button = driver.find_element(By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span')

    address_answer.send_keys(address_input)
    price_answer.send_keys(price_input)
    link_answer.send_keys(link_input)
    submit_button.click()

    # submit_another_form = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/a')
    # submit_another_form.click()

    time.sleep(15)


soup = get_html_page()
# property_listings = soup.select(selector="ul .with_constellation")
# Find the relevant tags containing the property listing info
address_tags = soup.select(selector="a address")
price_tags = soup.select(selector="div .hRqIYX span")
link_tags = soup.select(selector="div .property-card-data a")

# print(len(address_tags))
# print(len(price_tags))
# print(len(link_tags))

# Create property info lists using info from the tags
links_list = [link.get("href") for link in link_tags]
prices_list = [price.getText() for price in price_tags]
addresses_list = [addr.getText() for addr in address_tags]

formatted_addresses = []
formatted_prices = []
formatted_links = []

for n in range(0, len(addresses_list)):
    address = addresses_list[n]
    property_price = prices_list[n]
    link = links_list[n]

    if "|" in address:
        address = addresses_list[n].split("|")[1].strip()

    if "+" in property_price:
        property_price = property_price.split("+")[0]
    else:
        property_price = property_price.replace("/mo", "")

    if "https" not in link:
        link = f"https://www.zillow.com{link}"

    formatted_links.append(link)
    formatted_addresses.append(address)
    formatted_prices.append(property_price)

print(formatted_links)
print(formatted_addresses)
print(formatted_prices)

# Enter and submit all the responses from each list
for i in range(0, len(links_list)):
    fill_in_form(link_input=formatted_links[i], price_input=formatted_prices[i], address_input=formatted_addresses[i])
