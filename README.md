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


## Setup Instructions

### 1. Set Static IP Address
Configure your device to have a static IP address.

### 2. RFID Configuration
1. Enable SPI:
  ```sh
  sudo raspi-config
  ```
  - Navigate to `Interfacing Options` -> `SPI` and enable it.
2. Reboot the device:
  ```sh
  sudo reboot
  ```
3. Verify SPI is enabled:
  ```sh
  lsmod | grep spi
  ```
  - Expected response (example):
    ```
    spidev                 16384  2
    spi_bcm2835            16384  0

 ```
* set up .env file from .env-default

### 3. Set `settings.ini`
Configure your `settings.ini` file with the necessary settings.

### 4. Run Initialization Script
Run the provided initialization script to set up the environment:
  ```sh
  ./initialize.sh
  ```

### 5. Copy MP3 Files to Device
Transfer your MP3 files to the device. You can use `scp` or any other file transfer method:
  ```sh
  scp /path/to/your/mp3/files/* user@device_ip:/path/to/device/mp3_directory/
  ```

### 6. Extract Song Metadata from MP3 Files
Run the script to extract metadata:
  ```sh
  create-song-metadata.sh /path/to/audio/dir
  ```




## Additional Information
- Ensure your device is connected to the internet.
- Regularly update your system and packages to the latest versions.
- For detailed documentation, refer to the `docs` directory in the project repository.




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


- [SQLAlchemy](https://www.sqlalchemy.org/) for the ORM
- [VLC](https://www.videolan.org/vlc/) for the media player
