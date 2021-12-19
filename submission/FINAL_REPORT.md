# Abstract

The STCV-Synth is the first prototype in a series of devices designed to bring creative opportunities to people with disabilities. Additionally, these devices seek to provide novel mechanisms for creating interactive art performances.

Specifically, the STCV-Synth is a music synthesizer made up of two main components, the engine and the controllers. The engine is implemented in Pyo, a Python audio DSP library. The controllers that operate and instruct the behavior of the engine are the SensorTile, by STMicroelectronics, and Computer Vision.


# Introduction

People with disabilities have a limited range of opportunities to express themselves creatively. Depending on the severity of any given condition, the priorities surrounding these individuals revolve around ensuring that their basic survival needs are met, including nutrition, hydration, medical care, and overall comfort. However, the quality of life of a person entails numerous aspects that go beyond these basic needs. Creative expression and communication can bring a lot of fulfillment to a person's life, and in often cases, there are prominent obstacles that prevent people with disabilities from manifesting their artistic creativity.

We aim to bring accessible and effective mediums for any individual to have access to creative expression. Using alternative controllers, such as wearable devices and computer vision, brings an array of possibilities that simplify creative endeavors. We set out to design a music synthesizer operated by both of these devices to turn general motion into musical events. We hope that interactions with our design will bring people joy and ease in what may potentially be a difficult time in their lives. We aim to contribute our grain of sand to the bettering of the lives of few or many.

We named our invention the STCV-Synth, since it is a synthesizer operated by a SensorTile (ST), by STMicroelectronics, and computer vision (CV). The combination of these devices result in performance approaches analogous to performing an orchestra. These controllers are capable of converting general movement into musical expression, and although we have an intended method of use in mind, we are excited to find what new approaches the performers of our invention will come up with.


# Demo Videos

