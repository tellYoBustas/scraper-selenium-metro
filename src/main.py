import os
import json
from time import sleep
from threading import Thread
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ['enable-automation'])
timeout = 5


def threading(function):
    threads = []
    threads_count = 8

    for _ in range(threads_count):
        thread = Thread(target=function, args=(_, threads_count))
        thread.start()

        threads.append(thread)

    for thread in threads:
        thread.join()


def categories():
    print("write the 𝗰𝗮𝘁𝗲𝗴𝗼𝗿𝗶𝗲𝘀.𝗷𝘀𝗼𝗻 file ☕")
    _categories = []

    start_urls = [
        "https://online.metro-cc.ru/category/rybnye",
        "https://online.metro-cc.ru/category/myasnye",
        "https://online.metro-cc.ru/category/bakaleya",
        "https://online.metro-cc.ru/category/chaj-kofe-kakao",
        "https://online.metro-cc.ru/category/zdorovoe-pitanie",
        "https://online.metro-cc.ru/category/ovoshchi-i-frukty",
        "https://online.metro-cc.ru/category/bezalkogolnye-napitki",
        "https://online.metro-cc.ru/category/alkogolnaya-produkciya",
        "https://online.metro-cc.ru/category/gotovye-bljuda-polufabrikaty",
        "https://online.metro-cc.ru/category/molochnye-prodkuty-syry-i-yayca",
        "https://online.metro-cc.ru/category/hleb-vypechka-konditerskie-izdeliya"
    ]
    count = len(start_urls)

    def scrap(start_position, step):
        browser = webdriver.Chrome(options=options)

        for i in range(start_position, count, step):
            browser.get(start_urls[i])

            city_choice(browser)

            WebDriverWait(browser, timeout) \
                .until(expected_conditions
                       .visibility_of_element_located((By.CSS_SELECTOR, "a.level-first")))

            first_level_categories = browser.find_elements(By.CSS_SELECTOR, "a.level-first")

            for prop in first_level_categories:
                category_name = prop.text
                category_href = prop.get_attribute("href")

                if category_name == "Посуда и аксессуары для напитков":
                    continue

                _categories.append(category_href)

    threading(scrap)

    with open("../data/categories.json", "w", encoding="utf-8") as file:
        json.dump(_categories, file, indent=4, ensure_ascii=False)

    print("the 𝗰𝗮𝘁𝗲𝗴𝗼𝗿𝗶𝗲𝘀.𝗷𝘀𝗼𝗻 file is successfully written ✅")


def products():
    print("write the 𝗽𝗿𝗼𝗱𝘂𝗰𝘁𝘀.𝗷𝘀𝗼𝗻 file ☕")

    _products = []

    with open("../data/categories.json", encoding="utf-8") as file:
        _categories = json.load(file)
    count = len(_categories)

    def scrap(start_position, step):
        browser = webdriver.Chrome(options=options)

        for i in range(start_position, count, step):
            current_page_href = _categories[i]
            browser.get(current_page_href)

            city_choice(browser)

            elements_count = browser.find_element(By.CSS_SELECTOR, "span.heading-products-count")
            elements_count = int(elements_count.text.split(" ")[0])
            pages_count = int(-1 * (elements_count / 30) // 1 * -1)

            for j in range(1, pages_count + 1):
                browser.get(current_page_href + "?page=" + str(j))

                products_per_page = browser.find_elements(By.CSS_SELECTOR, "main .product-card div div div a")

                for prop in products_per_page:
                    _products.append(prop.get_attribute("href"))

    threading(scrap)

    with open("data/products.json", "w", encoding="utf-8") as file:
        json.dump(_products, file, indent=4, ensure_ascii=False)

    print("the 𝗽𝗿𝗼𝗱𝘂𝗰𝘁𝘀.𝗷𝘀𝗼𝗻 file is successfully written ✅")


def data():
    print("Collecting data ☕")
    _data = []

    with open("../data/products.json", encoding="utf-8") as file:
        _products = json.load(file)
    count = len(_products)

    def scrap(start_position, step):

        for i in range(start_position + 10000, count, step):
            data_struct = {
                "Title": "no_title",
                "Type": "no_type",
                "Brand": "no_brand",
                "Kilocalories": "0",
                "Proteins": "0",
                "Fats": "0",
                "Carbohydrates": "0"
            }

            browser = webdriver.Chrome(options=options)
            browser.get(_products[i])

            try:
                city_choice(browser)
                confirm_age(browser)

                WebDriverWait(browser, timeout) \
                    .until(expected_conditions
                           .visibility_of_element_located((By.CSS_SELECTOR, ".product__specification button")))

                button = browser.find_element(By.CSS_SELECTOR, ".product__specification button")

                ActionChains(browser) \
                    .click(button) \
                    .perform()

                left = browser.find_elements(By.CSS_SELECTOR, ".product__specification .left-col span")
                right = browser.find_elements(By.CSS_SELECTOR, ".product__specification .text")

                title = browser.find_element(By.CSS_SELECTOR, "h1.product__title")
                data_struct["Title"] = title.text
            except:
                browser.close()
                continue

            for j in range(len(left)):
                data_dt = left[j].text
                data_dd = right[j].text

                if data_dt == "Тип":
                    data_struct["Type"] = data_dd
                    continue
                if data_dt == "Бренд":
                    data_struct["Brand"] = data_dd
                    continue
                if data_dt == "Энергетическая ценность, ккал/100 г":
                    data_struct["Kilocalories"] = data_dd
                    continue
                if data_dt == "Белки, г":
                    data_struct["Proteins"] = data_dd
                    continue
                if data_dt == "Жиры, г":
                    data_struct["Fats"] = data_dd
                    continue
                if data_dt == "Углеводы, г":
                    data_struct["Carbohydrates"] = data_dd
                    continue

            _data.append(data_struct)
            browser.close()

    threading(scrap)

    with open("../data/data.json", "w", encoding="utf-8") as file:
        json.dump(_data, file, indent=4, ensure_ascii=False)

    print("Data's collected ✅")


def city_choice(driver):
    for i in range(1):
        try:
            WebDriverWait(driver, timeout) \
                .until(expected_conditions
                       .visibility_of_element_located((By.CSS_SELECTOR, ".region-confirm__actions button")))

            button = driver.find_elements(By.CSS_SELECTOR, ".region-confirm__actions button")[1]

            ActionChains(driver) \
                .click(button) \
                .perform()

            sleep(1)

            WebDriverWait(driver, timeout) \
                .until(expected_conditions
                       .visibility_of_element_located((By.CSS_SELECTOR, "span.cities__item--main")))

            moscow = driver.find_elements(By.CSS_SELECTOR, "span.cities__item--main")[0]

            ActionChains(driver) \
                .click(moscow) \
                .perform()

            sleep(2)
        except:
            continue


def confirm_age(driver):
    for i in range(1):
        try:
            WebDriverWait(driver, timeout) \
                .until(expected_conditions
                       .visibility_of_element_located((By.CSS_SELECTOR, ".confirm-age button")))

            button = driver.find_elements(By.CSS_SELECTOR, ".confirm-age button")[1]

            ActionChains(driver) \
                .click(button) \
                .perform()

            sleep(2)
        except:
            continue


if __name__ == '__main__':
    if not os.path.isfile("../data/categories.json"):
        categories()
    if not os.path.isfile("../data/products.json"):
        products()
    if not os.path.isfile("../data/data.json"):
        data()
