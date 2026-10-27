import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from allure import step
from config import CALENDAR_TEXT, CALENDAR_MONTH_TEXT

MAX_SWIPES = 15
SWIPE_DURATION_MS = 300
POST_SWIPE_WAIT_SEC = 1.0


class TestCalendarSearch:
    @step("Выполнить свайп вниз по экрану")
    def _swipe_down(self, driver):
        window = driver.get_window_size()
        start_x = window["width"] * 0.5
        start_y = window["height"] * 0.75
        end_x = start_x
        end_y = window["height"] * 0.25

        driver.swipe(start_x, start_y, end_x, end_y, duration=SWIPE_DURATION_MS)
        time.sleep(POST_SWIPE_WAIT_SEC)

    @step("Найти элемент 'Календарь' в списке TextView")
    def _find_calendar_by_text(self, driver, text):
        elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        for elem in elements:
            try:
                elem_text = elem.text.strip()
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
                calendar_elem = self._find_calendar_by_text(driver, CALENDAR_TEXT)

                if calendar_elem and calendar_elem.is_displayed():
                    with step("Элемент найден — выполняем клик"):
                        calendar_elem.click()
                    found = True
                    break

                with step(f"Свайп вниз №{swipe_count + 1} (осталось: {MAX_SWIPES - swipe_count - 1})"):
                    self._swipe_down(driver)
                swipe_count += 1

        if not found:
            raise AssertionError(
                f"Элемент с текстом '{CALENDAR_TEXT}' не найден после {MAX_SWIPES} свайпов. "
                "Проверь, не изменился ли интерфейс приложения."
            )

        # --- ПРОВЕРКА РЕЗУЛЬТАТА: ищем текст месяца на экране ---
        with step("Проверить, что экран календаря открылся (ожидание появления текста месяца)"):
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (AppiumBy.XPATH, f"//android.widget.TextView[@text='{CALENDAR_MONTH_TEXT}']")
                    )
                )
            except Exception as e:
                raise AssertionError(
                    f"Не удалось подтвердить открытие экрана календаря: не найден текст месяца '{CALENDAR_MONTH_TEXT}'. "
                    "Возможно, месяц изменился или текст отображается иначе."
                ) from e
        assert True, "Экран календаря подтверждён появлением текста месяца"
