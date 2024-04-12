from fake_useragent import UserAgent
from selenium import webdriver


def _add_user_agent(options):
    ua = UserAgent().getChrome
    options.add_argument(f"user-agent={ua}")
    return options


def options_configuration() -> webdriver.IeOptions:
    options = webdriver.ChromeOptions()

    _add_user_agent(options)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")

    return options
