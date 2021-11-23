import asyncio
import logging
import struct

from bleak import BleakClient, BleakError, BleakScanner

from util import *


class SensorTile():
    def __init__(self, address):
        self.address = address
        self.client = BleakClient(self.address)
        # A LiFo Queue will ensure that the most recent registered
        # ST data is retrieved
        self.data = asyncio.LifoQueue(maxsize=1)

    async def BLE_connect(self):
        # Connect to SensorTile
        await self.client.connect()
        # Ensure connection was established
        assert self.client.is_connected, "ST is not connected"
        print("\n\tConnected to SensorTile")

    async def BLE_disconnect(self):
        # Disconnect from SensorTile
        await self.client.disconnect()
        print("\tDisconnected from SensorTile.\n")

    async def start_notification(self, char):
        try:
            await self.client.start_notify(char, self.notification_handler)
        except Exception as e:
            print(f"Error: {e}")

    async def stop_notification(self, char):
        try:
            await self.client.stop_notify(char)
        except Exception as e:
            print(f"Error: {e}")

    # Add data to Queue
    async def notification_handler(self, handle, data):
        # Store incoming data in a dictionary
        data_d = {}

        # Acceleration
        data_d['acc_x'] = struct.unpack_from("<h", data[2:4])[0]
        data_d['acc_y'] = struct.unpack_from("<h", data[4:6])[0]
        data_d['acc_z'] = struct.unpack_from("<h", data[6:8])[0] 

        # Gyroscope
        # Data is multiplied by 100 to compensate for the division
        # applied in the firmware. This division is so that the
        # gyroscope data fits in two bytes of data.
        data_d['gyr_x'] = struct.unpack_from("<h", data[8:10])[0] * 100
        data_d['gyr_y'] = struct.unpack_from("<h", data[10:12])[0] * 100
        data_d['gyr_z'] = struct.unpack_from("<h", data[12:14])[0] * 100

        # Magnetometer
        # Incoming magnetometer data has the magnetometer offset
        # subtracted from it prior to being sent.
        data_d['mag_x'] = struct.unpack_from("<h", data[14:16])[0]
        data_d['mag_y'] = struct.unpack_from("<h", data[16:18])[0]
        data_d['mag_z'] = struct.unpack_from("<h", data[18:20])[0]

        # Calculate Magnitude of each parameter
        data_d['mag_acc'] = magnitude(
            [data_d['acc_x'], data_d['acc_y'], data_d['acc_z']]
        )
        data_d['mag_gyr'] = magnitude(
            [data_d['gyr_x'], data_d['gyr_y'], data_d['gyr_z']]
        )   
        data_d['mag_mag'] = magnitude(
            [data_d['mag_x'], data_d['mag_y'], data_d['mag_z']]
        )

        # Calculate Roll, Pitch, and Yaw
        data_d['roll'] = roll()
        data_d['pitch'] = pitch()
        data_d['yaw'] = yaw()
        
        # Add data to Queue
        await self.data.put((handle, data_d))

        ############
        # Uncomment to print incomming data
        # result = struct.unpack_from("<hhhhhhhhhh", data)
        # print(data)
        # print(result)
        # print(f"\tACC X: {acc_x}\tACC Y: {acc_y}\tACC Z: {acc_z}")
        # print(f"\tGYR X: {gyr_x}\tGYR Y: {gyr_y}\tGYR Z: {gyr_z}")
        # print(f"\tMAG X: {mag_x}\tMAG Y: {mag_y}\tMAG Z: {mag_z}")



async def find_ST():
    print("\n\t##### Scanning BLE Devices #####\n")
    search_for_ST = True
    while search_for_ST:
        # Find SensorTile address
        address = await scan_ST_address()
        # Break scan if ST address was found.
        if verify_ST_address(address):
            return address

        x = input("\tWould you like to scan again? (y/n) ")
        if x.lower() == "n":
            return None


async def scan_ST_address():
    try:
        # Scan BLE devices
        devices = await BleakScanner.discover()
        print(f"\n\tFound {str(len(devices))} devices.")
        # Find SensorTile
        for d in devices:
            if 'AM1V310' in d.name:
                print("\n\tFound SensorTile with AM1V310 firmware.")
                print(f"\tName: {d.name}\tAddress: {d.address}")
                return d.address

    except BleakError:
        print("\n\tPlease turn on your system's bluetooth device.\n")


# A return value of True will halt the search.
def verify_ST_address(address):
    # Verify that an address was retrieved
    if address is None:
        print("""
        No SensorTile was found.
        Please make sure your SensorTile is on.
        If that does not work, ensure you flashed the correct firmware.
        """)
        return False
    else:
        return True


async def read_characteristic(client, char):
    try:
        return await client.read_gatt_char(char)
    except Exception as e:
        print(f"Error: {e}")


async def write_characteristic(client, char, data):
    try:
        await client.write_gatt_char(char, data)
    except Exception as e:
        print(f"Error: {e}")


async def write_descriptor(client, desc, data):
    try:
        await client.write_gatt_descriptor(desc, data)
    except Exception as e:
        print(f"Error: {e}")


async def get_data(self):
    """
        Read all services, characteristics, and descriptors,
        as well as their properties, and values.
            REF: bleak/examples/service_explorer.py
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    for service in self.client.services:
        logger.info(f"[Service] {service}")
        for char in service.characteristics:
            if "read" in char.properties:
                try:
                    value = bytes(await self.client.read_gatt_char(char.uuid))
                    logger.info(
                        f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                    )
                except Exception as e:
                    logger.error(
                        f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {e}"
                    )
            else:
                value = None
                logger.info(
                    f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                )
            for descriptor in char.descriptors:
                try:
                    value = bytes(
                        await self.client.read_gatt_descriptor(descriptor.handle)
                    )
                    logger.info(f"\t\t[Descriptor] {descriptor}) | Value: {value}")
                except Exception as e:
                    logger.error(f"\t\t[Descriptor] {descriptor}) | Value: {e}")
