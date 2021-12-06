import asyncio
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

    # The server is initialized at a 48kHz sample rate.
    synth = Synth()
    # 'sampletype' of 1 sets the bit depth to 24-bit int for audio recordings.
    synth.server.recordOptions(sampletype=1, quality=1)

    # Create output audio file.
    out_path = synth.get_render_path()

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

        # Start recording of the new file
        synth.server.recstart(out_path + ".wav")

        # TODO add .csv

        while True:

            if ST_address:
                """
                    Get data from Queues using asyncio.gather() method, which
                    concurrently runs awaitable tasks.

                    Every retrieved value is a tuple with the time stamp of
                    the data collected as its first value, and the second
                    value matching the following info:

                    'environment' second tuple value is a dictionary.
                    Keys: 'pressure', 'humidity', 'temp1', 'temp2'

                    'motion' second tuple value is a dictionary.
                    Keys: 'acc_x', 'acc_y', 'acc_z',
                          'gyr_x', 'gyr_y', 'gyr_z',
                          'mag_x', 'mag_y', 'mag_z',
                          'acc_mag', 'gyr_mag', 'mag_mag'

                    'quaternions_data' second tuple value is a list
                    containing three dictionaries.
                    Each dict has keys: 'i', 'j', 'k', 'roll', 'pitch', 'yaw'

                    e.g., Syntax to get 'roll' value of the first quaternion:
                    quaternions[1][0]['roll']
                """
                environment, motion, quaternions = await asyncio.gather(
                    sensor_tile.environment_data.get(),
                    sensor_tile.motion_data.get(),
                    sensor_tile.quaternions_data.get()
                )

            scale_step = random.choice(synth.scale[1])
            synth.set_freq(scale_step)
            synth.play()
            await asyncio.sleep(synth.pulse_rate)

    except KeyboardInterrupt:
        print("\n\n\t##### STCV-Synth was stopped #####\n")

    finally:
        # Stop Synth
        synth.server.recstop()
        synth.stop_server()

        # Stop ST
        if ST_address:
            await sensor_tile.stop_notification(ST_handles['environment'])
            await sensor_tile.stop_notification(ST_handles['motion'])
            await sensor_tile.stop_notification(ST_handles['quaternions'])
            await sensor_tile.BLE_disconnect()


if __name__ == "__main__":
    asyncio.run(main())
