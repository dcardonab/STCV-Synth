import asyncio
import random
import sys
import time

sys.path.append('lib')
from constants import ST_handles
from st_ble import *
from synth import *


ST_ENVIRONMENT = ST_handles['environment']
ST_MOTION = ST_handles['motion']

async def main():
    ####################
    ### INIT SENSORS ###
    ####################
    # Find ST address
    ST_address = await find_ST()

    # Connect to SensorTile if an address was found.
    if ST_address:
        # Create a SensorTile object, and connect via
        sensor_tile = SensorTile(ST_address)
        # Connect to ST
        await sensor_tile.BLE_connect()

    ########################
    ### INIT SYNTHESIZER ###
    ########################
    synth = Synth()

    print("\n\n\t##### Starting performance #####\n")
    try:
        if ST_address:
            # Enable notifications of motion data.
            await sensor_tile.start_notification(ST_MOTION)
        while True:
            if ST_address:
                # Get data from Queue
                _, ST_data = await sensor_tile.data.get()
                # print(f"\t{ST_data}")

            scale_step = random.choice(synth.scale)
            synth.set_freq(scale_step)
            synth.play()
            await asyncio.sleep(synth.pulse_rate)

    except KeyboardInterrupt:
        print("\n\n\t##### STCV-Synth was stopped #####\n")

    finally:
        synth.stop_server()
        if ST_address:
            await sensor_tile.stop_notification(ST_MOTION)
            await sensor_tile.BLE_disconnect()


if __name__ == "__main__":
    asyncio.run(main())
