import os.path
import time
from urllib.parse import urljoin

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver

import json
from multiprocessing.dummy import Pool as ThreadPool
import requests
from bs4 import BeautifulSoup

from AMO_2 import settings
from collect_macmenu.services.selenium_service.utils import clear_string
from .macmenu_parse_config import options_configuration


class SingletonMeta(type):
    """provides singleton behavior"""
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
        return cls.__instances[cls]


class MacMenu(metaclass=SingletonMeta):

    def __init__(self):
        self._main_url = "https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html"

    @staticmethod
    def open_accordion(product_url) -> BeautifulSoup:
        """opens accordion on the product page and returns bs object"""

        for i in range(10):
            try:
                driver = webdriver.Chrome(options=options_configuration())
                driver.get(product_url)
                accordion = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.cmp-accordion__item"))
                )
                accordion_id = accordion.get_attribute("id")
                break
            except Exception as e:
                print(f"Exception while waiting for accordion: {e}\n{product_url}")
                driver.close()
                continue

        driver.get(f"{product_url}#{accordion_id}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.cmp-nutrition-summary__details-column-view-desktop > ul"))
        )
        bs = BeautifulSoup(driver.page_source, "html.parser")
        return bs

    @staticmethod
    def _collect_product_info(product_url: str) -> dict:
        """returns dict with a full product info"""

        for i in range(10):
            try:
                bs = MacMenu.open_accordion(product_url)
                images_base_url = "https://s7d1.scene7.com/is/image/"

                name = bs.select_one("span.cmp-product-details-main__heading-title").text
                description = clear_string(bs.select_one("div.cmp-product-details-main__description").text)

                image_rel_path = bs.select_one("div.s7dm-dynamic-media").get("data-asset-path")
                image_url = urljoin(images_base_url, image_rel_path)

                primary_nutritions = bs.select("li.cmp-nutrition-summary__heading-primary-item")
                calories, fats, carbohydrates, proteins = [clear_string(nutrition.select("span.value > span")[1].text)
                                                           for nutrition in primary_nutritions]

                secondary_nutritions = bs.select_one("div.cmp-nutrition-summary__details-column-view-desktop > ul")
                unsaturated_fats, sugar, salt, portion = [
                    clear_string(nutrition.select_one("span.sr-only").text).split(" ")[0]
                    for nutrition in secondary_nutritions.select("li")[-4:]
                ]
                break
            except Exception as e:
                print(e)
                print(f"product page exception\n{product_url}")
                continue

        return {
            "name": name,
            "image_url": image_url,
            "description": description,
            "calories": calories,
            "fats": fats,
            "carbohydrates": carbohydrates,
            "proteins": proteins,
            "unsaturated_fats": unsaturated_fats,
            "sugar": sugar,
            "salt": salt,
            "portion": portion
        }

    def save_mac_menu_as_json(self) -> bool:
        """parses mcdonalds and dumps products data in .json file
        returns True if succeed"""

        try:
            menu_dict = {"products": []}
            bs = BeautifulSoup(requests.get(self._main_url).text, "html.parser")
            relative_product_urls = (product.get("href") for product in bs.select("a.cmp-category__item-link"))
            product_urls = [f"https://www.mcdonalds.com{url}" for url in relative_product_urls]
            with ThreadPool(32) as pool:
                products = pool.map(self._collect_product_info, product_urls)
            menu_dict["products"] = products
            with open(os.path.join(settings.BASE_DIR, "mac_menu.json"), "w") as f:
                json.dump(menu_dict, f, indent=4)
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == "__main__":
    start = time.time()
    menu = MacMenu()
    menu.save_mac_menu_as_json()
    print(time.time() - start)
