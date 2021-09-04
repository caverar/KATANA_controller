# KATANA Controller
Proyecto de controlador para amplificador Katana 50

## Dependencias:

Instalación de dependencias:
```
sudo apt install build-essential
sudo apt install python-dev
sudo apt install libasound2-dev
sudo apt install libjack-dev
pip install mido
pip install python-rtmidi
```

### Listar dispositivos midi en linux: 
```
amidi -l

```
### Listar dispositivos midi en Python: 
```
mido.get_output_names()
```