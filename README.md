# SUPREMEMOOD

## Windows build instructions
### Kivy 2.0
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
