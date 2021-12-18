# This is a sample Python script.
import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp
from sklearn.model_selection import train_test_split
from sklearn.metrics import multilabel_confusion_matrix, accuracy_score
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import TensorBoard
import argparse


'''
References
This code borrows heavily from the techniques and code used in the following GitHub repository
https://github.com/nicknochnack/ActionDetectionforSignLanguage/blob/main/Action%20Detection%20Refined.ipynb
created by Nicholas Renotte, 2021

This file was a research effort to determine if machine learning or MediaPipe should be used in this project.  
This pre-existing work saved research time and provided a rapid testing scenario.  In the end, the results could not
compare to the 

'''

# MP Holistic model
mp_holistic = mp.solutions.holistic

# Drawing Utilities
mp_drawing = mp.solutions.drawing_utils

DATA_PATH = "MP_Data2"
LOGS_PATH = "Logs2"
EPOCHS = 600

# Actions that we try to detect
actions = np.array(['one', 'two', 'three', 'four'])

# Thirty videos worth of data
no_sequences = 30

# Videos are going to be 30 frames in length
sequence_length = 30

def setup_folders(actions, number_of_sequences):
    '''
    Setting up folders for data collection
    :param actions:
    :param number_of_sequences:
    :return:
    '''
    for action in actions:
        for sequence in range(number_of_sequences):
            try:
                local_path = os.path.join(os.getcwd(), DATA_PATH, action, str(sequence))
                if not os.path.exists(local_path):
                    os.makedirs(local_path)

            except FileNotFoundError as err:
                print(err)


def mediapipe_detection(image, model):
    # Color conversion BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Image is no longer writable
    image.flags.writeable = False

    # Make a prediction
    results = model.process(image)

    # Image is writable
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results


def extract_keypoints(results):
    '''
    The function extract keypoints

    If we don't have results we return np.array with zeros added
    :param results:
    :return: np.concatenate([left_hand, right_hand])
    '''
    left_hand = np.array([[result.x, result.y, result.z] for result in results.left_hand_landmarks.landmark]).flatten() \
        if results.left_hand_landmarks else np.zeros(21 * 3)
    right_hand = np.array(
        [[result.x, result.y, result.z] for result in results.right_hand_landmarks.landmark]).flatten() \
        if results.right_hand_landmarks else np.zeros(21 * 3)

    # return np.concatenate([left_hand, right_hand])
    return np.concatenate([left_hand, right_hand])

def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks,
                              mp_holistic.HAND_CONNECTIONS)  # Draw left-hand connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks,
                              mp_holistic.HAND_CONNECTIONS)  # Draw right-hand connections


def draw_styled_landmarks(image, results):

    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
                              )
    # Draw right-hand connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                              )


def keypoints():
    cap = cv2.VideoCapture(0)

    # Access mediapipe model
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():

            # Read the feed
            ret, frame = cap.read()

            image, results = mediapipe_detection(frame, model=holistic)

            draw_styled_landmarks(image=image, results=results)
            # Show to user
            cv2.imshow('OpenCV Feed', image)

            # Leaving gracefully
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

