# STCV-Synth Demo Videos

* [Performance – Short Demo](https://www.youtube.com/watch?v=4_abwXvLJU0)

* [Rundown](https://www.youtube.com/watch?v=CzRnUWZmRmQ)


# Description

STCV-Synth is the first prototype in a series of devices designed for people with disabilites to express themselves creatively. Secondarily, these devices are designed to create novel approaches for interdisciplinary art performances. It is our hope that we bring new opportunities of expression to artists, non-artists, and any other individual.

The STCV-Synth consists of an audio DSP engine that is operated via two controllers, an STMicroelectronics SensorTile (ST), and Computer Vision (CV). The combination of these controllers create performance approaches analogous to conducting an orchestra.

*Note that you will need at least Python 3.7 to run STCV-Synth, as it heavily relies on the `asyncio` module. We are currently working in developing a workaround for running it on Python 3.6, which is what the NVIDIA Jetson Nano ships out with.*

Created by David Cardona and Robert Fischer.


# Installation

Please refer to the included [installation](/documentation/installation.md) file.


# Prepare SensorTile

![SensorTile](/media/SensorTile_Cradle.jpg)

*Please note that as of right now, the quaternion functionality will only work when the SensorTile is soldered onto a cradle board. Using the SensorTile on a cradle expansion board will result in an error unpacking the data received via GATT. We are working on this and hope to upload a updated version of the firmware that guarantees quaternion compatibility in both the cradle and the cradle expansion boards.*

Flashing the binaries is enough for prepping the SensorTile. See the [documentation](/ST_Firmware/flashing_the_ST.md) on how to do this within the [ST_Firmware](/ST_Firmware) folder.

If you're interested in modifying the firmware, see the [modified_files](/ST_Firmware/modified_files) folder and the [enclosed md file](/ST_Firmware/modified_files/updated_firmware_notes.md).

(*Note that building on Linux is currently not possible as Linux is case-sensitive OS, and there are some case issues in the STMicroelectronics that are inconsistent with this requirement.*)


# Execution

After completing the installation steps for your OS, and flashing you SensorTile, you may run the STCV-Synth from the project's root folder by running: `python main.py`


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

* MediaPipe
    * [Build MediaPipe Python Package](https://google.github.io/mediapipe/getting_started/python.html#building-mediapipe-python-package)
    * [Installation Instructions](https://google.github.io/mediapipe/getting_started/install.html#installing-on-debian-and-ubuntu)

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

* Ubuntu
    * [Upgrade from Python 3.6 to 3.7 on Ubuntu 18.04](http://xtremetechie.com/how-to-upgrade-python-from-3-6-to-3-7-on-ubuntu-18/)


# Further Goals

* Add provisions for real-time OpenCV execution, potentially using Docker and/or other processes enabled by RabbitMQ.

* Enable GPU acceleration.

* Optimize OpenCV performance.

* Gray out GUI plus and minus buttons when the current value is equal to the minimum or maximum.

* Use the ST wearing hand menu to only detect the other hand for polyphony, and the ST hand for GUI operation. This may be unnecessary and different approaches may be taken to determine the functionality that will come from the ST wearing hand vs the other one.

* Implement interactivity using various sensors.

* Add event handler
    * Set 'esc' key for quitting the program.
    * Set 'p' key for triggering a pause state.

* Add modes of operation based on automatic controller detection upon launch.

* Implement 'Sustain' mode of operation. (Determine how to start and stop notes. Perhaps a tapping gesture?)

* Add polyphonic control. (`Voice` class abstraction?)

* Create shell script for flashing binaries.

* Verify Quaternion computations (i.e., usage of Real value *w*).

* Map Quaternion calculated Euler angles to the synth.

* Verify value interpolation in Pyo when updating ADSR 'mul' within a loop.

* Decouple ST async Queues for real-time improvements.

* Video Synth (potentially use PyOpenGL + shaders for GPU execution)

* Add new musical gestures
    * Switch chord type, e.g., major, minor, suspended, augmented, diminished, etc. (this might be quite complicated because of scales are defined in such a way that the data gets quantizes to specific scale steps).

    * Switch chord inversion: assuming a C major chord (with notes C, E, and G), the chord is said to be in its fundamental position when the lowest note is C; it is said to be in first inversion if the bottom note is E (E, G, and C); and it is said to be in second inversion if the bottom note is G (G, C, and E). All of these permutations reflect the same major chord.

    * Add/Remove audio effects.
