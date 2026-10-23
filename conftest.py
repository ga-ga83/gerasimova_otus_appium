import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config import APPIUM_SERVER_URL, DEVICE_NAME, PLATFORM_NAME, APP_PACKAGE, APP_ACTIVITY
from selenium.webdriver.support.wait import WebDriverWait

@pytest.fixture(scope="function")
def driver():
    options = UiAutomator2Options()
    options.platform_name = PLATFORM_NAME
    options.device_name = DEVICE_NAME
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.no_reset = True
    options.new_command_timeout = 300

    wd = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    wd._test_name = "default"

    yield wd

    try:
        wd.quit()
    except Exception:
        pass


@pytest.fixture(scope="function")
def wait(driver):
    # 15 секунд — хороший баланс между стабильностью и скоростью при 8 ГБ RAM
    return WebDriverWait(driver, 15)
