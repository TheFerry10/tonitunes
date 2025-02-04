#!/bin/bash

# Define the Python version and package to be installed
PYTHON_VERSION="3.12.8"

# Install pyenv if it's not already installed
if ! command -v pyenv &> /dev/null
then
    echo "pyenv not found. Installing pyenv..."
    curl https://pyenv.run | bash

    # Add pyenv to the shell
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    exec "$SHELL"
else
    echo "pyenv is already installed."
fi

# # Restart the shell to ensure pyenv is properly initialized
# exec "$SHELL"

# # Install the specified Python version if it's not already installed
# if ! pyenv versions | grep -q $PYTHON_VERSION
# then
#     echo "Installing Python $PYTHON_VERSION..."
#     pyenv install $PYTHON_VERSION
# else
#     echo "Python $PYTHON_VERSION is already installed."
# fi

# # Set the local Python version for the project
# pyenv local $PYTHON_VERSION

# # Create a virtual environment
# echo "Creating virtual environment..."
# python -m venv venv

# # Activate the virtual environment
# echo "Activating virtual environment..."
# source venv/bin/activate

# # Install the specified package
# echo "Installing package $PACKAGE..."
# pip install

# # Verify installation
# echo "Verifying installation..."
# python --version
# pip show $PACKAGE

# echo "Setup complete."
