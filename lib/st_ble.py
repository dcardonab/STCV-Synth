import asyncio
import logging
import struct

from bleak import BleakClient, BleakError, BleakScanner

from constants import ST_handles
from util import *


class SensorTile():
    def __init__(self, address):
        self.address = address
        self.client = BleakClient(self.address)
        # A LiFo Queue will ensure that the most recent registered
        # ST data is retrieved
        self.environment_data = asyncio.LifoQueue(maxsize=1)
        self.motion_data = asyncio.LifoQueue(maxsize=1)
        self.quaternions_data = asyncio.LifoQueue(maxsize=1)

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
    async def notification_handler(self, char, data):
        # Route incoming characteristics to the appropriate callback functions
        if char == ST_handles['environment']:
            await self.environment_callback(data)
        elif char == ST_handles['motion']:
            await self.motion_callback(data)
        else:
            await self.quaternions_callback(data)

    async def environment_callback(self, data):
        # Store incoming data in a dictionary
        environment_data = {}

        environment_data['pressure'] = struct.unpack_from("<h", data[2:4])[0]
        environment_data['humidity'] = struct.unpack_from("<h", data[4:6])[0]
        environment_data['temp2'] = struct.unpack_from("<h", data[6:8])[0]
        environment_data['temp1'] = struct.unpack_from("<h", data[6:8])[0]

        # [print(f"{k}\t{v}") for k, v in environment_data.items()]
        
        # Add data to Queue
        await self.environment_data.put(environment_data)

    async def motion_callback(self, data):
        # Store incoming data in a dictionary
        motion_data = {}

        # Acceleration
        motion_data['acc_x'] = struct.unpack_from("<h", data[2:4])[0]
        motion_data['acc_y'] = struct.unpack_from("<h", data[4:6])[0]
        motion_data['acc_z'] = struct.unpack_from("<h", data[6:8])[0] 

        # Gyroscope
        # Data is multiplied by 100 to compensate for the division
        # applied in the firmware. This division is so that the
        # gyroscope data fits in two bytes of data.
        motion_data['gyr_x'] = struct.unpack_from("<h", data[8:10])[0] * 100
        motion_data['gyr_y'] = struct.unpack_from("<h", data[10:12])[0] * 100
        motion_data['gyr_z'] = struct.unpack_from("<h", data[12:14])[0] * 100

        # Magnetometer
        # Incoming magnetometer data has the magnetometer offset
        # subtracted from it prior to being sent.
        motion_data['mag_x'] = struct.unpack_from("<h", data[14:16])[0]
        motion_data['mag_y'] = struct.unpack_from("<h", data[16:18])[0]
        motion_data['mag_z'] = struct.unpack_from("<h", data[18:20])[0]

        # Calculate Magnitude of each parameter
        motion_data['acc_mag'] = magnitude(
            [motion_data['acc_x'], motion_data['acc_y'], motion_data['acc_z']]
        )
        motion_data['gyr_mag'] = magnitude(
            [motion_data['gyr_x'], motion_data['gyr_y'], motion_data['gyr_z']]
        )   
        motion_data['mag_mag'] = magnitude(
            [motion_data['mag_x'], motion_data['mag_y'], motion_data['mag_z']]
        )

        # [print(f"{k}\t{v}") for k, v in motion_data.items()]
        
        # Add data to Queue
        await self.motion_data.put(motion_data)

    async def quaternions_callback(self, data):
        # Store incoming data in a dictionary
        quaternions_data = {}

        # First Quaternion
        i = struct.unpack_from("<h", data[2:4])[0]
        j = struct.unpack_from("<h", data[4:6])[0]
        k = struct.unpack_from("<h", data[6:8])[0] 

        # # First Quaternion
        # quaternions_data['j_x'] = struct.unpack_from("<h", data[2:4])[0]
        # quaternions_data['j_y'] = struct.unpack_from("<h", data[10:12])[0]
        # quaternions_data['j_z'] = struct.unpack_from("<h", data[12:14])[0]

        # # Second Quaternion
        # quaternions_data['j_x'] = struct.unpack_from("<h", data[8:10])[0]
        # quaternions_data['j_y'] = struct.unpack_from("<h", data[10:12])[0]
        # quaternions_data['j_z'] = struct.unpack_from("<h", data[12:14])[0]

        # # Third Quaternion
        # quaternions_data['k_x'] = struct.unpack_from("<h", data[14:16])[0]
        # quaternions_data['k_y'] = struct.unpack_from("<h", data[16:18])[0]
        # quaternions_data['k_z'] = struct.unpack_from("<h", data[18:20])[0]

        # [print(f"{k}\t{v}") for k, v in quaternions_data.items()]

        norm = magnitude([i, j, k])
        i = i / norm
        j = j / norm
        k = k / norm

        print(f"Roll: {roll(i, j, k):.2f}\t Pitch: {pitch(i, j, k):.2f}\tYaw: {yaw(i, j, k):.2f}", end='\r', flush=True)
        
        # Add data to Queue
        await self.quaternions_data.put(quaternions_data)


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
