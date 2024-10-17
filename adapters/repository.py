from abc import ABC, abstractmethod
import json
import os
from typing import Optional


class AbstractUIDMappingRepository(ABC):
    @abstractmethod
    def get_all(self):
        """Retrieve all UID mappings"""
        pass

    @abstractmethod
    def get_by_uid(self, uid: str):
        """Retrieve the mapping by UID"""
        pass

    @abstractmethod
    def add(self, uid: str, name: Optional[str], path: str):
        """Add a new mapping."""
        pass

    @abstractmethod
    def update(self, uid: str, name: Optional[str], path: str):
        """Update an existing file mapping"""
        pass

    @abstractmethod
    def remove(self, uid: str):
        """Remove a mapping by UID."""
        pass

    @abstractmethod
    def save(self):
        """Persist the current state to the storage"""
        pass


class JsonUIDMappingRepository(AbstractUIDMappingRepository):
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

    def add(self, uid: str, name: Optional[str], path: str):
        self._mapping[uid] = {"name": name, "path": path}

    def update(self, uid: str, name: Optional[str], path: str):
        self._mapping[uid] = {"name": name, "path": path}

    def remove(self, uid: str):
        if uid in self._mapping:
            del self._mapping[uid]

    def save(self):
        """Persist the current state to the storage (e.g., JSON file)."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self._mapping, f, ensure_ascii=False, indent=4)
