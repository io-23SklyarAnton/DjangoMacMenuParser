from django.test import TestCase
from collect_macmenu.services.selenium_service.macmenu_parse import MacMenu


class TestSelenium(TestCase):

    def setUp(self):
        self.mac_menu = MacMenu()

    def test_collect_product_info(self):
        self.mac_menu._browser.get("https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html")
        strawberry_ice_dict = self.mac_menu._collect_product_info(
            "https://www.mcdonalds.com/ua/uk-ua/product/200128.html#accordion-29309a7a60-item-9ea8a10642")
        assert strawberry_ice_dict['name'] == "МАКСАНДІ® Полуниця у вафельному стаканчику"

    def test_save_mac_menu_as_json(self):
        self.mac_menu.save_mac_menu_as_json()
