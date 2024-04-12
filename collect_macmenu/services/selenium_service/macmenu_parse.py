import os

from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from AMO_2 import settings
from .macmenu_parse_config import options_configuration
from selenium import webdriver
import json


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
        self._browser = webdriver.Chrome(options=options_configuration())
        self._browser.implicitly_wait(10)
        self._wait = WebDriverWait(self._browser, timeout=15)

    def _collect_product_info(self, product_url: str) -> dict:
        """returns dict with a full product info"""

        # open product page in new tab
        self._browser.execute_script("window.open(arguments[0], '_blank');", product_url)
        self._browser.switch_to.window(self._browser.window_handles[1])

        name = self._browser.find_element(By.CSS_SELECTOR,
                                          "span.cmp-product-details-main__heading-title").get_attribute("textContent")
        description = self._browser.find_element(
            By.CSS_SELECTOR,
            "div.cmp-product-details-main__description").get_attribute("textContent") \
            .replace("\n", "").replace("\t", "")

        try:
            self._wait.until(EC.text_to_be_present_in_element_attribute(
                (By.CSS_SELECTOR, "div.cq-dd-image img"), "src", "https"))
            img_url = self._browser.find_element(By.CSS_SELECTOR, "div.cq-dd-image img").get_attribute("src")
        except TimeoutException:
            img_url = "https://t4.ftcdn.net/jpg/04/70/29/97/360_F_470299797_UD0eoVMMSUbHCcNJCdv2t8B2g1GVqYgs.jpg"
        # open accordion element
        energy_value_accordion = self._browser.find_element(
            By.XPATH,
            "//div[@class='accordion panelcontainer cmp-accordion--default cmp-accordion--nutrition-information']"
            "/div/div[1]/h2/button"
        )
        energy_value_accordion.click()
        self._wait.until(lambda d: energy_value_accordion.get_attribute("aria-expanded") == 'true')

        primary_nutrition_pattern = "//ul[@class='cmp-nutrition-summary__heading-primary']/li[{}]/span[1]/span[2]"
        calories = self._browser.find_element(By.XPATH, primary_nutrition_pattern.format(1)).text
        fats = self._browser.find_element(By.XPATH, primary_nutrition_pattern.format(2)).text
        carbs = self._browser.find_element(By.XPATH, primary_nutrition_pattern.format(3)).text
        proteins = self._browser.find_element(By.XPATH, primary_nutrition_pattern.format(4)).text

        secondary_nutrition_pattern = "//div[@class='cmp-nutrition-summary__details-column-view-desktop']/ul/li[{}]/span[2]/span[1]"

        unsaturated_fats = self._browser.find_element(By.XPATH, secondary_nutrition_pattern.format(1)).text
        sugar = self._browser.find_element(By.XPATH, secondary_nutrition_pattern.format(2)).text
        salt = self._browser.find_element(By.XPATH, secondary_nutrition_pattern.format(3)).text
        portion = self._browser.find_element(By.XPATH, secondary_nutrition_pattern.format(4)).text

        self._browser.close()
        self._browser.switch_to.window(self._browser.window_handles[0])

        product = {
            'name': name, 'description': description, 'img_url': img_url, 'calories': calories, 'fats': fats,
            'carbs': carbs, 'proteins': proteins, 'unsaturated_fats': unsaturated_fats, 'sugar': sugar, 'salt': salt,
            'portion': portion}
        return product

    def save_mac_menu_as_json(self) -> bool:
        """parses mcdonalds and dumps products data in .json file
        returns True if succeed"""
        try:
            menu_dict = {"products": []}
            self._browser.get("https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html")
            products = self._browser.find_elements(By.CSS_SELECTOR, "a.cmp-category__item-link")
            for product in products:
                try:
                    product_dict = self._collect_product_info(product.get_attribute("href"))
                except StaleElementReferenceException:
                    product_dict = self._collect_product_info(product.get_attribute("href"))
                menu_dict["products"].append(product_dict)
                print(product_dict)
            with open(os.path.join(settings.BASE_DIR, 'mac_menu.json'), "w") as menu_f:
                json.dump(menu_dict, menu_f, indent=4)
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self._browser.close()
            self._browser.quit()
