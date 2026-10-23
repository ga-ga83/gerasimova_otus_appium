import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from allure import step

CALENDAR_TEXT = "Календарь"
MAX_SWIPES = 15


class TestCalendarSearch:
    @step("Выполнить свайп вниз по экрану")
    def _swipe_down(self, driver):
        window = driver.get_window_size()
        start_x = window["width"] * 0.5
        start_y = window["height"] * 0.75
        end_x = start_x
        end_y = window["height"] * 0.25

        driver.swipe(start_x, start_y, end_x, end_y, duration=300)
        time.sleep(1.5)  # Даём время подгрузить новые элементы

    @step("Найти элемент 'Календарь' в списке всех TextView")
    def _find_calendar_by_text(self, driver, text):
        # Получаем ВСЕ текстовые элементы на экране
        elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")

        for elem in elements:
            try:
                elem_text = elem.text.strip()
                # Проверяем, содержит ли текст нужное слово
                if text in elem_text:
                    return elem
            except Exception:
                continue
        return None

    def test_find_and_click_calendar(self, driver, wait):
        found = False
        swipe_count = 0

        with step(f"Начать поиск элемента '{CALENDAR_TEXT}' (макс. {MAX_SWIPES} свайпов)"):
            while swipe_count < MAX_SWIPES:
                # Пытаемся найти элемент через надёжный метод
                calendar_elem = self._find_calendar_by_text(driver, CALENDAR_TEXT)

                if calendar_elem and calendar_elem.is_displayed():
                    with step("Элемент найден — выполняем клик"):
                        calendar_elem.click()
                        time.sleep(2)
                        found = True
                        break

                # Если не нашли — делаем свайп и пробуем снова
                with step(f"Свайп вниз №{swipe_count + 1} (осталось: {MAX_SWIPES - swipe_count - 1})"):
                    self._swipe_down(driver)
                swipe_count += 1

        if not found:
            raise AssertionError(
                f"Элемент с текстом '{CALENDAR_TEXT}' не найден после {MAX_SWIPES} свайпов. "
                "Проверь, не изменился ли интерфейс приложения."
            )

        assert True, "Успех: Календарь открыт"

