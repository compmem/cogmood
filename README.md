# SUPREMEMOOD

## Windows build instructions
### Kivy 2.0
Pysinstaller 5.0 took out some tk hooks that kivy 2.0 depends on. kivy 2.1 fixes that, and could be used with pyinstaller 5.0, but there's a mouse issue with kivy 2.1.

After cloning this repo
```commandline
conda create -p ./env_kivy20 -c conda-forge python=3.9 kivy=2.0 pyinstaller=4.10 requests
conda activate ./env_kivy20
pip install kivy-deps.sdl2 kivy-deps.glew pyo pyperclip
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
pip install pyo pyperclip
pip install -e cogmood/smile
cd cogmood/package
python -m PyInstaller cogmood_mackivy20.spec
```
