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
These setting then drive the rendering of the control using OpenCV method calls. 
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
Thus, the graphical user interface classes hold the configuration parameterss, and define the rendering logic that OpenCV provides the image on which these controls are rendered. How then do user actions reach the logic of the application? The answer is MediaPipe. 



## Data
As part of the programming, logging code was developed to capture all data specific to the data received from the sensor tile. This code tracked data such as acceleration, magnitude, Euler angles, and other items.  The data exists under the project root in the folders _analysis->renderExamples_.  Two files, dorian_bpm100_00_motion.csv and A_dorian_bpm100_06_quaternions.csv, are examined in more depth via Python notebooks. 

## Data Analysis
The project logged application data for the purpose of analysis.  An analysis is presented in the notebooks _stcv_linear_regressiondorian_bpm100_00_motion.ipynb_ and notebook_A_dorian_bpm100_06_quaternions.ipynb. The data studied the data produced by the sensor tile for two different perspectives. 

The purpose behind the analyis was to determine the difficulties that might be encounters should the project again attempt to apply machine learning to the applications problem sets. In our numerical experimentations we focused on two main areas, Euler Angles and Quaternion input and outputs. 

### Euler Angles
The first perspective found in stcv_linear_regressiondorian_bpm100_00_motion.ipynb looks at the data from using Euler angles to track motion. Euler angles, while simple to understand and computer, seem to create problems from a mathematical perspection.  In part, this difficulty comes from the trignometric identities used to compute Euler Angles.  Given that the computation of roll, pitch, and yawl in the calculations of $phi$ that creates interesting difficulties. The difficulties arise from the use of the arctan function.
$$
\phi = \arctan \left(\frac{acc_y}{acc_x}  \right)
$$

The input and output of arctan look as follows:

![arctan](arctan2.png)

(Wikimedia Foundation, Inc, 2021)

When viewed in three dimensions, the graph appears as follows
![arctan](arctan01.png)

Obviously, the output of arctan, arctan2 was used in the python code, is nonlinear. Hence, the value of applying linear regression to components of Euler Angles will yield difficulties in fitting data. And indeed, that was seen in the calculations of linear regression.  These calculations are presented in _stcv_linear_regressiondorian_bpm100_00_motion.ipynb_ 

Within that notebook, the data operations begin with investigating correlations from a general sense. The approach was the no assumptions were made about the relationships with the data. Starting with data features with the highest correlations, several graphs were made demonstrating the relationships.  
![accelartion_y_vs_phi](acceleration_y_vs_phi.png)

![phi_vs_acceleration_x](phi_vs_acceleration_x.png)

![phi_vs_acc_x_vs_acc_y](phi_vs_acc_x_vs_acc_y.png)

It is with these graphs that the underlying functions that is nonlinear can be visualized. Nor would a clustering analysis lead to a proper conclusion.  Hence, the data graphs provide significant insight into the data realities produced by the sensor tile. So given that Euler angles include nonlinear functions, it is now known that the use of Euler angles can be approximated with linear regression with any accurate accuracy.  For example, assuming a second-degree polynomial versus a fourth-degree polynomial does not significantly improve the performance of linear regression. 

![second_degree](second_degree.png)

![fourth_degree](fourth_degree.png)

It was determined that the use of Euler angles posed significant challenges for linear regression. The best R-squared for training set using a fourth-degree polynomial was: 0.5315. These results are documented in stcv_linear_regressiondorian_bpm100_00_motion.ipynb in the _analysis_ directory.

### Quaternions
The project also experimented with quaternions. Compared with Euler angles, linear regression proved much more successful, although the experiments were not the same. The experiments were different because quaternions act much differently than Euler angles, even though they can describe the same actions. 

The principal investigation of quaternions appear in the notebook _notebook_A_dorian_bpm100_06_quaternions.ipynb_. The investigation demonstrates that quaternions can be more readily used with linear regression. In fact, experiments demonstrate a possible R-squared for training set of 1.0000 when using a third degree polynomial. 

Fundamentally, graphs of the project data show a fundamental data structure 
that differs from Euler angle actions, as seen in the following graphs. 
![quaternion1](quaternion1.png)
![quaternion_cloud](quaternion_cloud.png)
A complete investigation can be reviewed in _notebook_A_dorian_bpm100_06_quaternions.ipynb_.


## References

Lee, W.-M. (2019). Python Machine Learning. Wiley.

Renotte, N. (2021, June 19). Sign Language Detection using ACTION   RECOGNITION with Python | LSTM Deep Learning Model. YouTube. Retrieved December 17, 2021, from https://www.youtube.com/watch?v=doDUihpj6ro