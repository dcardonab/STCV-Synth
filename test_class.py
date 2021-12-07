import pytest
import asyncio
import time
from lib.df_logging import data_frame_logger
from lib.screen import Screen
from lib.geometry_utility import *
from lib import *

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
    
async def test_ui_loop():

    queue = asyncio.Queue()
    screen = Screen()
    
    # loop = asyncio.get_event_loop()
    # server = loop.run_until_complete(screen.show())
    producer = asyncio.create_task(screen.show(queue))
    await asyncio.gather(producer)
    print('---- done producing')

    subdiviion = screen.plus_minus_subdivision.get_current_value()
    bpm = screen.bpm_slider.get_bpm()

if __name__ == "__main__":
    
    asyncio.run(df_logging())
    
    