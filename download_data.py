from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from tqdm import tqdm
import re
import time
import pandas as pd

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
service = Service("chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

driver.set_page_load_timeout(300)
driver.set_script_timeout(300)

base_url = "https://haikyuu.fandom.com"
category_url = f"{base_url}/ru/wiki/Категория:Персонажи"

try:
    driver.get(category_url)
except TimeoutException:
    print("Timeout при загрузке страницы категории.")
    driver.quit()
    exit()

time.sleep(2)

links = set()
while True:
    for el in driver.find_elements(By.CSS_SELECTOR, "div.category-page__members a.category-page__member-link"):
        links.add(el.get_attribute("href"))
    try:
        driver.find_element(By.CSS_SELECTOR, "a.category-page__pagination-next").click()
        time.sleep(1.5)
    except NoSuchElementException:
        break
    except TimeoutException:
        print("Timeout при переходе к следующей странице категории.")
        break

print(f"Всего найдено персонажей: {len(links)}")


info_fields = ["Пол", "Рост", "Вес", "Позиция"]
abilities = ["Сила", "Прыжки", "Выносливость", "Стратегия", "Техника", "Скорость"]

results = []

for url in tqdm(links, desc="Парсинг персонажей"):
    try:
        driver.get(url)
        time.sleep(1)
    except TimeoutException:
        print(f"Timeout при загрузке {url}")
        continue

    try:
        name = driver.find_element(By.CSS_SELECTOR, "h1.page-header__title").text.strip()
    except NoSuchElementException:
        continue

    char = {"Имя": name, "Ссылка": url}
    for f in info_fields:
        char[f] = None
    for a in abilities:
        char[a] = None

    try:
        ib = driver.find_element(By.CSS_SELECTOR, "aside.portable-infobox")
        for item in ib.find_elements(By.CSS_SELECTOR, "div.pi-item"):
            try:
                lbl = item.find_element(By.CSS_SELECTOR, ".pi-data-label").text.strip()
                val = item.find_element(By.CSS_SELECTOR, ".pi-data-value").text.strip()
                if lbl in info_fields:
                    char[lbl] = val
            except NoSuchElementException:
                continue
    except NoSuchElementException:
        pass

    for row in driver.find_elements(By.XPATH, "//table//tr"):
        ths = row.find_elements(By.TAG_NAME, "th")
        if not ths:
            continue
        key = ths[0].text.strip()
        if key not in abilities:
            continue
        for td in row.find_elements(By.TAG_NAME, "td"):
            text = td.text.strip()
            if re.match(r"^\s*\d+\s*/\s*\d+\s*$", text):
                char[key] = text[0]
                break

    results.append(char)

driver.quit()

df = pd.DataFrame(results)
cols = ["Имя"] + info_fields + abilities + ["Ссылка"]
df = df.reindex(columns=cols)
df.to_csv("haikyuu_characters.csv", index=False, encoding="utf-8-sig")

print("Парсинг завершён. Данные сохранены в haikyuu_characters.csv")
