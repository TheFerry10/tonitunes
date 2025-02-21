import json
import os
from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy.orm import Session

from app.cardmanager.models import Card


class AbstractCardRepository(ABC):
    @abstractmethod
    def get_all(self):
        """Retrieve all UID mappings"""

    @abstractmethod
    def get_by_uid(self, uid: str):
        """Retrieve the mapping by UID"""

    @abstractmethod
    def add(self, uid: str, name: Optional[str]):
        """Add a new mapping."""

    @abstractmethod
    def update(self, uid: str, name: Optional[str]):
        """Update an existing file mapping"""

    @abstractmethod
    def remove(self, uid: str):
        """Remove a mapping by UID."""

    @abstractmethod
    def save(self):
        """Persist the current state to the storage"""


class SqlAlchemyCardRepositoriy(AbstractCardRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Card]:
        return self.session.query(Card).all()

    def get_by_uid(self, uid) -> Card:
        return self.session.query(Card).filter_by(uid=uid).first()

    def add(self, uid, name):
        card = Card(uid=uid, name=name)
        self.session.add(card)

    def update(self, uid, name):
        card = self.session.query(Card).filter_by(uid=uid).first()
        if card:
            card.name = name
        else:
            raise ValueError(f"Card with uid {uid} not found")

    def remove(self, uid):
        record_to_delete = self.session.query(Card).filter_by(uid=uid).first()
        if record_to_delete:
            self.session.delete(record_to_delete)

    def save(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()


class JsonCardRepository(AbstractCardRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._mapping = self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_all(self):
        return self._mapping

    def get_by_uid(self, uid: str):
        return self._mapping.get(uid)

    def add(self, uid: str, name: Optional[str]):
        self._mapping[uid] = {"name": name}

    def update(self, uid: str, name: Optional[str]):
        self._mapping[uid] = {"name": name}

    def remove(self, uid: str):
        if uid in self._mapping:
            del self._mapping[uid]

    def save(self):
        """Persist the current state to the storage (e.g., JSON file)."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self._mapping, f, ensure_ascii=False, indent=4)