def get_keypoints_training(no_sequences, sequence_length):
    '''
    Collect Keypoint values for training and testing
    :param no_sequences:
    :param sequence_length:
    :return:
    '''
    cap = cv2.VideoCapture(0)
    # Set mediapipe model

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:

        # NEW LOOP
        # Loop through actions
        try:
            for action in actions:
                # Loop through sequences aka videos
                for sequence in range(no_sequences):
                    # Loop through video length aka sequence length
                    for frame_num in range(sequence_length):

                        # Read feed
                        ret, frame = cap.read()

                        # Make detections
                        image, results = mediapipe_detection(frame, holistic)
                        #                 print(results)

                        # Draw landmarks
                        draw_styled_landmarks(image, results)

                        # NEW Apply wait logic
                        if frame_num == 0:
                            cv2.putText(image, 'Starting Collection', (120, 200),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4, cv2.LINE_AA)
                            cv2.putText(image, 'Collecting frames for {} Video Number {}'.format(action, sequence), (15, 15),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                            # Show to screen
                            cv2.imshow('OpenCV Feed', image)
                            cv2.waitKey(2000)
                        else:
                            cv2.putText(image, 'Collecting frames for {} Video Number {}'.format(action, sequence), (15, 15),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                            # Show to screen
                            cv2.imshow('OpenCV Feed', image)

                        # NEW Export keypoints
                        keypoints = extract_keypoints(results)

                        npy_path = os.path.join(os.getcwd(), DATA_PATH, action, str(sequence), str(frame_num))
                        np.save(npy_path, keypoints)

                        # Break gracefully
                        if cv2.waitKey(10) & 0xFF == ord('q'):
                            break
        finally:
            cap.release()
            cv2.destroyAllWindows()

def process_data(actions, no_sequences, sequence_length):
    label_map = {label:num for num, label in enumerate(actions) }

    sequences, labels = [], []
    for action in actions:
        for sequence in range(no_sequences):
            window = []
            for frame_num in range(sequence_length):
                res = np.load(os.path.join(os.getcwd(), DATA_PATH, action, str(sequence), "{}.npy".format(frame_num)))
                window.append(res)
            sequences.append(window)
            labels.append(label_map[action])

    return sequences, labels


colors = [(245, 117, 16), (117, 245, 16), (16, 117, 245), (245, 117, 245)]

def prob_viz(res, actions, input_frame, colors):
    output_frame = input_frame.copy()
    for num, prob in enumerate(res):
        cv2.rectangle(output_frame, (0, 60 + num * 40), (int(prob * 100), 90 + num * 40), colors[num], -1)
        cv2.putText(output_frame, actions[num], (0, 85 + num * 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                    cv2.LINE_AA)

    return output_frame


def test_in_real_time(model, actions):
    sequence = []
    sentence = []
    threshold = 0.5
    predictions = []

    cap = cv2.VideoCapture(0)

    # Access mediapipe model
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():

            # Read the feed
            ret, frame = cap.read()

            image, results = mediapipe_detection(frame, model=holistic)
            #Draw Landmarks
            draw_styled_landmarks(image=image, results=results)

            # 2. Prediction logic
            keypoints = extract_keypoints(results)
            sequence.append(keypoints)
            sequence = sequence[-30:]

            if len(sequence) == 30:
                res = model.predict(np.expand_dims(sequence, axis=0))[0]
                print(actions[np.argmax(res)])
                predictions.append(np.argmax(res))

                # 3. Viz logic
                if np.unique(predictions[-10:])[0] == np.argmax(res):
                    if res[np.argmax(res)] > threshold:

                        if len(sentence) > 0:
                            if actions[np.argmax(res)] != sentence[-1]:
                                sentence.append(actions[np.argmax(res)])
                        else:
                            sentence.append(actions[np.argmax(res)])

                if len(sentence) > 5:
                    sentence = sentence[-5:]

                # Viz probabilities
                image = prob_viz(res, actions, image, colors)

            cv2.rectangle(image, (0, 0), (640, 40), (245, 117, 16), -1)
            cv2.putText(image, ' '.join(sentence), (3, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            # Show to user
            cv2.imshow('OpenCV Feed', image)

            # Leaving gracefully
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Example with long option names')
    parser.add_argument('--keypoints', action="store_true", default=False, help='Run key points switch')
    parser.add_argument('--folders', action='store_true', default=False, help='Create folders switch')

    results = parser.parse_args()

    if results.keypoints:
        print(results.noarg)
        keypoints()

    if results.folders:
        print(results.folders)
        setup_folders(actions=actions, number_of_sequences=no_sequences)
        get_keypoints_training(no_sequences=no_sequences, sequence_length=sequence_length)

    sequences, labels = process_data(actions=actions, no_sequences=no_sequences, sequence_length=sequence_length)
    label_map = {label: num for num, label in enumerate(actions)}

    sequences, labels = [], []
    for action in actions:
        for sequence in range(no_sequences):
            window = []
            for frame_num in range(sequence_length):
                res = np.load(os.path.join(DATA_PATH, action, str(sequence), "{}.npy".format(frame_num)))
                window.append(res)
            sequences.append(window)
            labels.append(label_map[action])
    print(np.array(labels).shape)

    X = np.array(sequences)

    y = to_categorical(labels).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05)

    log_dir = os.path.join(LOGS_PATH)
    tb_callback = TensorBoard(log_dir=log_dir)

    model = Sequential()
    model.add(LSTM(126, return_sequences=True, activation='relu', input_shape=(30, 126)))
    model.add(LSTM(64, return_sequences=True, activation='relu'))
    model.add(LSTM(64, return_sequences=False, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(actions.shape[0], activation='softmax'))

    model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
    model.fit(X_train, y_train, epochs=EPOCHS, callbacks=[tb_callback])

    model.save('action01.h5')
    print(model.summary())

    res = model.predict(X_test)

    print(np.array(y_test).shape)
    print(actions[np.argmax(res[0])], actions[np.argmax(y_test[0])])
    print(actions[np.argmax(res[1])], actions[np.argmax(y_test[1])])
    print(actions[np.argmax(res[2])], actions[np.argmax(y_test[2])])
    print(actions[np.argmax(res[3])], actions[np.argmax(y_test[3])])
    print(actions[np.argmax(res[4])], actions[np.argmax(y_test[4])])


    yhat = model.predict(X_train)

    ytrue = np.argmax(y_train, axis=1).tolist()
    yhat = np.argmax(yhat, axis=1).tolist()
    print(multilabel_confusion_matrix(ytrue, yhat))

    print(accuracy_score(ytrue, yhat))

    test_in_real_time(model, actions=actions)