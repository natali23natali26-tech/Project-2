import pytest
import requests
from unittest.mock import patch, MagicMock
from src.api import HeadHunterAPI


@pytest.fixture
def hh_api():
    """Фикстура для создания экземпляра HeadHunterAPI."""
    return HeadHunterAPI(per_page=10)


def test_valid_per_page():
    """Проверка валидной инициализации с per_page в диапазоне."""
    api = HeadHunterAPI(per_page=50)
    assert api.per_page == 50


def test_invalid_per_page_type():
    """Проверка обработки TypeError при некорректном типе per_page."""
    with pytest.raises(TypeError):
        HeadHunterAPI(per_page="10")


def test_invalid_per_page_range():
    """Проверка обработки ValueError при per_page вне диапазона 0–100."""
    with pytest.raises(ValueError):
        HeadHunterAPI(per_page=150)


@patch("requests.get")
def test_connect_success(mock_get, hh_api):
    """Тестирование успешного ответа от API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={"items": [], "pages": 1})
    mock_get.return_value = mock_response

    result = hh_api.connect()

    assert result == {"items": [], "pages": 1}
    mock_get.assert_called_once()


@patch("requests.get")
def test_connect_http_error(mock_get, hh_api):
    """Тестирование обработки HTTP-ошибки (4xx/5xx)."""
    mock_get.side_effect = requests.exceptions.HTTPError("404")

    result = hh_api.connect()

    assert result is None


@patch("requests.get")
def test_connect_request_exception(mock_get, hh_api):
    """Тестирование обработки исключения RequestException."""
    mock_get.side_effect = requests.exceptions.RequestException("Timeout")

    result = hh_api.connect()

    assert result is None


@patch.object(HeadHunterAPI, "connect")
def test_get_vacancies_no_data(mock_connect, hh_api):
    """Тестирование случая, когда API не возвращает данные."""
    mock_connect.return_value = None

    result = hh_api.get_vacancies("python")

    assert result == []
    assert len(hh_api._HeadHunterAPI__vacancies) == 0


@patch.object(HeadHunterAPI, "connect")
def test_get_vacancies_with_pages(mock_connect, hh_api):
    """Тестирование получения данных с нескольких страниц API."""
    mock_connect.side_effect = [
        {"items": [{"id": 1}], "pages": 2},
        {"items": [{"id": 2}], "pages": 2},
    ]

    result = hh_api.get_vacancies("python")

    assert len(result) == 2
    assert [v["id"] for v in result] == [1, 2]
