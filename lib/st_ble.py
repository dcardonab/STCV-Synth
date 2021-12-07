import asyncio
import struct
from typing import Union

from bleak import BleakClient, BleakError, BleakScanner

from constants import ST_handles
from util import *


class SensorTile():
    def __init__(self, address: str) -> None:
        """
        The SensorTile object contains the MAC address (or UUID address in
        MacOS) of a SensorTile with the appropriate firmware name.
        The object also contains a BleakClient to send requests and receive
        data while the connections is kept alive in main.py.
        The incoming data will be stored in individual asyncio LifoQueues
        for retrieving the most recent available data in main.py as it becomes
        available.

        Every retrieved value is a tuple with the time stamp of
        the data collected as its first value (in ticks), and the
        second value depends on the data source, and matches the
        following info:

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
        self.address = address
        self.client = BleakClient(self.address)
        # A LiFo Queue will ensure that the most recent registered
        # ST data is retrieved
        self.environment_data = asyncio.LifoQueue(maxsize=1)
        self.motion_data = asyncio.LifoQueue(maxsize=1)
        self.quaternions_data = asyncio.LifoQueue(maxsize=1)

    async def BLE_connect(self) -> None:
        """ Connect to SensorTile and ensure connection was established. """
        await self.client.connect()
        assert self.client.is_connected, "ST is not connected"
        print("\n\tConnected to SensorTile")

    async def BLE_disconnect(self) -> None:
        """ Disconnect from SensorTile """
        await self.client.disconnect()
        print("\tDisconnected from SensorTile.\n")

    async def start_notification(self, char: Union[int, str]) -> None:
        """
        Start receiving notifications from a given handle.
        """
        try:
            await self.client.start_notify(char, self.notification_callback)
        except Exception as e:
            print(f"Error: {e}")

    async def stop_notification(self, char: Union[int, str]) -> None:
        """
        Stop receiving notifications from a given handle.
        """
        try:
            await self.client.stop_notify(char)
        except Exception as e:
            print(f"Error: {e}")

    # Add data to Queue
    async def notification_callback(self, char: Union[int, str],
                                    data: bytearray) -> None:
        """
        Redirect incoming notification data to the adequate callback function.
        """
        # Route incoming characteristics to the appropriate callback functions
        if char == ST_handles['environment']:
            await self.environment_callback(data)
        elif char == ST_handles['motion']:
            await self.motion_callback(data)
        else:
            await self.quaternions_callback(data)

    async def environment_callback(self, data: bytearray) -> None:
        """
        Retrieve Environmental data from incoming bytearrays.
        The ST will send barometer data every 10ms.
        """
        # Store incoming data in a dictionary
        environment_data = {}

        time_stamp = struct.unpack_from("<h", data[0:2])[0]

        # Pressure is represented by 4 bytes
        environment_data['pressure'] = struct.unpack_from("<h", data[2:6])[0]

        environment_data['humidity'] = struct.unpack_from("<h", data[6:8])[0]

        # The order of the temp sensors is swapped in the ST GATT transfer.
        environment_data['temp2'] = struct.unpack_from("<h", data[8:10])[0]
        environment_data['temp1'] = struct.unpack_from("<h", data[10:12])[0]
        
        # Add data to Queue
        await self.environment_data.put((time_stamp, environment_data))

    async def motion_callback(self, data: bytearray) -> None:
        """
        Retrieve Motion data from incoming bytearrays.
        Accelerometer, gyroscope, and magnetometer data will be sent by the
        ST every 10ms. Each one of the three sensors has been set to their
        maximum ranges (please refer to STMicroelectronics documentation).
        In addition to the sensor data, the magnitude of each sensor is
        being calculated.
        """
        # Store incoming data in a dictionary
        motion_data = {}

        time_stamp = struct.unpack_from("<h", data[0:2])[0]

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
            motion_data['acc_x'], motion_data['acc_y'], motion_data['acc_z']
        )
        motion_data['gyr_mag'] = magnitude(
            motion_data['gyr_x'], motion_data['gyr_y'], motion_data['gyr_z']
        )   
        motion_data['mag_mag'] = magnitude(
            motion_data['mag_x'], motion_data['mag_y'], motion_data['mag_z']
        )
        
        # Add data to Queue
        await self.motion_data.put((time_stamp, motion_data))

    async def quaternions_callback(self, data: bytearray) -> None:
        """
        Retrieve Quaternion data from incoming bytearrays.
        A group of three quaternions will be sent by the ST every 30ms.
        Each received quaternion is a vector quaternion with values that
        are not constrained to unit length. However, when computing Euler
        angles, these 3 components are normalized (see util.py).
        The stored quaternion values are the raw non-normalized values.
        """
        # Store incoming data in independent dictionaries
        # Initialize multiple dictionaries using a range for loop.
        q1, q2, q3 = ({} for _ in range(3))

        # Retrieve time stamp
        time_stamp = struct.unpack_from("<h", data[0:2])[0]

        # Retrieve First Quaternion
        q1['i'] = struct.unpack_from("<h", data[2:4])[0]
        q1['j'] = struct.unpack_from("<h", data[4:6])[0]
        q1['k'] = struct.unpack_from("<h", data[6:8])[0] 

        # Retrieve Second Quaternion
        q2['i'] = struct.unpack_from("<h", data[8:10])[0]
        q2['j'] = struct.unpack_from("<h", data[10:12])[0]
        q2['k'] = struct.unpack_from("<h", data[12:14])[0]

        # Retrieve Third Quaternion
        q3['i'] = struct.unpack_from("<h", data[14:16])[0]
        q3['j'] = struct.unpack_from("<h", data[16:18])[0]
        q3['k'] = struct.unpack_from("<h", data[18:20])[0]

        # Calculate Euler angles for first quaternion
        q1['roll'], q1['pitch'], q1['yaw'] = vecQ_to_euler(
            q1['i'], q1['j'], q1['k']
        )

        # Calculate Euler angles for second quaternion
        q2['roll'], q2['pitch'], q2['yaw'] = vecQ_to_euler(
            q2['i'], q2['j'], q2['k']
        )

        # Calculate Euler angles for third quaternion
        q3['roll'], q3['pitch'], q3['yaw'] = vecQ_to_euler(
            q3['i'], q3['j'], q3['k']
        )

        # print(f"Roll: {q3['roll']:.2f}\
        #         \tPitch: {q3['pitch']:.2f}\
        #         \tYaw: {q3['yaw']:.2f}", end='\r', flush=True)

        # 'quat_data' is a list containing the dictionaries of each
        # retrieved quaternion.
        quat_data = [q1, q2, q3]
        
        # Add data to Queue
        await self.quaternions_data.put((time_stamp, quat_data))


async def find_ST(firmware_name: str) -> Union[str, None]:
    """
    Scan for addresses that match a given name, and then verify that
    the retrieved address is a string. If that is the case, then return
    the address. If not, offer the user the possibility to search again.
    """
    print("\n\t##### Scanning BLE Devices #####\n")
    search_for_ST = True
    while search_for_ST:
        # Find SensorTile address
        address = await scan_ST_address(firmware_name)

        # Check if an address was returned, and break scan
        # if ST address was found.
        if isinstance(address, type(str)):
            return address
        else:
            print("""
            No SensorTile was found.
            Please make sure your SensorTile is on.
            If that does not work, ensure you flashed the correct firmware.
            """)

        x = input("\tWould you like to scan again? (y/n) ")
        if x.lower() == "n":
            return None


async def scan_ST_address(firmware_name: str) -> str:
    """
    Scan for BLE devices that have the correct name property, and return
    the MAC address (or the UUID address in MacOS) for devices that match
    that name property.
    """
    try:
        # Scan BLE devices
        devices = await BleakScanner.discover()
        print(f"\n\tFound {str(len(devices))} devices.")
        # Find SensorTile
        for d in devices:
            if firmware_name in d.name:
                print("\n\tFound SensorTile with AM1V310 firmware.")
                print(f"\tName: {d.name}\tAddress: {d.address}")
                return d.address

    except BleakError:
        print("\n\tPlease turn on your system's bluetooth device.\n")


async def read_characteristic(client: BleakClient,
                              char: Union[int, str]) -> bytearray:
    """
    Read value from BLE client's specified GATT characteristic.
    """
    try:
        return await client.read_gatt_char(char)
    except Exception as e:
        print(f"Error: {e}")


async def write_characteristic(client: BleakClient,
                               char: Union[int, str],
                               data: bytearray) -> None:
    """
    Write value to BLE client's specified GATT characteristic.
    """
    try:
        await client.write_gatt_char(char, data)
    except Exception as e:
        print(f"Error: {e}")


async def write_descriptor(client: BleakClient,
                           desc: int,
                           data: bytearray) -> None:
    """
    Write value to BLE client's specified GATT descriptor.
    """                           
    try:
        await client.write_gatt_descriptor(desc, data)
    except Exception as e:
        print(f"Error: {e}")
