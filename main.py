"""
Synthesizer controlled via computer vision and a STMicroelectronics
SensorTile. The script will automatically create an audio file using the Pyo
audio DSP library.
"""

# Python Libraries
import argparse
import asyncio
import signal
import sys

# Third-Party Libraries
import numpy as np

# Local Files
sys.path.append('lib')
from lib.constants import ST_FIRMWARE_NAME, ST_HANDLES, ST_SETTINGS
from lib.cv_screen import Screen
from lib.logger import Logger
from lib.st_ble import find_st, SensorTile
from lib.synth import Synth


#######################
### Input Arguments ###
#######################

parser = argparse.ArgumentParser(description="Synthesizer settings.")

# Controller Args
# To avoid using a BooleanOptionalAction, use the '--no' prefix:
#   e.g.: --no-st
parser.add_argument('--st', action=argparse.BooleanOptionalAction,
                    default=False, help="SensorTile toggle")
parser.add_argument('--cv', action=argparse.BooleanOptionalAction,
                    default=True, help="Computer vision toggle")
parser.add_argument('--fps', action=argparse.BooleanOptionalAction,
                    default=False, help="Display FPS.")

# Synth Args
parser.add_argument('-sr', '--sample_rate',
                    type=int, default=48000,
                    help="Set audio sample rate.")
parser.add_argument('-tc', '--tonal_center',
                    type=str, default="A",
                    help="Set tonal center.")
parser.add_argument('-sm', '--scale_mode',
                    type=str, default="dorian",
                    help="Scale mode.")
parser.add_argument('-bm', '--base_multiplier',
                    type=int, default=1,
                    help="Multiplier to set bottom tonal center note.")
parser.add_argument('-or', '--octave_range',
                    type=int, default=2,
                    help="Number of octaves.")
parser.add_argument('-bpm', '--beats_per_min',
                    type=int, default=100,
                    help="BPM in milliseconds.")
parser.add_argument('-sd', '--subdivision',
                    type=int, default=16,
                    help="Tempo subdivision.")

args = parser.parse_args()

synth_config = {
    "sample_rate": args.sample_rate,
    "tonal_center": args.tonal_center,
    "scale_mode": args.scale_mode,
    "base_multiplier": args.base_multiplier,
    "octave_range": args.octave_range,
    "bpm": args.beats_per_min,
    "subdivision": args.subdivision
}


