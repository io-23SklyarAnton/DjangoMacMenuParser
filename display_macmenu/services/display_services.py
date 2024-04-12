import json
import os
from typing import Union, List

from AMO_2 import settings


def get_products() -> Union[List[dict], None]:
    try:
        with open(os.path.join(settings.BASE_DIR, 'mac_menu.json'), "r") as menu_f:
            return json.load(menu_f)["products"]
    except FileExistsError:
        pass


def get_product(product_name: str) -> Union[dict, None]:
    try:
        with open(os.path.join(settings.BASE_DIR, 'mac_menu.json'), "r") as menu_f:
            data = json.load(menu_f)["products"]
            for product in data:
                if product["name"] == product_name:
                    return product
    except FileExistsError:
        pass
    except KeyError:
        pass


def get_field(product_name: str, field: str) -> Union[str, None]:
    try:
        product = get_product(product_name)
        return product[field]
    except FileExistsError:
        pass
    except KeyError:
        pass
