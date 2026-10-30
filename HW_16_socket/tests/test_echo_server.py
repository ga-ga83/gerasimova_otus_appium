import pytest
import re
import requests


@pytest.fixture(scope="session")
def host():
    return "127.0.0.1"


@pytest.fixture(scope="session")
def port():
    return 5000


def test_response_format(host, port):
    r = requests.get(f'http://{host}:{port}')
    assert r.status_code == 200, f"Ожидался 200, получил {r.status_code}"
    text = r.text
    assert text, "Тело ответа пустое! Сервер не вернул данные."
    assert "Request Method: GET" in text
    # Регулярка ищет формат кортежа Python: ('IP', port)
    assert re.search(r"Request Source: \('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', \d+\)", text) is not None
    assert "Response Status: 200 OK" in text


def test_default_headers(host, port):
    """Проверяем, что заголовки клиента попали в ТЕЛО ответа."""
    r = requests.get(f'http://{host}:{port}')
    text = r.text
    assert text, "Тело ответа пустое!"

    for key, value in r.request.headers.items():
        # Ищем строку "Key: Value" в теле ответа.
        # Иногда requests нормализует ключи, поэтому проверяем оба варианта.
        assert f"{key}: {value}" in text or f"{key.lower()}: {value}" in text


def test_custom_header(host, port):
    key, val = 'MyHeader', 'Agr'
    r = requests.get(f'http://{host}:{port}', headers={key: val})
    text = r.text
    assert text, "Тело ответа пустое!"
    assert f"{key}: {val}" in text


@pytest.mark.parametrize('code, expected_code', [
    (200, 200),
    (201, 201),
    (404, 404),
    (503, 503),
    ('a', 200),
    ('', 200),
])
def test_status_code(host, port, code, expected_code):
    r = requests.get(f'http://{host}:{port}/?status={code}')
    assert r.status_code == expected_code, f"Ожидался {expected_code}, получил {r.status_code}"


def test_status_second_parameter(host, port):
    r = requests.get(f'http://{host}:{port}/?a=1&status=500')
    assert r.status_code == 500


def test_post_method(host, port):
    r = requests.post(f'http://{host}:{port}')
    text = r.text
    assert text, "Тело ответа пустое!"
    assert 'Request Method: POST' in text


def test_server_alive(host, port):
    for _ in range(2):
        r = requests.get(f'http://{host}:{port}')
        assert r.status_code == 200
