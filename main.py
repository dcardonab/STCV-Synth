# Python Libraries
import asyncio
import signal
import sys

# Third-Party Libraries
import numpy as np

# Local Files
sys.path.append('lib')
from lib.constants import *
from lib.cv_screen import *
from lib.df_logging import *
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

        # Wait for OpenCV to initialize.
        await asyncio.sleep(1)

        y = input("\n\tWould you like to display FPS? (y/n) ")
        show_FPS = True if y.lower() == "y" else False

        # Set initial GUI values to match the Synth settings.
        screen.bpm_slider.set_bpm(int(60 / synth.bpm))
        screen.subdivision_plus_minus.init_value(int(synth.subdivision))
        screen.octave_base_plus_minus.init_value(int(synth.base_key))
        screen.octave_range_plus_minus.init_value(synth.oct_range)

        # Initialize Menus
        screen.scales_menu.init_value(synth.scale[0])
        screen.pulse_sustain_menu.init_value(list(SYNTH_MODE.keys())[0])
        screen.st_wearing_hand_menu.init_value(list(ST_WEARING_HAND.keys())[0])

    else:
        screen = False

    # Wait for three seconds to prevent printed lines from getting into
    # other routines.
    

    """
    PRE-PERFORMANCE
    """
    # Get audio and log file path.
    out_path = synth.get_render_path()

    if ST_address:
        # Enable notifications of SensorTile data and create logger for
        # DataFrames containing SensorTile data from each activated handle.

        # await sensor_tile.start_notification(ST_HANDLES['environment'])
        # environment_dfl = data_frame_logger(f"{out_path}_environment.csv")

        await sensor_tile.start_notification(ST_HANDLES['motion'])
        motion_dfl = data_frame_logger(f"{out_path}_motion.csv")

        # await sensor_tile.start_notification(ST_HANDLES['quaternions'])
        # quaternions_dfl = data_frame_logger(f"{out_path}_quaternions.csv")


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

            # quaternions = await sensor_tile.quaternions_data.get()
            # quaternions_dataframe = quaternions_dfl.new_record(quaternions)
            # await quaternions_dfl.add_record(quaternions_dataframe)

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
            # Update Octave Range GUI control in case it exceeded the maximum
            # for the selected base.
            screen.CV_loop(show_FPS)
        
            """
            Update Synth parameters based on CV controllers.
            """
            # Update synth BPM if it changed in the GUI.
            if synth.bpm != 60 / screen.bpm_slider.BPM:
                synth.set_bpm(screen.bpm_slider.BPM)
                # Apply new BPM to the pulsing rate.
                synth.set_pulse_rate()

            # Update synth subdivision it changed in the GUI.
            if int(synth.subdivision) != \
               screen.subdivision_plus_minus.value:
                synth.set_subdivision(
                    str(screen.subdivision_plus_minus.value)
                )
                # Apply new subdivision to the pulsing rate.
                synth.set_pulse_rate()

            # Update synth octave base if it changed in the GUI.
            if synth.base_key != screen.octave_base_plus_minus.value:
                synth.set_base(
                    synth.tonal_center,
                    str(screen.octave_base_plus_minus.value)
                )
                screen.octave_range_plus_minus.set_max_value(
                    synth.base_mult_and_range[1]
                )

            # Update synth octave range if it changed in the GUI.
            if synth.oct_range != screen.octave_range_plus_minus.value:
                synth.set_oct_range(screen.octave_range_plus_minus.value)
                # Apply new octave range to the scale. The first value of
                # the scale tuple contains the name of the scale.
                synth.set_scale(synth.scale[0])
                # Because octave range has constrains based on the octave
                # base, and the GUI element is unconstrained, it needs to
                # be updated in case there was any truncation applied when
                # updating the synth's octave range.
                screen.octave_range_plus_minus.set_max_value(
                    synth.base_mult_and_range[1]
                )

            # Update synth scale if it changed in the GUI.
            if synth.scale[0] != screen.scales_menu.get_value():
                synth.set_scale(screen.scales_menu.get_value())

        # Update synth values. Numpy random module is used as opposed
        # to Python's 'random' library, since Numpy will compute random
        # numbers at a C level, improving speed.
        scale_step = np.random.choice(synth.scale[1])
        synth.set_osc_freq(scale_step)
        synth.play()
        await asyncio.sleep(synth.pulse_rate)

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

        # await sensor_tile.stop_notification(ST_HANDLES['environment'])
        # await environment_dfl.write_log()

        await sensor_tile.stop_notification(ST_HANDLES['motion'])
        await motion_dfl.write_log()

        # await sensor_tile.stop_notification(ST_HANDLES['quaternions'])
        # await quaternions_dfl.write_log()

        # Disconnect from ST.
        await sensor_tile.BLE_disconnect()

    print("\n##### Performance Complete #####\n\n")
        

if __name__ == "__main__":
    asyncio.run(main())
