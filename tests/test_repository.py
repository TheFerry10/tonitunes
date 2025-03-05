import csv

import pytest

from adapters.repository import CsvCardRepository, UIDAlreadyExistsError


@pytest.fixture(name="csv_file")
def csv_file_fixture(tmp_path):
    file_path = tmp_path / "test_cards.csv"
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["uid", "name"])
        writer.writeheader()
        writer.writerow({"uid": "123", "name": "Card 1"})
        writer.writerow({"uid": "456", "name": "Card 2"})
    return file_path


@pytest.fixture(name="repository")
def repository_fixture(csv_file):
    return CsvCardRepository(csv_file)


def test_get_all(repository):
    all_cards = repository.get_all()
    assert len(all_cards) == 2
    assert all_cards["123"]["name"] == "Card 1"
    assert all_cards["456"]["name"] == "Card 2"


def test_get_by_uid(repository):
    card = repository.get_by_uid("123")
    assert card["name"] == "Card 1"


def test_add(repository):
    repository.add("789", "Card 3")
    assert repository.get_by_uid("789")["name"] == "Card 3"


def test_update(repository):
    repository.update("123", "Updated Card 1")
    assert repository.get_by_uid("123")["name"] == "Updated Card 1"


def test_remove(repository):
    repository.remove("123")
    assert repository.get_by_uid("123") is None


def test_save(repository, csv_file):
    repository.add("789", "Card 3")
    repository.save()
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 3
        assert any(row["uid"] == "789" and row["name"] == "Card 3" for row in rows)


def test_add_existing_uid(repository):
    with pytest.raises(UIDAlreadyExistsError):
        repository.add("123", "Duplicate Card")