* [Performance – Short Demo](https://www.youtube.com/watch?v=4_abwXvLJU0)

* [Rundown](https://www.youtube.com/watch?v=CzRnUWZmRmQ)


# Design

In this section we have outlined our efforts and explorations towards designing our synth and our controllers, emphasizing findings, obstacles, and conclusions.


## Synthesizer Engine

We developed the engine in charge of generating the audio using `pyo`, a Python audio DSP library developed by Olivier Belanger, containing abstractions that successfully emulate the components that make up an audio synthesizer, including oscillators, filters, envelope generators, signal mixers, audio effects, digital audio device selectors, and other useful utilities.

The library and the documentation are very straight-forward and a lot of experimentation was performed with the selection of various audio generators (i.e., oscillators), filters, and audio effects.

The final engine architecture is contains:
* 1 sawtooth wave oscillator.
* 1 4th-order (24dB per octave) low-pass filter.
* 1 ADSR (attack-decay-sustain-release) envelope generator.
* 1 digital audio mixer.
* 1 digital long-delay.
* 1 algorithmic reverb.

However, we encountered some difficulties at the time of getting Pyo to select the correct audio drivers in Linux. After extensive exploration, we discovered that the solution was instruction Linux to select the *default* audio device upon launching the Pyo audio server. Although this brought a solution, we still wanted to be able to automate this process. We directly wrote a GitHub issue, and Mr. Belanger pointed us towards some Pyo functions that would automatically choose the default audio device. This allowed us to programmatically select the adequate audio device for the performance, hence automating the whole audio server initialization routine.

The simple code to achieve this, included in the `__init__` function of the `synth.py` file, is expressed in the following lines:
```python
# Create a server to handle all communications with
# Portaudio and Portaudio MIDI.
self.server = Server(audio_sample_rate)

# Set the default device of the computer (the one selected in the
# system's audio preferences) as the output device for the server.
self.server.setOutputDevice(pa_get_default_output())

```


## SensorTile

Implementing the SensorTile included extensive studies and experimentation with the provided ALLMEMS version 3.1 firmware. Incorporating the SensorTile was also filled with a variety of challenges. Overcoming these challenges was essential for the proper incorporation of the controller. The results were incredibly effective, and we discovered powerful interactions between the sensor and the synthesizer. In particular, accelerometer data converted into spherical coordinates was the most intuitive way to process and control parameters.


### BLE Connectivity, GATT Characteristics, and Sample Rates

The first big challenge was to accurately transfer data from the SensorTile into the custom Python software. We attempted implementing the _pygatt_ library, but unfortunately this library only implements the Linux BlueZ backend, which prevented cross-compatibility. Exploring available libraries, we came across _bleak_, which is a powerful cross-platform library that permits BLE communication using various Bluetooth backends for Windows, MacOS, and Linux. It was written and developed by Henrik Blidh.

Our explorations with _bleak_ were done alongside with Alvaro Ramirez, another DGMD-E14 student. Together, we discovered what characteristics are available in the SensorTile firmware, and we found efficient ways to navigate the library. We also discovered how to turn on notifications for specific characteristics, and then it was a matter of discovering the best way to unpack the incoming data. We discovered that using the struct library, we could unpack incoming data in a callback function using the `unpack_from()` function, and utilizing the little endian hexadecimal format (`<h`).

Once the parsing of data was properly set, minor modifications were done to the firmware so that the magnetism offset would be taken into account in the magnetometer data. We also made the decision of transferring one quaternion every 10ms (as opposed to 3 quaternions every 30ms). This is because we didn't need to compare the quaternions against one another upon unpacking them from the SensorTile.

Alvaro and us got heavily involved with the _bleak_ library, and to satisfy lingering doubts, Alvaro reached out to Henrik directly, and managed to set up two tutoring session which we all assisted. Henrik shared with us powerful approaches to interacting with _bleak_, and demonstrated some examples that reaffirmed that our work with the library was in fact in the right track. One of the big answers from this session, was the answer to a big challenge that we had been facing, and that was to find a way to stop the main loop using a method other than keyboard interrupt, as keyboard interrupt would cause _asyncio_ to list many errors as there were concurrent processes that weren't terminated. Henrik demonstrated an approach using the _signal_ Python library to override the keyboard interrupt sequence, and turn it into an event that would interrupt the main while loop. This would allow us to use keyboard interrupt not as an interrupting sequence, but as an event to stop the main while loop.

The overriding of the method was:
```python
"""
INIT ESCAPE ROUTINE
"""
# The program will exit upon recieving a keyboard interrupt event.
# Creating an asyncio event will allow the program to gracefully exit.
# If instead a 'try/except' approach is used, the keyboard interrupt
# will conflict with async coroutines that are still running.
keyboard_interrupt_event = asyncio.Event()

# Signal is a library to set handles for asyncronous events.
# SIGINT is the name for the keyboard interrupt event.
# Upon receiving the SIGINT event, the callback function will set
# the asyncio event declared above. This event will halt the main
# while loop execution function.
signal.signal(
    signal.SIGINT,
    lambda *args: keyboard_interrupt_event.set()
)

```

And then, in the while loop, the following code could be added:
```python
if keyboard_interrupt_event.is_set():
    break

```

Just as it was important for us to automate the selection of the audio device when using Pyo, it was important for us to automate the selection of the SensorTile without inputting the MAC address of the device. For this, the `BleakScanner` would search for a device with a name property equal to the name of the device:

```python
async def scan_ST_address(firmware_name: str) -> str:
    """
    Scan for BLE devices that have the correct name property, and return
    the MAC address (or the UUID address in MacOS) for devices that match
    that name property.
    """
    try:
        # Scan BLE devices
        device = await BleakScanner.find_device_by_filter(
            lambda device, _: device.name == firmware_name,
            timeout=10.0
        )
        # print(f"\n\tFound {str(len(devices))} devices.")
        # Find SensorTile
        if device:
            print(f"\n\tFound SensorTile with {firmware_name} firmware.")
            if platform == 'darwin':
                print(f"\tUUID Address: {device.address}")
            else:
                print(f"\tMAC Address: {device.address}")
            return device.address

    except BleakError:
        print("\n\tPlease turn on your system's bluetooth device.\n")
```

### Spherical Coordinates and Data Mapping

Arguably, the most important data when it came to a performative approach was the acceleration data. From acceleration, we calculated spherical coordinates which resulted in very intuitive and effective performance gestures when mapped to specific synthesizer parameters.

The callback function of motion data calculated spherical coordinates prior to modifying the synthesizer's parameters:

```python
async def motion_callback(self, data: bytearray) -> None:
    """
    Retrieve Motion data from incoming bytearrays.
    Accelerometer, gyroscope, and magnetometer data will be sent by the
    ST every 10ms. Each one of the three sensors has been set to their
    maximum ranges (please refer to STMicroelectronics documentation).
    In addition to the sensor data, the magnitude of each sensor is
    being calculated.
    """
    # Store incoming data in a dictionary
    motion_data = {}

    result = unpack_from('<hhhhhhhhhh', data)

    time_stamp = result[0]

    # Acceleration
    motion_data['acc_x'] = result[1]
    motion_data['acc_y'] = result[2]
    motion_data['acc_z'] = result[3]

    # Gyroscope
    # Data is multiplied by 100 to compensate for the division
    # applied in the firmware. This division is so that the
    # gyroscope data fits in two bytes of data.
    motion_data['gyr_x'] = result[4] * 100
    motion_data['gyr_y'] = result[5] * 100
    motion_data['gyr_z'] = result[6] * 100

    # Magnetometer
    # Incoming magnetometer data has the magnetometer offset
    # subtracted from it prior to being sent.
    motion_data['mag_x'] = result[7]
    motion_data['mag_y'] = result[8]
    motion_data['mag_z'] = result[9]

    """
    Calculate Orientation
    """
    # * 'r' is radial distance (i.e., distance to origin), or magnitude
    # * 'theta' is polar angle (i.e., angle with respect to polar axis)
    # * 'phi' is azimuth angle (i.e., angle of rotation from initial
    #   meridian plane)
    # This implementation of magnitude is faster than alternatives.
    # REF:
    # https://stackoverflow.com/questions/9171158/how-do-you-get-the-magnitude-of-a-vector-in-numpy
    motion_data['r'] = np.round(
        np.sqrt(np.dot(result[1:4], result[1:4])), 2)
    motion_data['theta'] = np.round(
        np.degrees(np.arccos(motion_data['acc_z'] / motion_data['r'])),
        2
    )
    motion_data['phi'] = np.round(
        np.degrees(np.arctan2(motion_data['acc_y'], motion_data['acc_z'])),
        2
    )

    # Add data to Queue
    self.motion_data.put_nowait((time_stamp, motion_data))

```

Once spherical coordinates were calculated, it was important to map the ranges of these functions to the synthesizer parameters. For this, various mapping functions were used. One of these functions (the Numpy function `interp`) mapped a number in a given input range to a number in a given output range in a linear scale. The second one (the `Map` function in Pyo) mapped a value between 0 and 1 to a given output value in a given scale, in this case a logarithmic scale.

The magnitude of acceleration or radial distance was set to control various aspects of the envelope generator, which directly affects the amplitude of the signal, increasing loudness and intensity at higher acceleration magnitudes. The polar angle was set to control the low-pass filter cutoff frequency, allowing control of the audio signal's high-frequency content based on the rotation of the sensor. Finally, the azimuth angle was used to control how much reverberation was applied to the audio signal by controlling the balance between the unaffected and the reverberated signals.

This second mapping function can be found in `synth.py` and it reads:

```python
# Maps inputs between 0 and 1 to a range of 20Hz to 20kHz using
# a logarithmic scale.
# REF: http://ajaxsoundstudio.com/pyodoc/api/classes/map.html
self.filt_map = Map(200.0, 20000.0, 'log')

```

The mapping in `main.py` reads as follows:

```python
"""
Set Synth values from ST motion data.
"""
# The magnitude of acceleration will control various parameters
# of the envelope generator, including attack, amplitude
# multiplier, and duration.
synth.amp_env.setAttack(float(np.interp(
    motion[1]['r'],
    (MIN_ACC_MAGNITUDE, MAX_ACC_MAGNITUDE),
    (synth.pulse_rate * 0.9, 0.01)
)))

synth.amp_env.setMul(float(np.interp(
    motion[1]['r'],
    (MIN_ACC_MAGNITUDE, MAX_ACC_MAGNITUDE),
    (0.25, 0.707)
)))

synth.amp_env.setDur(float(np.interp(
    motion[1]['r'],
    (MIN_ACC_MAGNITUDE, MAX_ACC_MAGNITUDE),
    (synth.pulse_rate * 0.9, 0.1)
)))

# Set the amplitude of the delay effect in the mixer.
synth.mixer.setAmp(1, 0, float(np.interp(
    motion[1]['r'],
    (MIN_ACC_MAGNITUDE, MAX_ACC_MAGNITUDE),
    (0.1, 0.5)
)))

# The polar angle controls the low-pass filter cutoff frequency.
synth.filt.setFreq(synth.filt_map.get(float(np.interp(
    motion[1]['theta'],
    (MIN_TILT, MAX_TILT),
    (0, 1)
))))

# The Azimuth angle controls the balance of reverb's dry and wet
# signals (i.e., unaffected and affected signals respectively).
synth.reverb.setBal(float(np.interp(
    motion[1]['phi'],
    (MIN_AZIMUTH, MAX_AZIUMTH),
    (0, 0.707)
)))

```

### Quaternions

Quaternions posed a big challenge in our project. It took a lot of effort and study to decode how to utilize the information, especially because the SensorTile was transferring only the vector quaternion (i.e., the imaginary components). This inference arrived upon studying a paper by Stanford on computing orientation from inertial measurement units, which described that the three imaginary values of a quaternion, unconstrained to unit length, represented a vector quaternion. This was exactly the information that we were receiving. The question was then how to compute the real component from these imaginary components, since by receiving only three components (as opposed to four), we couldn't compute Euler angles from quaternions, as we required all four quaternion components. Further research explained that quaternions may also be computed from relative quaternions, which is a quaternion that takes in 1 as its real value, and 0 for each of the imaginary values. Then, variations in the information could be computed. This was consistent with the data that we were receiving, as the first few vector quaternions upon initializing the quaternion notification handle all had a value of 0. The answer was to keep track of the real component, and normalize that value against previously normalized quaternion values.

The resulting quaternion callback function reads as follows:

```python
async def quaternions_callback(self, data: bytearray) -> None:
    """
    Retrieve Quaternion data from incoming bytearrays.
    A group of three quaternions will be sent by the ST every 30ms.
    Each received quaternion is a vector quaternion with values that
    are not constrained to unit length. However, when computing Euler
    angles, these 3 components are normalized (see util.py).
    The stored quaternion values are the raw non-normalized values.
    """
    # Store incoming data in independent dictionaries
    # Initialize multiple dictionaries using a range for loop.
    quat_data = {}

    result = unpack_from('<hhhh', data)

    # Retrieve time stamp
    time_stamp = result[0]

    # Retrieve First Quaternion
    quat_data['raw_i'] = result[1]
    quat_data['raw_j'] = result[2]
    quat_data['raw_k'] = result[3]

    """
    Calculate Euler Angles
    """
    # Normalize Incoming vector quaternion.
    norm = np.sqrt(np.dot(result[1:], result[1:]))
    vec_q = list(i / norm for i in result[1:]) \
        if norm > 0 else list(result[1:])

    # Add real component to the quaternion.
    q = [self.quat_w] + vec_q

    # Normalize all 4 quaternion values.
    norm = np.sqrt(np.dot(q, q))
    q = list(i / norm for i in q)

    quat_data['norm_w'] = np.round(q[0], 2)
    quat_data['norm_i'] = np.round(q[1], 2)
    quat_data['norm_j'] = np.round(q[2], 2)
    quat_data['norm_k'] = np.round(q[3], 2)

    # Roll is the rotation about the x axis.
    quat_data['roll'] = np.round(np.degrees(
        np.arctan2(
            2 * (q[0] * q[1] + q[2] * q[3]),
            1 - 2 * (q[1] ** 2 + q[2] ** 2)
        )),
        2
    )

    # Pitch is the rotation about the y axis.
    pitch = 2 * (q[0] * q[2] - q[1] * q[3])
    # Prevent passing a value outside the arcsine input range,
    # which is -1 to 1 inclusive.
    if pitch > 1:
        quat_data['pitch'] = np.round(np.degrees(np.arcsin(1)), 2)
    elif pitch < -1:
        quat_data['pitch'] = np.round(np.degrees(np.arcsin(-1)), 2)
    else:
        quat_data['pitch'] = np.round(np.degrees(np.arcsin(pitch)), 2)

    # Yaw is the rotation about the z axis.
    quat_data['yaw'] = np.round(np.degrees(
        np.arctan2(
            2 * (q[0] * q[3] + q[1] * q[2]),
            1 - 2 * (q[2] ** 2 + q[3] ** 2)
        )),
        2
    )

    self.quat_w = q[0]

    # Add data to Queue.
    self.quaternions_data.put_nowait((time_stamp, quat_data))
    
```

It wasn't until we had figured out how to keep track of the real value that we realized that the SensorTile MotionFX library was already computing Euler angles (i.e., yaw, pitch and roll). However, these angles were not being sent via BLE GATT, which meant that a new characteristic had to be declared within the SensorTile firmware. That was a task that presented abundant challenges, and so we decided to keep implementing our own computations in the quaternion callback function, as these did not seem to make a big impact in the runtime of our application.


### Concurrency

A very important library for the development of our project was the Python library *asyncio*. In fact, *bleak* was implemented using *asyncio* in order to perform connectivity in a concurrent fashion. This allowed retrieving information from the callback handles as it became available without constraining the efficiency of the code, not to mention the importance of waiting for specific functions to complete, such as scanning for Bluetooth devices, and connecting to the SensorTile upon discovering it. Concurrency was further explored in the computer vision controller when we decided to perform the update function in a separate thread. An understanding of these concepts came from a series of write-ups by Real Python which explore when to use which kind of approach.

Future implementations of the synthesizer will further explore concurrency by replacing the use of threading for multiprocessing. However, asynchronous connectivity needs to be maintained to satisfy BLE connectivity via *bleak*.


## Computer Vision 

The use of computer vision has always been a requirement STCV project. A user interface that does not require touch to control a fundamental component of the application. However, what was not know at the project's inception was what form the computer vision would take.


### Project Research Experiment

In the early stages of the project, it was not apparent if the STCV application should use a neural network trained to recognize sign language symbols. It was originally envisioned that the STCV project would use sign language to control the application. By using sign language, the user would not be required to touch a user interface.  Instead, computer vision would recognize commands and manage the application. 

Examples of training a neural network exist in plenty. For this project, the work of Nicholas Renotte was utilized.  Starting with Renotte's work, the project refactored his code to remove the face, arms, and torso landmarks that his design made use of. (Renotte, 2021) These items were removed to reduce the overall training load. This effort was successful, as can be seen in the following screenshots.

![Image One](images/Selection_113.png)

The neural network calculated probabilities of which sign language system was being displayed. Based on the highest probability, the sign language symbol was identified.  

```python
model = Sequential()
model.add(LSTM(126, return_sequences=True, activation='relu', input_shape=(30, 126)))
model.add(LSTM(64, return_sequences=True, activation='relu'))
model.add(LSTM(64, return_sequences=False, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(actions.shape[0], activation='softmax'))

model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
model.fit(X_train, y_train, epochs=EPOCHS, callbacks=[tb_callback])

```

(Renotte, 2021)

![Image Two](images/Selection_112.png)

In the end, while the neural networks were easily trained, the accuracy was not comparable to MediaPipe. MediaPipe provides the ability to recognize hands and landmarks assigned by MediaPipe with astonishing ease.  Further, the landmarks provided by MediaPipe provided a simple hand coordinate system that allowed the STCV to become more sophisticated than sign language training of the neural network easily allowed. Simply put, MediaPipe provides more capability with substantially less effort. 

Thus, the code in action_classification.py demonstrates computer vision and a neural network training of sign language, the code is not part of the end product. The fitting and predictition developed reasonable results but still fell short in that following ways.  


### False Results

When using a trained model, the developed algorithm determines the most probable label from the set of labels found in the data.  However, what happens when there is no actual label condition present? In those cases, the training would still attempt to make predictions.  While this scenario could have relieved additional programming, the situation was entirely bypassed with MediaPipe. If there were no hands present in the computer vision field of view, false positives were almost completely avoided


### Significant Training Costs

Google trained MediaPipe trained with a dataset larger than anything the STCV application could accomplish. "To obtain ground truth data, we have manually annotated ~30K real-world images with 21 3D coordinates..." (Google, LLC, 2020). For the project research, code was written to assist in the capturing of images to build model training data.  This work required time and patience since the quality of the images had to be suitable as exemplars.  Early results indicated that building model training data would be time-consuming without yielding a superior product to MediaPipe.   


## MediaPipe Computer Vision

With MediaPipe, hand landmarks are easily identified. The MediaPipe abilities were discovered as a result of the neural network training. Renotte makes use of MediaPipe to extract the landmarks into NumPy arrays that are then submitted to fitting and prediction.  MediaPipe provides "precise keypoint localization of 21 3D hand-knuckle coordinates inside the detected hand regions via regression, that is direct, coordinate prediction." (Google, LLC, 2020) Direct, coordinated predication allowed the project to recognize finger movements exactly. MediaPipe provided for specific finger identification. Once the application could identify finger positions precisely, the application could then substitute the touch interface for a computer vision interface.

![Hand landmarks](images/handlandmarks.png) (Google, LLC, 2020)

Using MediaPipe and combined with OpenCV for Python provided for basis for a touchless user interface. 


## Graphical User Interface

Computer vision forms the basis of the user interface. The user interface makes use of two primary libraries: MediaPipe and OpenCV.  OpenCV is the rendering platform for all user controls. The visual interface of visual controls that are rendered on the screen to provide the grahical interface. These controls are not accessed via mouse and keyboard, but virtually through computer vision. All user controls were created by this project team, since the project is unaware of any applicable OpenCV controls that could adapted to this project. That is not to say that OpenCV does not have user interface controls as part of the library, it does.  Those controls did not meet the project requirements.

The following is an example of the __init__ function for a user interface class written for the project. As seen below, the parameters of the class define the user interface.

```python
class PlusMinusButtons:
    """
    Base Class for Button-based GUI elements.
    """
    def __init__(
        self, x: int, y: int,
        label: str = "Label", label_offset_x: int = 50,
        min_value: int = 1, max_value: int = 100,
        text_color: Tuple[int, int, int] = (255, 255, 255),
        btm_text_color: Tuple[int, int, int] = (4, 201, 126),
        back_color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:

        # Screen Coordinates.
        self.x1 = x         # Left
        self.y1 = y         # Top
        self.x2 = x + 50    # Right (Length)
        self.y2 = y + 50    # Bottom (Height)

        # Button Design.
        self.label = label                              # Button Label
        self.text_color = text_color                    # Text color for label
        self.btm_text_color = btm_text_color            # Text color for botton
        self.back_color = back_color                    # BG color
        self.label_offset_x = self.x1 + label_offset_x  # Distance from button

        # Create a bounding boxes to detect collisions against the buttons.
        self.minus_bounding_box = create_rectangle_array(
            (self.x1, self.y1), (self.x2, self.y2)
        )
        self.plus_bounding_box = create_rectangle_array(
            (self.x1 + 100, self.y1), (self.x2 + 100, self.y2)
        )

        # Set range of GUI element.
        self.min_value = min_value
        self.max_value = max_value

```

These settings then drive the rendering of the control using OpenCV method calls. 

```python
def render(self, img):
    # Create the minus button rectangle.
    cv2.rectangle(
        img, (self.x1, self.y1), (self.x2, self.y2),
        self.back_color, cv2.FILLED
    )

    # Add the 'minus' sign text.
    # The order of drawing sets the display order.
    cv2.putText(
        img, "-", (self.x1 + 12, self.y1 + 35),
        cv2.FONT_HERSHEY_SIMPLEX, 1, self.btm_text_color,
        2, cv2.LINE_AA
    )

    # Create the plus button rectangle.
    cv2.rectangle(
        img, (self.x1 + 100, self.y1), (self.x2 + 100, self.y2),
        self.back_color, cv2.FILLED,
    )

    # Add the 'plus' sign text.
    cv2.putText(
        img, "+", (self.x1 + 112, self.y1 + 35),
        cv2.FONT_HERSHEY_SIMPLEX, 1, self.btm_text_color,
        2, cv2.LINE_AA
    )

    # Draw the label of the control.
    cv2.putText(
        img, self.label, (self.label_offset_x, self.y2),
        cv2.FONT_HERSHEY_SIMPLEX, 1, self.text_color,
        2, cv2.LINE_AA
    )

    # Draw the currently selected value
    cv2.putText(
        img, str(self.value), (self.x2 + 150, self.y2),
        cv2.FONT_HERSHEY_SIMPLEX, 1, self.text_color,
        2, cv2.LINE_AA
    )

    # Return drawn controls overlaid on the image.
    return img

```

Thus, the graphical user interface classes hold the configuration parameters and define the rendering logic that OpenCV provides the image on which these controls are rendered. How then do user actions reach the logic of the application? The answer is MediaPipe. 

MediaPipe provides landmark tracking of hands.  As discussed above, MediaPipe gives precise coordinates of each landmark point in a hand. As such, MediaPipe made it simple to do away with a mouse and keyboard for some operations.  

Given that the application drew user controls, it meant that the boundaries of each control was already known.  To determine if the user was interacting with the controls meant simply running the calculations to see if the index finger control the application had fallen within the boundaries of the user control.  The logic for this was trivial, as seen in the following code from _cv_screen.py_.

```python
def minus_btn_check_collision(self, x: int, y: int) -> Union[bool, None]:
"""
Processes events for the minus botton collision (i.e., the
intersection between a finger landmark and the button).
"""
# Ensure that decreasing the value would not exceed minumum.
if self.min_value < self.value:
    point = Point(x, y)
    # Decrease value if there was a collision.
    if point_intersects(point, self.minus_bounding_box):
        self.set_value(self.value - 1)
        return True

```


## Data

As part of the programming, logging code was developed to capture all data specific to the data received from the sensor tile. This code tracked data such as acceleration, magnitude, Euler angles, and other items.  The data exists under the project root in the folders _analysis->renderExamples_.  Two files, dorian_bpm100_00_motion.csv and A_dorian_bpm100_06_quaternions.csv, are examined in more depth via Python notebooks.

It is also possible to log environmental data by uncommenting the following lines in `main.py`: 96, 97, 123, 124, 125, 250, and 251. This data was not logged nor analyzed in our final submission as we found that environmental data was not as sensitive nor as informative at the time of mapping data to the synth, nor applying data analysis algorithms.

In addition to these .csv files, the synthesizer engine captures .wav files of every execution of the performance. These files are included in the _render_ folder that will be created at the STCV-Synth root directory after the first execution.


## Data Analysis

The project logged application data for the purpose of analysis.  An analysis is presented in the notebooks _stcv_linear_regressiondorian_bpm100_00_motion.ipynb_ and notebook_A_dorian_bpm100_06_quaternions.ipynb. The data studied the data produced by the sensor tile for two different perspectives. 

The purpose behind the analyis was to determine the difficulties that might be encounters should the project again attempt to apply machine learning to the applications problem sets. In our numerical experimentations we focused on two main areas, Euler Angles and Quaternion input and outputs. 


### Euler Angles

The first perspective found in stcv_linear_regressiondorian_bpm100_00_motion.ipynb looks at the data from using Euler angles to track motion. Euler angles, while simple to understand and computer, seem to create problems from a mathematical perspection.  In part, this difficulty comes from the trignometric identities used to compute Euler Angles.  Given that the computation of roll, pitch, and yawl in the calculations of $phi$ that creates interesting difficulties. The difficulties arise from the use of the arctan function.

$$
\phi = \arctan \left(\frac{acc_y}{acc_x}  \right)
$$

The input and output of arctan look as follows:

![arctan](images/arctan2.png)

(Wikimedia Foundation, Inc, 2021)

When viewed in three dimensions, the graph appears as follows:

![arctan](images/arctan01.png)

Obviously, the output of arctan, arctan2 was used in the python code, is nonlinear. Hence, the value of applying linear regression to components of Euler Angles will yield difficulties in fitting data. And indeed, that was seen in the calculations of linear regression.  These calculations are presented in _stcv_linear_regressiondorian_bpm100_00_motion.ipynb_ 

Within that notebook, the data operations begin with investigating correlations from a general sense. The approach was the no assumptions were made about the relationships with the data. Starting with data features with the highest correlations, several graphs were made demonstrating the relationships.

![accelartion_y_vs_phi](images/acceleration_y_vs_phi.png)

![phi_vs_acceleration_x](images/phi_vs_acceleration_x.png)

![phi_vs_acc_x_vs_acc_y](images/phi_vs_acc_x_vs_acc_y.png)

It is with these graphs that the underlying functions that is nonlinear can be visualized. Nor would a clustering analysis lead to a proper conclusion.  Hence, the data graphs provide significant insight into the data realities produced by the sensor tile. So given that Euler angles include nonlinear functions, it is now known that the use of Euler angles can be approximated with linear regression with any accurate accuracy.  For example, assuming a second-degree polynomial versus a fourth-degree polynomial does not significantly improve the performance of linear regression. 

![second_degree](images/second_degree.png)

![fourth_degree](images/fourth_degree.png)

It was determined that the use of Euler angles posed significant challenges for linear regression. The best R-squared for training set using a fourth-degree polynomial was: 0.5315. These results are documented in stcv_linear_regressiondorian_bpm100_00_motion.ipynb in the _analysis_ directory.


### Quaternions in Data Analysis

The project also experimented with quaternions. Compared with Euler angles, linear regression proved much more successful, although the experiments were not the same. The experiments were different because quaternions act much differently than Euler angles, even though they can describe the same actions. 

The principal investigation of quaternions appear in the notebook _notebook_A_dorian_bpm100_06_quaternions.ipynb_. The investigation demonstrates that quaternions can be more readily used with linear regression. In fact, experiments demonstrate a possible R-squared for training set of 1.0000 when using a third degree polynomial. 

Fundamentally, graphs of the project data show a fundamental data structure 
that differs from Euler angle actions, as seen in the following graphs. 
![quaternion1](images/quaternion1.png)
![quaternion_cloud](images/quaternion_cloud.png)

A complete investigation can be reviewed in _notebook_A_dorian_bpm100_06_quaternions.ipynb_.


## NVIDIA Jetson Nano


# Conclusions


# References

Anderson, J. (n.d.). Speed Up Your Python Program With Concurrency – Real Python. Real Python. https://realpython.com/python-concurrency/

Bélanger, O. (n.d.). Pyo 1.0.4 documentation. AJAX SOUND STUDIO. http://ajaxsoundstudio.com/pyodoc/

Lee, W.-M. (2019). Python Machine Learning. Wiley.

Renotte, N. (2021, June 19). Sign Language Detection using ACTION   RECOGNITION with Python | LSTM Deep Learning Model. YouTube. Retrieved December 17, 2021, from https://www.youtube.com/watch?v=doDUihpj6ro

Scheidler, P. (n.d.). Quaternions for Orientation. enDAQ Blog. https://blog.endaq.com/quaternions-for-orientation

Solomon, B. (n.d.). Async IO in Python: A Complete Walkthrough – Real Python. Real Python. https://realpython.com/async-io-python/

Wetzstein, G. (n.d.). EE 267 Virtual Reality Course Notes: 3-DOF Orientation Tracking with IMUs 1 Overview of Inertial Measurement Units. Stanford University. https://stanford.edu/class/ee267/notes/ee267_notes_imu.pdf
