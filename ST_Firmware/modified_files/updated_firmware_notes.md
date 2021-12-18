# Updates to ALLMEMSv3 Firmware

The following updates were made to the STMicroelectronics distributed firmware, which can be found in the following link: [UCLA AllMEMS Firmware](www.st.com/content/st_com/en/premium-content/sensortile-curriculum-fp-sns-allmems1_firmware_zip.html)

To add the STCV-Synth firmware into the distributed firmware listed above, please do the follwing substitutions (*note that this is only necessary if you wish to further modify the firmware using STM32CubeIDE*):

* Replace `main.c` and the `sensor_service.c` in the following path: `STM32CubeFunctionPack_ALLMEMS1_V3.1/Projects/Multi/Applications/ALLMEMS1/Src/`

* Replace `ALLMEMS1_config.h` in the following path: `STM32CubeFunctionPack_ALLMEMS1_V3.1Projects/Multi/Applications/ALLMEMS1/Inc/`


Below is a breakdown of what was changed, in case you'd rather do the changes manually.


## Update DataLog in main.c and ALLMEMS1_config.h

To take into account the magnetometer offset in the DataLog (data printed to the terminal) so that it matches the BLE GATT data being transferred, the magnetometer offset was subtracted from the read magnetometer values. Additionally, the data was printed as bytearrays to the terminal for correlation when parsing the data when being received in Python. This is not a substantial change, but it is helpful when debugging. The following lines can be added to the `SendMotionData()` function in main.c, right under the `BSP_GYRO_Get_Axes()` function call (line 941):

```cpp
#ifdef ALLMEMS1_DEBUG_NOTIFY_TRAMISSION
  int16_t acc_x_to_send, acc_y_to_send, acc_z_to_send;
  int16_t gyr_x_to_send, gyr_y_to_send, gyr_z_to_send;
  int16_t mag_x_to_send, mag_y_to_send, mag_z_to_send;

  acc_x_to_send = ACC_Value.AXIS_X;
  acc_y_to_send = ACC_Value.AXIS_Y;
  acc_z_to_send = ACC_Value.AXIS_Z;
  ALLMEMS1_PRINTF("ACC_X = %d ; [%x] ", acc_x_to_send, acc_x_to_send);
  ALLMEMS1_PRINTF("ACC_Y = %d ; [%x] ", acc_y_to_send, acc_y_to_send);
  ALLMEMS1_PRINTF("ACC_Z = %d ; [%x]\n\r", acc_z_to_send, acc_z_to_send);

  gyr_x_to_send = GYR_Value.AXIS_X / 100;
  gyr_y_to_send = GYR_Value.AXIS_Y / 100;
  gyr_z_to_send = GYR_Value.AXIS_Z / 100;
  ALLMEMS1_PRINTF("GYR_X = %d ; [%x] ", gyr_x_to_send, gyr_x_to_send);
  ALLMEMS1_PRINTF("GYR_Y = %d ; [%x] ", gyr_y_to_send, gyr_y_to_send);
  ALLMEMS1_PRINTF("GYR_Z = %d ; [%x]\n\r", gyr_z_to_send, gyr_z_to_send);

  // Subtract MAG_Offset so that what is sent via GATT and what is
  // printed to the terminal by the Datalog application matches.
  mag_x_to_send = MAG_Value.AXIS_X - MAG_Offset.AXIS_X;
  mag_y_to_send = MAG_Value.AXIS_Y - MAG_Offset.AXIS_Y;
  mag_z_to_send = MAG_Value.AXIS_Z - MAG_Offset.AXIS_Z;
  ALLMEMS1_PRINTF("MAG_X = %d ; [%x] ", mag_x_to_send, mag_x_to_send);
  ALLMEMS1_PRINTF("MAG_Y = %d ; [%x] ", mag_y_to_send, mag_y_to_send);
  ALLMEMS1_PRINTF("MAG_Z = %d ; [%x]\n\r", mag_z_to_send, mag_z_to_send);

  ALLMEMS1_PRINTF("\r\n");
#endif /* ALLMEMS1_DEBUG_NOTIFY_TRAMISSION */
```

To enable DEBUG printing, in `ALLMEMS1_config.h`:
* Uncomment line 96: `#define ALLMEMS1_ENABLE_PRINTF`


## Update ENV Rate in main.c, sensor_service.c, and ALLMEMS1_config.h

To set the environmental data rate, the following updates were made:

* In `main.c`:
    * Line 414:
        * Replace `ENV_UPDATE_MUL_100MS * 100` with `ENV_UPDATE_MUL_10MS * 10`
    * Line 1634 (after adding the Datalog code above):
        * Replace `ENV_UPDATE_MUL_100MS * 200 - 1` with `ENV_UPDATE_MUL_10MS * 10`

* In `sensor_service.c`:
    * In line 2749:
        * Replace `ENV_UPDATE_MUL_100MS*200 - 1` with `ENV_UPDATE_MUL_10MS*10`

* In `ALLMEMS1_config.h`:
    * Line 113:
        * Replace `#define ENV_UPDATE_MUL_100MS 5` with `#define ENV_UPDATE_MUL_10MS 1`


## Update Number of Quaternions and Quaternion Rate

The quaternion transfer rate was set to transfer 1 vector quaternion (the thee imaginary values unconstrained by unit length) every 10ms. This is done by modifying the `ALLMEMS1_config.h` file constants:

* Line 74:
    * Replace `#define QUAT_UPDATE_MUL_10MS 3` with `#define QUAT_UPDATE_MUL_10MS 1`

* Line 77:
    * Replace `#define SEND_N_QUATERNIONS 3` with `#define SEND_N_QUATERNIONS 1`
