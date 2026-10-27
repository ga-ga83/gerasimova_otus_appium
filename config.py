import os

# Настройки Appium Server
APPIUM_SERVER_URL = "http://127.0.0.1:4723"

# Настройки устройства/эмулятора
DEVICE_NAME = "ARXC9X3909G10025"
PLATFORM_NAME = "Android"
PLATFORM_VERSION = "14"  # Версия Android

# Настройки приложения PNW
APP_PACKAGE = "com.csdroid.pkg"
APP_ACTIVITY = "com.csdroid.pkg/.MainActivity"

# Локаторы (можно вынести сюда же или в отдельный файл locators.py)
CALENDAR_TEXT = "Календарь"
LIST_CONTAINER_ID = "com.example.pnw:id/recycler_view_apps"
CALENDAR_MONTH_TEXT = "Октябрь"