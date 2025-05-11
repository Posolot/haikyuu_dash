from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
import time
import pandas as pd

options = Options()
options.add_argument("--headless")
driver_path = "chromedriver-win64/chromedriver.exe"

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

base_url = "https://haikyuu.fandom.com"
category_url = f"{base_url}/ru/wiki/Категория:Персонажи"
driver.get(category_url)
time.sleep(2)

character_links = []
while True:
    links = driver.find_elements(By.CSS_SELECTOR, "div.category-page__members a.category-page__member-link")
    for link in links:
        character_links.append(link.get_attribute("href"))

    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "a.category-page__pagination-next")
        next_btn.click()
        time.sleep(2)
    except NoSuchElementException:
        break

print(f"Найдено персонажей: {len(character_links)}")

characters = []
for link in tqdm(character_links):
    driver.get(link)
    time.sleep(1)

    try:
        name = driver.find_element(By.CSS_SELECTOR, "h1.page-header__title").text.strip()
    except:
        continue

    character = {"Имя": name, "Ссылка": link}

    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "aside.portable-infobox > section > div.pi-item")
        for row in rows:
            try:
                label = row.find_element(By.CLASS_NAME, "pi-data-label").text.strip()
                value = row.find_element(By.CLASS_NAME, "pi-data-value").text.strip()
                character[label] = value
            except:
                continue
    except:
        pass

    characters.append(character)

driver.quit()

df = pd.DataFrame(characters)
df.to_csv("haikyuu_characters.csv", index=False)
print("Данные сохранены в haikyuu_characters.csv")
