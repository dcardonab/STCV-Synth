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
    * [Signal Library](https://docs.python.org/3/library/signal.html)

* asyncio - Modify Queue
    * [CPython - Queue File](https://github.com/python/cpython/blob/d8080c01195cc9a19af752bfa04d98824dd9fb15/Lib/asyncio/queues.py#L235)
    * [Modify Queue to drop old items to make space for new ones](https://stackoverflow.com/questions/54376090/how-to-push-items-off-of-asyncio-priorityqueue-when-it-is-at-maxsize-and-i-put)

* Bleak
    * [Documentation](https://bleak.readthedocs.io/en/latest/)
    * [GitHub](https://github.com/hbldh/bleak)
    * [Enable Notifications Example](https://github.com/hbldh/bleak/blob/develop/examples/enable_notifications.py)
    * [SensorTag Example](https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py)
    * [Service Explorer Example](https://github.com/hbldh/bleak/blob/develop/examples/service_explorer.py)

* Orientation
    * [3-DOF Orientation Tracking - Stanford](https://stanford.edu/class/ee267/notes/ee267_notes_imu.pdf)
    * [Orientation from Acceleration](https://wiki.dfrobot.com/How_to_Use_a_Three-Axis_Accelerometer_for_Tilt_Sensing)
    * [Quaternions for Orientation](https://blog.endaq.com/quaternions-for-orientation)
    * [STMicroelectronics - Orientation](https://drive.google.com/file/d/1Xf-TZg9yErff3C9yOtBsvXd0sC9HHD0M/view)

* Pyo
    * [Documentation](http://ajaxsoundstudio.com/pyodoc/)
    * [GitHub](https://github.com/belangeo/pyo)
    * [Map Function](http://ajaxsoundstudio.com/pyodoc/api/classes/map.html)
    * [Tips for Improving Real-Time Performance](http://ajaxsoundstudio.com/pyodoc/perftips.html)

* General
    * [Scale one range to another](https://stackoverflow.com/questions/4154969/how-to-map-numbers-in-range-099-to-range-1-01-0/33127793)
