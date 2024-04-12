from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from .macmenu_parse_config import options_configuration
from selenium import webdriver
import json


class SingletonMeta(type):
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

        # open accordion element
        energy_value_accordion = self._browser.find_element(
            By.XPATH,
            "//div[@class='accordion panelcontainer cmp-accordion--default cmp-accordion--nutrition-information']"
            "/div/div[1]/h2/button"
        )
        energy_value_accordion.click()
        self._wait.until(lambda d: energy_value_accordion.get_attribute("aria-expanded") == 'true')

        primary_nutritions = self._browser.find_elements(
            By.XPATH,
            "//li[@class='cmp-nutrition-summary__heading-primary-item']/span[1]/span[2]"
        )
        calories = primary_nutritions[0].text
        fats = primary_nutritions[1].text
        carbs = primary_nutritions[2].text
        proteins = primary_nutritions[3].text

        secondary_nutritions = self._browser.find_elements(
            By.XPATH,
            "//div[@class='cmp-nutrition-summary__details-column-view-desktop']/ul/li/span[2]/span[1]")

        unsaturated_fats = secondary_nutritions[0].text
        sugar = secondary_nutritions[1].text
        salt = secondary_nutritions[2].text
        portion = secondary_nutritions[3].text

        self._browser.close()
        self._browser.switch_to.window(self._browser.window_handles[0])

        product = {
            'name': name, 'description': description, 'calories': calories, 'fats': fats, 'carbs': carbs,
            'proteins': proteins, 'unsaturated fats': unsaturated_fats, 'sugar': sugar, 'salt': salt,
            'portion': portion}
        return product

    def save_mac_menu_as_json(self):
        """parses mcdonalds and dumps products data in .json file"""
        menu_dict = {"products": []}
        self._browser.get("https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html")
        products = self._browser.find_elements(By.CSS_SELECTOR, "a.cmp-category__item-link")
        for product in products:
            product_dict = self._collect_product_info(product.get_attribute("href"))
            menu_dict["products"].append(product_dict)
        with open("..\\..\\..\\mac_menu.json", "w") as menu_f:
            json.dump(menu_dict, menu_f, indent=4)
