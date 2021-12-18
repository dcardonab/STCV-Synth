# Abstract

# Introduction

## Computer Vision 

The use of computer vision has always been a requirement STCV project. A user interface that does not require touch to control a fundamental component of the application. However, what was not know at the project's inception was what form the computer vision would take.

### Project Research Experiment

In the early stages of the project, it was not apparent if the STCV application should use a neural network trained to recognize sign language symbols. It was originally envisioned that the STCV project would use sign language to control the application. By using sign language, the user would not be required to touch a user interface.  Instead, computer vision would recognize commands and manage the application. 

Examples of training a neural network exist in plenty. For this project, the work of Nicholas Renotte was utilized.  Starting with Renotte's work, the project refactored his code to remove the face, arms, and torso landmarks that his design made use of. (Renotte, 2021) These items were removed to reduce the overall training load. This effort was successful, as can be seen in the following screenshots.

![Image One](Selection_113.png)

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

![Image Two](Selection_112.png)

In the end, while the neural networks were easily trained, the accuracy was not comparable to MediaPipe. MediaPipe provides the ability to recognize hands and landmarks assigned by MediaPipe with astonishing ease.  Further, the landmarks provided by MediaPipe provided a simple hand coordinate system that allowed the STCV to become more sophisticated than sign language training of the neural network easily allowed. Simply put, MediaPipe provides more capability with substantially less effort. 

Thus, the code in action_classification.py demonstrates computer vision and a neural network training of sign language, the code is not part of the end product. The fitting and predictition developed reasonable results but still fell short in that following ways.  

### False Results

When using a trained model, the developed algorithm determines the most probable label from the set of labels found in the data.  However, what happens when there is no actual label condition present? In those cases, the training would still attempt to make predictions.  While this scenario could have relieved additional programming, the situation was entirely bypassed with MediaPipe. If there were no hands present in the computer vision field of view, false positives were almost completely avoided

### Significant Training Costs

Google trained MediaPipe trained with a dataset larger than anything the STCV application could accomplish. "To obtain ground truth data, we have manually annotated ~30K real-world images with 21 3D coordinates..." (Google, LLC, 2020). For the project research, code was written to assist in the capturing of images to build model training data.  This work required time and patience since the quality of the images had to be suitable as exemplars.  Early results indicated that building model training data would be time-consuming without yielding a superior product to MediaPipe.   

## MediaPipe Computer Vision

With MediaPipe, hand landmarks are easily identified. The MediaPipe abilities were discovered as a result of the neural network training. Renotte makes use of MediaPipe to extract the landmarks into NumPy arrays that are then submitted to fitting and prediction.  MediaPipe provides "precise keypoint localization of 21 3D hand-knuckle coordinates inside the detected hand regions via regression, that is direct, coordinate prediction." (Google, LLC, 2020) Direct, coordinated predication allowed the project to recognize finger movements exactly. MediaPipe provided for specific finger identification. Once the application could identify finger positions precisely, the application could then substitute the touch interface for a computer vision interface.

![Hand landmarks](handlandmarks.png) (Google, LLC, 2020)

Using MediaPipe and combined with OpenCV for Python provided for basis for a touchless user interface. 

## User Interface

## Data
As part of the programming, logging code was developed to capture all data specific to the data received from the sensor tile. This code tracked data such as acceleration, magnitude, Euler angles, and other items.  The data exists under the project root in the folders _analysis->renderExamples_.  Two files, dorian_bpm100_00_motion.csv and A_dorian_bpm100_06_quaternions.csv, are examined in more depth via Python notebooks. 

## Data Analysis
The project logged application data for the purpose of analysis.  An analysis is presented in the notebooks _stcv_linear_regressiondorian_bpm100_00_motion.ipynb_ and notebook_A_dorian_bpm100_06_quaternions.ipynb. The data studied the data produced by the sensor tile for two different perspectives. 

The purpose behind the analyis was to determine the difficulties that might be encounters should the project again attempt to apply machine learning to the applications problem sets. In our numerical experimentations we focused on two main areas, Euler Angles and Quaternion input and outputs. 

### Euler Angles
The first perspective found in stcv_linear_regressiondorian_bpm100_00_motion.ipynb looks at the data from the perspective of using Euler angles to track motion. Euler angles, while simple to understand and computer do seem to create problems from a mathematical perspection.  In part, this difficulty comes from the trignometric identities used to compute Euler Angles.  Given that the computation of roll, pitch, and yawl, it is in the calculations of $phi$ that creates interesting difficulties. The difficulties arise from the use of the arctan function.

$$
\phi = \arctan \left(\frac{acc_y}{acc_x}  \right)
$$

The input and output of arctan look as follows:

![arctan](arctan2.png)

(Wikimedia Foundation, Inc, 2021)

When viewed in three dimensions, the graph appears as follows
![arctan](arctan01.png)

Obviously the output of arctan, arctan2 was used in the python code, in nonlinear. Hence, the value of applying linear regression to components of Euler Angles will yield difficulties in fitting data. And indeed, that was seen in the calculations of linear regression.  These calculations are presented in _stcv_linear_regressiondorian_bpm100_00_motion.ipynb_ 


## References

Lee, W.-M. (2019). Python Machine Learning. Wiley.

Renotte, N. (2021, June 19). Sign Language Detection using ACTION   RECOGNITION with Python | LSTM Deep Learning Model. YouTube. Retrieved December 17, 2021, from https://www.youtube.com/watch?v=doDUihpj6ro