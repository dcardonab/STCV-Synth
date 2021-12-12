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

* Numpy
    * [Numpy Math Fuctions](https://numpy.org/doc/stable/reference/routines.math.html)

* OpenCV
    * [Video Capture](https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html)
    * [Video Capture Properties](https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html)

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

* Threading
    * [Python Threading](https://docs.python.org/3/library/threading.html)


# Further Goals

* Add provisions for real-time OpenCV execution. (Potentially using Docker and/or other processes enabled by RabbitMQ)

* Add event handler
    * Set 'esc' key for quitting the program.
    * Set 'p' key for triggering a pause state.

* Add modes of operation based on automatic controller detection upon launch.

* Create shell script for flashing binaries.

* Verify Quaternion computations (i.e., usage of Real value *w*)

* Verify value interpolation in Pyo when updating ADSR 'mul' within a loop.

* Decouple ST async Queues for real-time improvements.

* Video Synth (potentially use PyOpenGL + shaders for GPU execution)

* Add new musical gestures
    * Switch chord type, e.g., major, minor, suspended, augmented, diminished, etc. (this might be quite complicated because of scales are defined in such a way that the data gets quantizes to specific scale steps).

    * Switch chord inversion: assuming a C major chord (with notes C, E, and G), the chord is said to be in its fundamental position when the lowest note is C; it is said to be in first inversion if the bottom note is E (E, G, and C); and it is said to be in second inversion if the bottom note is G (G, C, and E). All of these permutations reflect the same major chord.

    * Add/Remove audio effects.
