# Allows you to just call 'make' to package on Windows (WSL or Git Bash) or MacOS

# Define the spec files for each OS
MAC_SPEC_FILE=cogmood_mac.spec
WIN_SPEC_FILE=cogmood_windows.spec
EXECUTABLE_NAME=SUPREME

# Define UPX executable path
WIN_UPX=upx/windows_upx.exe

# Check OS
OS := $(shell uname)

# Targets for different OS
ifeq ($(OS), Darwin)
    # macOS target
    build:
		@echo "Building for macOS..."
		pyinstaller --noconfirm $(MAC_SPEC_FILE)
		@echo ".app bundle created at dist/$(EXECUTABLE_NAME).app"
		@echo "Printing Mach-O file info:"
		file dist/$(EXECUTABLE_NAME).app/Contents/MacOS/$(EXECUTABLE_NAME)
else ifeq ($(OS), MINGW64_NT) # for 64-bit Windows
	# Windows target (assuming it's called under something like WSL or Git Bash)
    build:
		@echo "Building for Windows..."
		pyinstaller --noconfirm --upx-dir $(WIN_UPX) $(WIN_SPEC_FILE)
		@echo "EXE created at dist/$(EXECUTABLE_NAME).exe"
else
	@echo "OS, $(OS), not supported for packaging."
	exit 1
endif

# Clean target to remove old builds
clean:
	@echo "Cleaning up old build files..."
	rm -rf build dist __pycache__

.PHONY: build clean