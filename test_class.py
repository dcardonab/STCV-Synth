import pytest
import asyncio
import time
from lib.df_logging import data_frame_logger
from lib.screen import Screen
from lib.geometry_utility import *
from lib.plus_minus_base import PlusMinusBase
from lib import *
import cv2

async def df_logging():
    dfl = data_frame_logger("test.csv", max_record=100000)

    # Sample data
    environment = (7745, {'pressure': -29824, 'humidity': 362, 'temp2': 257, 'temp1': 241})
    motion = (7474, {'acc_x': -32, 'acc_y': 0, 'acc_z': 1037, 'gyr_x': -900, 'gyr_y': 300, 'gyr_z': 0, 'mag_x': 146, 'mag_y': 12, 'mag_z': -996, 'acc_mag': 1037.4936144381804, 'gyr_mag': 948.6832980505138, 'mag_mag': 1006.715451356539})
    quaternions = (7484, [{'i': 169, 'j': 6, 'k': 9992, 'roll': 0.0688296650520866, 'pitch': -1.937962384978148, 'yaw': 179.99883584761844}, {'i': 169, 'j': 5, 'k': 9992, 'roll': 0.0573580563195839, 'pitch': -1.9379625985158244, 'yaw': 179.9990298729084}, {'i': 169, 'j': 5, 'k': 9992, 'roll': 0.0573580563195839, 'pitch': -1.9379625985158244, 'yaw': 179.9990298729084}])
    

    s = time.perf_counter()
    for i in range(2000): 
        new_dataframe = dfl.new_record(environment, motion, quaternions)
        await dfl.add_record(new_dataframe)
    elapsed = time.perf_counter() - s 
    print(f"time elapsed: {elapsed}")
    
    await dfl.write_log()

    assert not new_dataframe is None

def test_df_logging():
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(df_logging())
    task = asyncio.run(df_logging())
    
def test_plus_minus():
    pmb = PlusMinusBase(
            x=1000, y=550, label="8ve base", label_offset_x=840, visible=False)

    x = pmb.get_current_value()
    y = pmb.get_current_value_constant()
    print(x)



def test_ui_loop():

    screen = Screen()
    while True:
        if screen:
                # Import the image
                _, img = screen.cap.read()
                img = cv2.flip(img, 1)

                # Find hand landmarks (i.e., nodes)
                img = screen.detector.findHands(img=img, draw=False)
                for handNumber in range(screen.detector.handCount()):
                    # lmList is a list of all landmarks present in the screen.
                    lmList = screen.detector.find_position(
                        img, hand_number=handNumber, draw=True
                    )
                    img = screen.event_processing(img, lmList)

                header = screen.overlayList[screen.header_index]
                # Determine what controllers to display in the GUI.
                if screen.header_index == 0:
                    screen.hide_settings_controls()
                    img = screen.draw_run_controls(img)
                    
                else:
                    screen.hide_run_controls()
                    img = screen.draw_settings_controls(img)
                    
                assert isinstance(header, object)
                
                img[0: header.shape[0], 0: header.shape[1]] = header
                
                cv2.imshow("Image", img)
                cv2.waitKey(1)

                # Provision to prevent the toggle from staying engaged
                screen.switch_delay += 1
                if screen.switch_delay > 500:
                    screen.switch_delay = 0


    subdiviion = screen.plus_minus_subdivision.get_current_value()
    bpm = screen.bpm_slider.get_bpm()

if __name__ == "__main__":
    
    test_plus_minus()
    
    