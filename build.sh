#!/bin/bash

# Define the name of the executable
EXECUTABLE_NAME="Class Watcher"

# Function to build for macOS
build_mac() {
    echo "Building for macOS..."
    pyinstaller --onefile --windowed \
        --add-data ".env:." \
        --icon=assets/icon.icns \
        --name "$EXECUTABLE_NAME" main.py
}

# Function to build for Windows
build_windows() {
    echo "Building for Windows..."
    wine pyinstaller --onefile --windowed \
        --add-data ".env;." \
        --icon=assets/icon.icns \
        --name "$EXECUTABLE_NAME" main.py
}

# Check the argument passed to the script
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <os>"
    echo "Where <os> can be 'mac' or 'windows'."
    exit 1
fi

TARGET_OS="$1"

# Build based on the specified operating system
case "$TARGET_OS" in
    mac)
        build_mac
        ;;
    windows)
        build_windows
        ;;
    *)
        echo "Unsupported OS: $TARGET_OS"
        echo "Please specify 'mac' or 'windows'."
        exit 1
        ;;
esac

echo "Build completed. Check the 'dist' folder for the executable."

