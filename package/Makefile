# Define the spec files for each OS
MAC_SPEC_FILE=cogmood_mac.spec
WIN_SPEC_FILE=cogmood_windows.spec
EXECUTABLE_NAME=NIMHCogMood

# Define UPX executable path
WIN_UPX=upx/windows_upx.exe

# Detect the OS
OS := $(shell uname)

# Build target based on the OS
build:
ifeq ($(OS), Darwin)
	@echo "Building for macOS..."
	pyinstaller --noconfirm $(MAC_SPEC_FILE)
	@echo ".app bundle created at dist/$(EXECUTABLE_NAME).app"
	@echo "Printing Mach-O file info:"
	file dist/$(EXECUTABLE_NAME).app/Contents/MacOS/$(EXECUTABLE_NAME)
else ifeq ($(findstring MINGW64_NT, $(OS)), MINGW64_NT)
	@echo "Building for Windows..."
	pyinstaller --noconfirm --upx-dir $(WIN_UPX) $(WIN_SPEC_FILE)
	@echo "EXE created at dist/$(EXECUTABLE_NAME).exe"
else
	@echo "OS $(OS) not supported."
	exit 1
endif

# Clean target to remove old builds
clean:
	@echo "Cleaning up old build files..."
	rm -rf build dist __pycache__

.PHONY: build clean
