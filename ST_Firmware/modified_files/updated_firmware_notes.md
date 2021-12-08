# Updates to ALLMEMSv3 Firmware

The following updates were made to the STMicroelectronics distributed firmware, which can be found in the following link: [UCLA AllMEMS Firmware](www.st.com/content/st_com/en/premium-content/sensortile-curriculum-fp-sns-allmems1_firmware_zip.html)

Please replace the `main.c` and the `sensor_service.c` files provided with the STMicroelectronics firmware in the following path: `STM32CubeFunctionPack_ALLMEMS1_V3.1/Projects/Multi/Applications/ALLMEMS1/Src`

## Update ENV rate

To set the environmental data rate, the following updates were made to `main.c` and `sensor_service.c`:

* `ENV_UPDATE_MUL_100MS` to `ENV_UPDATE_MUL_10MS`
* `ENV_UPDATE_MUL_100MS * 200 - 1` to `ENV_UPDATE_MUL_10MS * 10`


## Update DataLog

To take into account the magnetometer offset in the DataLog (data printed to the terminal) so that it matches the BLE GATT data being transferred, the following was updated in `main.c`, circa line 960 (see UCLA tutorial 8 and add this data to the modifications in the tutorial):

* `mag_x_to_send = MAG_Value.AXIS_X - MAG_Offset.AXIS_X;`
* `mag_y_to_send = MAG_Value.AXIS_Y - MAG_Offset.AXIS_Y;`
* `mag_z_to_send = MAG_Value.AXIS_Z - MAG_Offset.AXIS_Z;`

Additionally, the data was printed as bytearrays to the terminal for correlation when parsing the data when being received in Python. This is not a substantial change, but it is helpful when debugging. The following lines can be updated to the same section of the code mentioned above:

* `ALLMEMS1_PRINTF("ACC_X = %d ; [%x] ", acc_x_to_send, acc_x_to_send);`
* `ALLMEMS1_PRINTF("ACC_Y = %d ; [%x] ", acc_y_to_send, acc_y_to_send);`
* `ALLMEMS1_PRINTF("ACC_Z = %d ; [%x]\n\r", acc_z_to_send, acc_z_to_send);`

...

* `ALLMEMS1_PRINTF("GYR_X = %d ; [%x] ", gyr_x_to_send, gyr_x_to_send);`
* `ALLMEMS1_PRINTF("GYR_Y = %d ; [%x] ", gyr_y_to_send, gyr_y_to_send);`
* `ALLMEMS1_PRINTF("GYR_Z = %d ; [%x]\n\r", gyr_z_to_send, gyr_z_to_send);`

...

* `ALLMEMS1_PRINTF("MAG_X = %d ; [%x] ", mag_x_to_send, mag_x_to_send);`
* `ALLMEMS1_PRINTF("MAG_Y = %d ; [%x] ", mag_y_to_send, mag_y_to_send);`
* `ALLMEMS1_PRINTF("MAG_Z = %d ; [%x]\n\r", mag_z_to_send, mag_z_to_send);`

## Update Quaternion Rate

The quaternion transfer rate was set to transfer 1 vector quaternion (the thee imaginary values unconstrained by unit length) every 10ms. This is done by modifying the ALL