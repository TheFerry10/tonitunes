from pathlib import Path

from adapters.repository import JsonFileMappingRepository


class FilePathMapper:
    def __init__(self, media_mapping_path, audio_dir):
        self.media_mapping_path = media_mapping_path
        self.audio_dir = audio_dir
        self.mapping_repo = JsonFileMappingRepository(file_path=self.media_mapping_path)

    def get_file_path_from_id(self, file_id) -> Path:
        file_name = self.mapping_repo.get_by_id(file_id)
        return Path(self.audio_dir, file_name)
