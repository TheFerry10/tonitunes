# Tonitunes

## Project Description
Tonitunes is a Python-based application for Raspberry Pi that integrates RFID technology with audio playback. It uses VLC media player to manage and play audio files based on RFID card interactions. The project includes modules for handling RFID data, managing audio playback, and interacting with a database via a Flask application to store and retrieve card information. Playlists can be managed and mapped to cards using a simple Flask application called CardManager.


## Table of Contents

- [Tonitunes](#tonitunes)
  - [Project Description](#project-description)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
    - [1. RFID Configuration](#1-rfid-configuration)
    - [2. Set Up .env File](#2-set-up-env-file)
    - [3. Configure `settings.ini`](#3-configure-settingsini)
    - [4. Run Initialization Script](#4-run-initialization-script)
    - [5. Copy MP3 Files to Device](#5-copy-mp3-files-to-device)
    - [6. Extract Song Metadata from MP3 Files](#6-extract-song-metadata-from-mp3-files)
    - [7. Install Requirements and Package](#7-install-requirements-and-package)
    - [8. Run Tonitunes Service on Startup](#8-run-tonitunes-service-on-startup)
    - [Run Shutdown Service (Optional)](#run-shutdown-service-optional)
  - [CardManager](#cardmanager)
  - [Contributing](#contributing)
  - [License](#license)
  - [Acknowledgements](#acknowledgements)


## Features

- Read and handle RFID data
- Manage audio playback using VLC
- Store and retrieve card information from a database
- Handle playlists and songs associated with RFID cards

## Installation

### Prerequisites

- Python 3.8 or higher
- Raspbian OS (bookworm or bullseye)
- MFRC522 (RFID Reader module)

### Steps

Clone the repository:
```bash
git clone https://github.com/yourusername/tonibox-rfid.git
```

### 1. RFID Configuration

1. Enable SPI:
  ```bash
  sudo raspi-config
  ```
  - Navigate to `Interfacing Options` -> `SPI` and enable it.
2. Reboot the device:
  ```bash
  sudo reboot
  ```
3. Verify SPI is enabled:
  ```bash
  lsmod | grep spi
  ```
  - Expected response (example):
    ```
    spidev                 16384  2
    spi_bcm2835            16384  0
    ```

### 2. Set Up .env File

Create a `.env` file from `.env-default`.

### 3. Configure `settings.ini`

Configure your `settings.ini` file with the necessary settings, such as the GPIO pins related to your configuration.

### 4. Run Initialization Script

Run the provided initialization script to set up the environment:
  ```bash
  ./initialize.bash
  ```

### 5. Copy MP3 Files to Device

Transfer your MP3 files to the device using `scp` or any other file transfer method:
  ```bash
  scp /path/to/your/mp3/files/* user@device_ip:/path/to/device/mp3_directory/
  ```

### 6. Extract Song Metadata from MP3 Files

Run the script to extract metadata:
  ```bash
  ./create-song-metadata.bash /path/to/audio/dir
  ```
This will create a CSV file with the song information, which can be used in the web app for creating playlists from songs.

### 7. Install Requirements and Package

Install the necessary requirements and package:
  ```bash
  make install
  ```

### 8. Run Tonitunes Service on Startup

Create Tonitunes as a service on startup by running the script:
  ```bash
  ./setup-systemd-service.bash tonitunes-default.service
  ```

### Run Shutdown Service (Optional)

Control shutting off the Raspberry Pi by installing the shutdown service:
  ```bash
  ./setup-systemd-service.bash shutdown-default.service
  ```

## CardManager

- Add new cards via scripts:
  - `scripts/card_registration_to_csv.py`: Running with default configuration, will create a `cards.csv` file in the `.tonibox/cards` directory (directory initialized in step 4).
  - `scripts/card_registration_to_db.py`: Will create new cards directly in the default SQLite database also stored in `.tonibox/sqlite`.
- Add new songs via executing `create-song-metadata.bash`: Will create a `songs.csv` file in the `.tonibox/songs` directory.
- Run Flask app for loading the songs and cards from the CSV files into the SQLite DB.
- Create playlists from songs.
- Map playlists to cards.
- Start Flask app:
  ```bash
  ./cardmanager.bash
  ```
  or run the Docker Compose file via:
  ```bash
  docker compose up --build
  ```

## Contributing

We welcome contributions! Please read our contributing guidelines for more details.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

## Acknowledgements

- [SQLAlchemy](https://www.sqlalchemy.org/) for the ORM.
- [VLC](https://www.videolan.org/vlc/) for the media player.
