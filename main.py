import asyncio
from asyncio.events import Handle
import random
import sys

sys.path.append('lib')
from lib.constants import ST_handles
from lib.st_ble import *
from lib.synth import *


async def main():

    #######################
    ### INIT SENSORTILE ###
    #######################

    # Find ST address
    ST_address = await find_ST()

    # Connect to SensorTile if an address was found.
    if ST_address:
        # Create a SensorTile object, and connect via
        sensor_tile = SensorTile(ST_address)
        # Connect to ST
        await sensor_tile.BLE_connect()

    ###################
    ### INIT CAMERA ###
    ###################

    # TODO

    ########################
    ### INIT SYNTHESIZER ###
    ########################

    synth = Synth()

    print("\n\n\t##### Starting performance #####\n")
    try:
        if ST_address:
            # Enable notifications of environmental data.
            await sensor_tile.start_notification(ST_handles['environment'])
            # Enable notifications of motion data.
            await sensor_tile.start_notification(ST_handles['motion'])
            # Enable notifications of quaternion data.
            await sensor_tile.start_notification(ST_handles['quaternions'])

        # TODO if camera:

        input("Press enter")
        while True:
            if ST_address:
                # Get data from Queues
                environment_data = await sensor_tile.environment_data.get()
                motion_data = await sensor_tile.motion_data.get()
                quaternions_data = await sensor_tile.quaternions_data.get()

            scale_step = random.choice(synth.scale)
            synth.set_freq(scale_step)
            synth.play()
            await asyncio.sleep(synth.pulse_rate)

    except KeyboardInterrupt:
        print("\n\n\t##### STCV-Synth was stopped #####\n")

    finally:
        # Stop Synth
        synth.stop_server()

        # Stop ST
        if ST_address:
            await sensor_tile.stop_notification(ST_handles['environment'])
            await sensor_tile.stop_notification(ST_handles['motion'])
            await sensor_tile.stop_notification(ST_handles['quaternions'])
            await sensor_tile.BLE_disconnect()


if __name__ == "__main__":
    asyncio.run(main())
