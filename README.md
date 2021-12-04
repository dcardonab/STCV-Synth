# Install Dependecies

## MAC and Windows

To install all dependencies, run: `pip install -r requirements.txt`


## Debian and Ubuntu

1. Follow these instructions to install **Pyo**:
    * http://ajaxsoundstudio.com/pyodoc/compiling.html#debian-ubuntu-apt-get
    * *Note that this series of commands will also install pip, which is required for step 2.*

2. Run: `pip install -r requirements_linux.txt`


# Prepare SensorTile

Flashing the binaries is enough for prepping the SensorTile. See the [documentation](https://github.com/dcardonab/STCV-Synth/tree/main/ST_Firmware/flashing_the_ST.md) on how to do this within the [ST_Firmware](https://github.com/dcardonab/STCV-Synth/tree/main/ST_Firmware) folder.

If you're interested in modifying the firmware, see the [modified_files](https://github.com/dcardonab/STCV-Synth/tree/main/ST_Firmware/modified_files) folder and the [enclosed md file](https://github.com/dcardonab/STCV-Synth/tree/main/ST_Firmware/modified_files/updated_firmware_notes.md).


# Execution

On the STCV-Synth root folder, run: `python main.py`
