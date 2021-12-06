# Install Dependecies

## MAC and Windows

To install all dependencies, run: `pip install -r requirements.txt`


## Debian and Ubuntu

1. Follow these instructions to install **Pyo**:
    * http://ajaxsoundstudio.com/pyodoc/compiling.html#debian-ubuntu-apt-get
    * *Note that this series of commands will also install pip, which is required for step 2.*

2. Run: `pip install -r requirements_linux.txt`


# Prepare SensorTile

Flashing the binaries is enough for prepping the SensorTile. See the [documentation](/ST_Firmware/flashing_the_ST.md) on how to do this within the [ST_Firmware](/ST_Firmware) folder.

If you're interested in modifying the firmware, see the [modified_files](/ST_Firmware/modified_files) folder and the [enclosed md file](/ST_Firmware/modified_files/updated_firmware_notes.md).


# Execution

On the STCV-Synth root folder, run: `python main.py`


# References

* asyncio
    * [Async IO in Python: A Complete Walkthrough](https://realpython.com/async-io-python/)
    * [Documentation](https://docs.python.org/3/library/asyncio.html)

* Bleak
    * [Documentation](https://bleak.readthedocs.io/en/latest/)
    * [GitHub](https://github.com/hbldh/bleak)
    * [Enable Notifications Example](https://github.com/hbldh/bleak/blob/develop/examples/enable_notifications.py)
    * [SensorTag Example](https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py)
    * [Service Explorer Example](https://github.com/hbldh/bleak/blob/develop/examples/service_explorer.py)

* Pyo
    * [Documentation](http://ajaxsoundstudio.com/pyodoc/)

* Quaternions
    * [3-DOF Orientation Tracking - Stanford](https://stanford.edu/class/ee267/notes/ee267_notes_imu.pdf)
    * [Quaternions for Orientation](https://blog.endaq.com/quaternions-for-orientation)
