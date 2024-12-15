import requests


def test_get_cards():
    cards_json = [
        {"name": "Justin Graham", "uid": 11824057},
        {"name": "Kimberly Matthews", "uid": 16344897},
        {"name": "Joseph Johnston", "uid": 32976344},
        {"name": "Kimberly Schroeder", "uid": 62109375},
        {"name": "Dustin Johnson", "uid": 65458256},
        {"name": "Gabrielle Brown", "uid": 66678529},
        {"name": "Vanessa Williamson", "uid": 73359400},
        {"name": "Linda Schneider", "uid": 80954621},
        {"name": "Donald Hernandez", "uid": 87334242},
        {"name": "Jose Smith", "uid": 93863668},
    ]
    base_url = "http://127.0.0.1:5000"
    url = base_url + "/api/card"
    response = requests.get(url)

    assert response.status_code == 200
    assert response.json() == cards_json