async def main():
    """
    Complete execution of the synth.
    """

    ###########################
    ### INIT ESCAPE ROUTINE ###
    ###########################

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


    ###############################
    ### INIT SYNTHESIZER ENGINE ###
    ###############################

    print("\n\n##### Initializing Synthesizer #####\n")
    # The server is initialized at a 48kHz sample rate.
    synth = Synth(synth_config)
    # 'sampletype' of 1 sets the bit depth to 24-bit int for audio recordings.
    synth.server.recordOptions(sampletype=1, quality=1)


    ########################
    ### INIT CONTROLLERS ###
    ########################

    # Init SensorTile
    print("\n\n##### Initializing Controllers #####\n")

    # Find ST address
    st_address = await find_st(ST_FIRMWARE_NAME) if args.st else False

    # Connect to SensorTile if an address was found.
    if st_address:
        print("\n\tInitializing SensorTile\n")
        # Create a SensorTile object, and connect via
        sensor_tile = SensorTile(st_address)
        # Connect to ST
        await sensor_tile.ble_connect()


    # Init Computer Vision
    if args.cv:
        print("\n\tInitializing OpenCV\n")
        screen = Screen()

        # Wait for OpenCV to initialize.
        await asyncio.sleep(1)

        # Expression will evaluate to true only when the FPS arg is true.
        screen.show_FPS = bool(args.fps)

        screen.init_values(synth)

    else:
        screen = False


    #######################
    ### PRE-PERFORMANCE ###
    #######################

    # Get audio and log file path.
    out_path = synth.get_render_path()

    if st_address:
        # Enable notifications of SensorTile data and create logger for
        # DataFrames containing SensorTile data from each activated handle.

        # await sensor_tile.start_notification(ST_HANDLES['environment'])
        # environment_dfl = data_frame_logger(f"{out_path}_environment.csv")

        await sensor_tile.start_notification(ST_HANDLES['motion'])
        motion_dfl = Logger(f"{out_path}_motion.csv")

        # await sensor_tile.start_notification(ST_HANDLES['quaternions'])
        # quaternions_dfl = data_frame_logger(f"{out_path}_quaternions.csv")

    # Start recording of the new audio file.
    synth.server.recstart(f"{out_path}.wav")

    if screen:
        # Start frame update thread
        screen.thread.start()


    ###################
    ### PERFORMANCE ###
    ###################

    print("\n\n##### Starting performance #####\n")

    # The running method of a keyboard listener returns a boolean depending
    # on whether the listener is running or not.
    while True:
        # Get and log ST data
        if st_address:
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


            #############################################
            ### Set Synth values from ST motion data. ###
            #############################################

            # The magnitude of acceleration will control various parameters
            # of the envelope generator, including attack, amplitude
            # multiplier, and duration.
            synth.amp_env.setAttack(float(np.interp(
                motion[1]['r'],
                (ST_SETTINGS["min_acc_magnitude"], ST_SETTINGS["max_acc_magnitude"]),
                (synth.pulse_rate * 0.9, 0.01)
            )))

            synth.amp_env.setMul(float(np.interp(
                motion[1]['r'],
                (ST_SETTINGS["min_acc_magnitude"], ST_SETTINGS["max_acc_magnitude"]),
                (0.25, 0.707)
            )))

            synth.amp_env.setDur(float(np.interp(
                motion[1]['r'],
                (ST_SETTINGS["min_acc_magnitude"], ST_SETTINGS["max_acc_magnitude"]),
                (synth.pulse_rate * 0.9, 0.1)
            )))

            # Set the amplitude of the delay effect in the mixer.
            synth.mixer.setAmp(1, 0, float(np.interp(
                motion[1]['r'],
                (ST_SETTINGS["min_acc_magnitude"], ST_SETTINGS["max_acc_magnitude"]),
                (0.1, 0.5)
            )))

            # The polar angle controls the low-pass filter cutoff frequency.
            synth.filt.setFreq(synth.filt_map.get(float(np.interp(
                motion[1]['theta'],
                (ST_SETTINGS["min_tilt"], ST_SETTINGS["max_tilt"]),
                (0, 1)
            ))))

            # The Azimuth angle controls the balance of reverb's dry and wet
            # signals (i.e., unaffected and affected signals respectively).
            synth.reverb.setBal(float(np.interp(
                motion[1]['phi'],
                (ST_SETTINGS["min_azimuth"], ST_SETTINGS["max_azimuth"]),
                (0, 0.707)
            )))

        # Read image from the camera for processing and displaying it.
        # This includes all visual GUI controls.
        if screen:
            screen.render()

            ########################################################
            ### Update Synth parameters based on CV controllers. ###
            ########################################################

            # Update synth BPM if it changed in the GUI.
            if synth.bpm != 60 / screen.bpm_slider.bpm:
                synth.set_bpm(screen.bpm_slider.bpm)
                # Apply new BPM to the pulsing rate.
                synth.set_pulse_rate()

            # Update synth subdivision it changed in the GUI.
            if synth.subdivision != \
               screen.subdivision_buttons.value:
                synth.set_subdivision(screen.subdivision_buttons.value)
                # Apply new subdivision to the pulsing rate.
                synth.set_pulse_rate()

            # Update synth octave base if it changed in the GUI.
            if synth.base_key != screen.oct_base_buttons.value:
                synth.set_base(
                    synth.tonal_center,
                    screen.oct_base_buttons.value
                )
                screen.oct_range_buttons.set_max_value(
                    synth.base_mult_and_range[1]
                )

            # Update synth octave range if it changed in the GUI.
            if synth.oct_range != screen.oct_range_buttons.value:
                synth.set_oct_range(screen.oct_range_buttons.value)
                # Apply new octave range to the scale. The first value of
                # the scale tuple contains the name of the scale.
                synth.set_scale(synth.scale[0])
                # Because octave range has constrains based on the octave
                # base, and the GUI element is unconstrained, it needs to
                # be updated in case there was any truncation applied when
                # updating the synth's octave range.
                screen.oct_range_buttons.set_max_value(
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


    ########################
    ### SHUTDOWN ROUTINE ###
    ########################

    print("\n\n##### Shutdown Initialized #####")

    # Stop Synth
    synth.server.recstop()
    synth.stop_server()

    # Stop ST
    if st_address:
        # Stop notification characteristics and write logs to .csv files.

        # await sensor_tile.stop_notification(ST_HANDLES['environment'])
        # await environment_dfl.write_log()

        await sensor_tile.stop_notification(ST_HANDLES['motion'])
        await motion_dfl.write_log()

        # await sensor_tile.stop_notification(ST_HANDLES['quaternions'])
        # await quaternions_dfl.write_log()

        # Disconnect from ST.
        await sensor_tile.ble_disconnect()

    print("\n##### Performance Complete #####\n\n")


if __name__ == "__main__":
    asyncio.run(main())
