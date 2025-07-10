# SUPREMEMOOD

## Dylan's working approach to building on Mac
Make sure you pulled submodules so you've got smlie  
Get a nonsystem, nonconda python binary installed  
Create virtual environment:  
```bash
python -m venv .venv
```

Install universal binaries:  
```bash
pip install --target $PWD/python_packages --only-binary=:all: --platform macosx_10_13_universal2 -r requirements.txt
```

Update pythonpath:
```bash
export PYTHONPATH=$PWD/python_packages:$PWD/smile:$PYTHONPATH
```

Build app:  
```bash
python3 -m PyInstaller --noconfirm NIMHCogMood.spec
```

## Dylan's working approach to building on Windows
```commandline
conda create -p ./env_kivy20 -c conda-forge python=3.10 kivy=2.3 pyinstaller=4.10 requests kivy-garden
conda activate ./env_kivy20
pip install kivy-deps.sdl2 kivy-deps.glew pyo
pip install -e cogmood/smile
cd cogmood  
export PYTHONPATH=$PWD/smile:$PYTHONPATH
cd package
python -m PyInstaller cogmood_winkivy20.spec
```

## Updated Non-Conda Build Instructions
**Note:** Must use Git Bash or WSL on Windows for compatibility with Make


Create virtual environment: 
```bash
python -m venv .venv
```

Activate venv:
- Windows:
```bash
source .venv/Scripts/activate
```

- Mac:
```bash
source .venv/bin/activate
```

Install requirements:
```bash
pip install -r requirements.txt
```

Go to package directory:
```bash
cd package
```

Use Makefile to call PyInstaller (The Makefile will check for MacOS or Windows or other & call PyInstaller or output message if OS not supported):
```bash
make
```

## Windows build instructions
### Kivy 2.0
Pysinstaller 5.0 took out some tk hooks that kivy 2.0 depends on. kivy 2.1 fixes that, and could be used with pyinstaller 5.0, but there's a mouse issue with kivy 2.1.

After cloning this repo
```commandline
conda create -p ./env_kivy20 -c conda-forge python=3.9 kivy=2.0 pyinstaller=4.10 requests
conda activate ./env_kivy20
pip install kivy-deps.sdl2 kivy-deps.glew pyo
pip install -e cogmood/smile
cd cogmood/package
python -m PyInstaller cogmood_winkivy20.spec
```

## Mac build instructions
### Kivy 2.0
After cloning this repo
```commandline
conda create -p ./env_kivy20 -c conda-forge python=3.9 kivy=2.0 pyinstaller=4.10 requests
conda activate ./env_kivy20
pip install pyo
pip install -e cogmood/smile
cd cogmood/package
python -m PyInstaller cogmood_mackivy20.spec
```
