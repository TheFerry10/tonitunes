from pathlib import Path


class FilePathMapper:
    def __init__(self, uid_mapping, audio_dir):
        self.uid_mapping = uid_mapping
        self.audio_dir = audio_dir

    def get_file_path_from_id(self, file_id) -> Path:
        file_name = self.uid_mapping.get_by_id(file_id)
        return Path(self.audio_dir, file_name)
