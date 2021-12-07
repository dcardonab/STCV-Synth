# Note

These directions assume an [ST Nucleo L476RG Board](https://www.st.com/en/evaluation-tools/nucleo-l476rg.html) for flashing your SensorTile. For instruction on how to connect your SensorTile to the Nucleo board, you may follow the directions in UCLA's SensorTile Curriculum, tutorial 1:

* [MacOS](https://drive.google.com/file/d/1v540B7Kj-gJ9Px35lsvecWksL4ZKAPr_/view)
* [Windows](https://drive.google.com/file/d/1bh39QMUHsFQ8bXTbingEP0JvlwMTbXq4/view)

# Flashing SensorTile Non-Volatile Memory with ST-Link Utility (Windows)

These are instructions to flash data to the SensorTile using the [ST-Link](https://www.st.com/en/development-tools/stsw-link004.html) Windows native utility.

Follow the directions in [UCLA Windows Tutorial 1](https://drive.google.com/file/d/1bh39QMUHsFQ8bXTbingEP0JvlwMTbXq4/view), Chapter 10, Page 67.

When you reach the point of providing a path for the BootLoader and Project binaries, use the following paths:

1. Flash bootloader:
    * `st-flash write ~/Desktop/STCV_Synth/ST_Firmware/binaries/BoorLoaderL4.bin 0x08000000`

2. Flash project:
    * `st-flash write ~/Desktop/STCV_Synth/ST_Firmware/binaries/ALLMEMS1_ST.bin 0x08040000`

Please note that these paths assume that the STCV_Synth folder is in your desktop. Adjust your absolute path accordingly.

Alternatively, use [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html).


# Flashing SensorTile Non-Volatile Memory with stlink Utility (MacOS and Linux)

These are instructions to flash data to the SensorTile using the `stlink` command line utility.

* MacOS - Install via Homebrew:
    * `brew install stlink`


## Flashing Addresses

* Bootloader: 0x08000000
* Project: 0x08004000


## Write

* Main command: `st-flash write <path> <addr>`

    * e.g., This example assumes that the following folder is in your desktop. Please adjust your absolute path accordingly. (If using full STMicroelectronics firmware, for paths to binary files, see [UCLA Windows Tutorial 1](https://drive.google.com/file/d/1bh39QMUHsFQ8bXTbingEP0JvlwMTbXq4/view), Chapter 10, Page 67.)

        1. Flash bootloader:
            * `st-flash write ~/Desktop/STCV_Synth/ST_Firmware/binaries/BoorLoaderL4.bin 0x08000000`

        2. Flash project:
            * `st-flash write ~/Desktop/STCV_Synth/ST_Firmware/binaries/ALLMEMS1_ST.bin 0x08040000`

* Use `--connect-under-reset` option (before `write`) to make it possible to connect to the device before code execution. This is useful when the target contains code that lets the device go to sleep, disables debug pins or other special code.

* `st-flash --help` to visualize all options.

Alternatively, you may attempt using [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html), though this approach has resulted in bugs in MacOS.

## Resources

* Main repo: https://github.com/stlink-org/stlink

* Manual: https://github.com/stlink-org/stlink/blob/develop/doc/tutorial.md
