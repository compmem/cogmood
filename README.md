# SUPREMEMOOD

## Windows build instructions
### Kivy 2.0
After cloning this repo
```commandline
conda create -p ./env_kivy20 -c conda-forge python=3.9 kivy=2.0 pyinstaller=4.10 requests
pip install kivy-deps.sdl2 kivy-deps.glew pyo
pip install -e cogmood/smile
cd cogmood/package
python -m PyInstaller cogmood_winkivy20.spec
```
