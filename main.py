import asyncio
import numpy as np
import signal
import sys
import time 

sys.path.append('lib')
from lib.constants import *
from lib.df_logging import *
from lib.screen import *
from lib.st_ble import *
from lib.synth import *


async def main():

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

    """
    INIT SYNTHESIZER ENGINE
    """
    print("\n\n##### Initializing Synthesizer #####\n")
    # The server is initialized at a 48kHz sample rate.
    synth = Synth(48000)
    # 'sampletype' of 1 sets the bit depth to 24-bit int for audio recordings.
    synth.server.recordOptions(sampletype=1, quality=1)

    """
    INIT CONTROLLERS
    """
    # Init SensorTile
    print("\n\n##### Initializing Controllers #####\n")

    x = input("\tWould you like the SensorTile controller? (y/n) ")
    if x.lower() == "y":
        # Find ST address
        ST_address = await find_ST(ST_FIRMWARE_NAME)
    else:
        ST_address = False

    # Connect to SensorTile if an address was found.
    if ST_address:
        print("\n\tInitializing SensorTile\n")
        # Create a SensorTile object, and connect via
        sensor_tile = SensorTile(ST_address)
        # Connect to ST
        await sensor_tile.BLE_connect()

    # Init Computer Vision
    x = input("\n\n\tWould you like the computer vision controller? (y/n) ")
    if x.lower() == "y":
        print("\n\tInitializing OpenCV\n")
        screen = Screen()
        screen.bpm_slider.set_bpm(int(60 / synth.bpm))
        screen.plus_minus_subdivision.init_value(int(synth.sub_division))
    else:
        screen = False

    # Wait for three seconds to prevent printed lines from getting into
    # other routines.
    await asyncio.sleep(1)

    """
    PRE-PERFORMANCE
    """
    # Get audio and log file path.
    out_path = synth.get_render_path()

    if ST_address:
        # Enable notifications of SensorTile data and create logger for
        # DataFrames containing SensorTile data from each activated handle.

        # await sensor_tile.start_notification(ST_handles['environment'])
        # environment_dfl = data_frame_logger(f"{out_path}_environment.csv")

        await sensor_tile.start_notification(ST_handles['motion'])
        motion_dfl = data_frame_logger(f"{out_path}_motion.csv")

        await sensor_tile.start_notification(ST_handles['quaternions'])
        quaternions_dfl = data_frame_logger(f"{out_path}_quaternions.csv")


    # Start recording of the new audio file.
    synth.server.recstart(f"{out_path}.wav")
    
    """
    PERFORMANCE
    """
    print("\n\n##### Starting performance #####\n")
    # The running method of a keyboard listener returns a boolean depending
    # on whether the listener is running or not.
    while True:
        # Get and log ST data
        if ST_address:
            # Get data from Queues, create data frames, and add to logger.

            # environment = await sensor_tile.environment_data.get()
            # environment_dataframe = environment_dfl.new_record(environment)
            # await environment_dfl.add_record(environment_dataframe)

            motion = await sensor_tile.motion_data.get()
            motion_dataframe = motion_dfl.new_record(motion)
            await motion_dfl.add_record(motion_dataframe)

            quaternions = await sensor_tile.quaternions_data.get()
            quaternions_dataframe = quaternions_dfl.new_record(quaternions)
            await quaternions_dfl.add_record(quaternions_dataframe)

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

            # Set the amplitude of the delay effect in the mixer
            synth.mixer.setAmp(1, 0, float(np.interp(
                motion[1]['r'],
                (MIN_ACC_MAGNITUDE, MAX_ACC_MAGNITUDE),
                (0.1, 0.5)
            )))

            synth.filt.setFreq(synth.filt_map.get(float(np.interp(
                motion[1]['theta'],
                (MIN_TILT, MAX_TILT),
                (0, 1)
            ))))

            synth.reverb.setBal(float(np.interp(
                motion[1]['phi'],
                (MIN_AZIMUTH, MAX_AZIUMTH),
                (0, 0.707)
            )))

        # Read image from the camera for processing and displaying it.
        # This includes all visual GUI controls.
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
        
            # Update Synth parameters based on CV controllers
            if synth.bpm != 60 / screen.bpm_slider.BPM:
                synth.set_bpm(screen.bpm_slider.BPM)
                synth.set_pulse_rate()

            if int(synth.sub_division) != \
               screen.plus_minus_subdivision.current_value:
                synth.set_subdivision(
                    str(screen.plus_minus_subdivision.current_value)
                )
                synth.set_pulse_rate()

        # Update synth values. Numpy random module is used as opposed
        # to Python's 'random' library, since Numpy will compute random
        # numbers at a C level, improving speed.
        scale_step = np.random.choice(synth.scale[1])
        synth.set_osc_freq(scale_step)
        synth.play()
        time.sleep(synth.pulse_rate)

        if keyboard_interrupt_event.is_set():
            break

    """
    SHUTDOWN ROUTINE
    """
    print("\n\n##### Shutdown Initialized #####")

    # Stop Synth
    synth.server.recstop()
    synth.stop_server()

    # Stop ST
    if ST_address:
        # Stop notification characteristics and write logs to .csv files.

        # await sensor_tile.stop_notification(ST_handles['environment'])
        # await environment_dfl.write_log()

        await sensor_tile.stop_notification(ST_handles['motion'])
        await motion_dfl.write_log()

        await sensor_tile.stop_notification(ST_handles['quaternions'])
        await quaternions_dfl.write_log()

        # Disconnect from ST.
        await sensor_tile.BLE_disconnect()

    print("\n##### Performance Complete #####\n\n")
        

if __name__ == "__main__":
    asyncio.run(main())
