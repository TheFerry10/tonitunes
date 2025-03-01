# Tonibox RFID Project

## Project Description

The Tonibox RFID Project is a Python-based application that integrates RFID technology with audio playback. The project uses the VLC media player to manage and play audio files based on RFID card interactions. It includes modules for handling RFID data, managing audio playback, and interacting with a database to store and retrieve card information.

## Features

- Read and handle RFID data
- Manage audio playback using VLC
- Store and retrieve card information from a database
- Handle playlists and songs associated with RFID cards

## Installation

### Prerequisites

- Python 3.8 or higher
- VLC media player
- SQLite (or another supported database)

### Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/tonibox-rfid.git
    ```
2. Navigate to the project directory:
    ```bash
    cd tonibox-rfid
    ```
3. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
4. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
5. Set up the environment variables:
    Create a `.env` file in the project root directory and add the following variables:
    ```env
    AUDIO_DIR=/path/to/your/audio/files
    DATABASE_URI=sqlite:///path/to/your/database.db
    VALID_FILE_PATH_SONG_1=/path/to/your/audio/files/song1.mp3
    VALID_FILE_PATH_SONG_2=/path/to/your/audio/files/song2.mp3
    VALID_FILE_PATH_SONG_3=/path/to/your/audio/files/song3.mp3
    INVALID_FILE_PATH_SONG=/path/to/your/audio/files/invalid_song.mp3
    ```

## Usage

### Running the Application

1. Run the main script to start the application:
    ```bash
    python main.py
    ```

### Running Tests

1. To run the tests, use `pytest`:
    ```bash
    pytest
    ```

## Project Structure
tonibox-rfid/
├── src/
│   ├── adapters/
│   │   ├── rfid_interface.py
│   │   └── ...
│   ├── app/
│   │   ├── cardmanager/
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   └── ...
│   ├── player/
│   │   ├── player.py
│   │   └── ...
│   └── ...
├── tests/
│   ├── test_player.py
│   ├── test_e2e_player.py
│   └── ...
├── .env
├── requirements.txt
├── README.md
└── main.py

## Contributing

We welcome contributions! Please read our contributing guidelines for more details.

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

## Contact

For any questions or suggestions, please contact us at [email@example.com](mailto:email@example.com).

## Acknowledgements

- [Freesound.org](https://freesound.org/) for providing free sound samples
- [SQLAlchemy](https://www.sqlalchemy.org/) for the ORM
- [VLC](https://www.videolan.org/vlc/) for the media player
