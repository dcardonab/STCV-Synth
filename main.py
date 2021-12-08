import asyncio
import random
import signal
import sys

sys.path.append('lib')
from lib.constants import ST_handles, ST_FIRMWARE_NAME
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
    INIT SYNTHESIZER
    """
    # The server is initialized at a 48kHz sample rate.
    synth = Synth(48000)
    # 'sampletype' of 1 sets the bit depth to 24-bit int for audio recordings.
    synth.server.recordOptions(sampletype=1, quality=1)

    """
    INIT SENSORTILE
    """
    x = input("\n\tWould you like the SensorTile controller? (y/n) ")
    if x.lower() == "y":
        # Find ST address
        ST_address = await find_ST(ST_FIRMWARE_NAME)
    else:
        ST_address = False

    # Connect to SensorTile if an address was found.
    if ST_address:
        # Create a SensorTile object, and connect via
        sensor_tile = SensorTile(ST_address)
        # Connect to ST
        await sensor_tile.BLE_connect()

    """
    INIT COMPUTER VISION
    """
    x = input("\n\tWould you like the computer vision controller? (y/n) ")
    if x.lower() == "y":
        screen = Screen()
        screen.bpm_slider.set_bpm(int(60 / synth.bpm))
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
        # Enable notifications of SensorTile data.
        await sensor_tile.start_notification(ST_handles['environment'])
        await sensor_tile.start_notification(ST_handles['motion'])
        await sensor_tile.start_notification(ST_handles['quaternions'])

        # Create Logger for DataFrames containing the SensorTile data.
        dfl = data_frame_logger(f"{out_path}.csv")

    # Start recording of the new audio file.
    synth.server.recstart(f"{out_path}.wav")
    
    """
    PERFORMANCE
    """
    print("\n\n\t##### Starting performance #####\n")
    while True:
        # Get and log ST data
        if ST_address:
            # Get data from Queues using asyncio.gather() method to
            # concurrently run awaitable tasks.
            environment, motion, quaternions = await asyncio.gather(
                sensor_tile.environment_data.get(),
                sensor_tile.motion_data.get(),
                sensor_tile.quaternions_data.get()
            )

            # Create data frame from retrieved info, and add to logger
            new_dataframe = dfl.new_record(environment, motion, quaternions)
            await dfl.add_record(new_dataframe)
        
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
            
            # # Draws the controls
            # img = screen.scales_menu.draw(img)
            # img = screen.pulse_sustain_menu.draw(img)
            # img = screen.left_right_menu.draw(img)

            # header = screen.overlayList[screen.header_index]
            # if screen.header_index == 1:
            #     #  Displays the run control menu
            #     screen.draw_run_controls(img)

            #     screen.pulse_sustain_menu.set_visible(False)
            #     screen.scales_menu.set_visible(False)
            #     screen.left_right_menu.set_visible(False)
            # else:
            #     # Settings controls run controls
            #     screen.pulse_sustain_menu.set_visible(True)
            #     screen.scales_menu.set_visible(True)
            #     screen.left_right_menu.set_visible(True)
            #     screen.hide_run_controls()

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
            synth.set_bpm(screen.bpm_slider.get_bpm())
            synth.set_pulse_rate()

        # Update synth values
        scale_step = random.choice(synth.scale[1])
        synth.set_freq(scale_step)
        synth.play()
        await asyncio.sleep(synth.pulse_rate)

        # Check if keyboard interrupt has been engaged.
        # If so, the loop will break and the Shutdown routine will engage.
        if keyboard_interrupt_event.is_set():
            print("\n\n\t##### STCV-Synth was stopped #####\n")
            break

    """
    SHUTDOWN ROUTINE
    """
    # Stop Synth
    synth.server.recstop()
    synth.stop_server()

    # Stop ST
    if ST_address:
        # Stop notification characteristics.
        await sensor_tile.stop_notification(ST_handles['environment'])
        await sensor_tile.stop_notification(ST_handles['motion'])
        await sensor_tile.stop_notification(ST_handles['quaternions'])
        # Disconnect from ST.
        await sensor_tile.BLE_disconnect()
        # Write logger to .csv file.
        await dfl.write_log()
        

if __name__ == "__main__":
    asyncio.run(main())
