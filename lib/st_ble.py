# Python Libraries
from ctypes import sizeof
from struct import unpack_from
from sys import platform
from typing import Union

# Third-Party Libraries
from bleak import BleakClient, BleakError, BleakScanner
import numpy as np

# Local Files
from constants import ST_FIRMWARE_NAME, ST_HANDLES
from droppingLifoQueue import droppingLifoQueue


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
              'r', 'theta', 'phi'

        'quaternions_data' second tuple is a dictionary.
        Keys: 'i', 'j', 'k', 'roll', 'pitch', 'yaw'
        """
        self.address = address
        self.client = BleakClient(self.address)
        # A LiFo Queue will ensure that the most recent registered
        # ST data is retrieved
        self.environment_data = droppingLifoQueue(maxsize=1)
        self.motion_data = droppingLifoQueue(maxsize=1)
        self.quaternions_data = droppingLifoQueue(maxsize=1)

        # In a relative quaternion, the initial value of the W (real)
        # component is 1. The information received from the ST is a
        # vector quaternion.
        self.quat_w = 1

    async def BLE_connect(self) -> None:
        """ Connect to SensorTile and ensure connection was established. """
        await self.client.connect()
        assert self.client.is_connected, "ST is not connected"
        print("\tConnected to SensorTile")

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
        if char == ST_HANDLES['environment']:
            await self.environment_callback(data)
        elif char == ST_HANDLES['motion']:
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

        result = unpack_from('<hhhhh', data)

        time_stamp = result[0]

        # Pressure is represented by 4 bytes
        environment_data['pressure'] = result[1]

        environment_data['humidity'] = result[2]

        # The order of the temp sensors is swapped in the ST GATT transfer.
        environment_data['temp1'] = result[4]
        environment_data['temp2'] = result[3]

        # Add data to Queue
        self.environment_data.put_nowait((time_stamp, environment_data))

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

        result = unpack_from('<hhhhhhhhhh', data)

        time_stamp = result[0]

        # Acceleration
        motion_data['acc_x'] = result[1]
        motion_data['acc_y'] = result[2]
        motion_data['acc_z'] = result[3]

        # Gyroscope
        # Data is multiplied by 100 to compensate for the division
        # applied in the firmware. This division is so that the
        # gyroscope data fits in two bytes of data.
        motion_data['gyr_x'] = result[4] * 100
        motion_data['gyr_y'] = result[5] * 100
        motion_data['gyr_z'] = result[6] * 100

        # Magnetometer
        # Incoming magnetometer data has the magnetometer offset
        # subtracted from it prior to being sent.
        motion_data['mag_x'] = result[7]
        motion_data['mag_y'] = result[8]
        motion_data['mag_z'] = result[9]

        """
        Calculate Orientation
        """
        # * 'r' is radial distance (i.e., distance to origin), or magnitude
        # * 'theta' is polar angle (i.e., angle with respect to polar axis)
        # * 'phi' is azimuth angle (i.e., angle of rotation from initial
        #   meridian plane)
        # This implementation of magnitude is faster than alternatives.
        # REF:
        # https://stackoverflow.com/questions/9171158/how-do-you-get-the-magnitude-of-a-vector-in-numpy
        motion_data['r'] = np.round(
            np.sqrt(np.dot(result[1:4], result[1:4])), 2)
        motion_data['theta'] = np.round(
            np.degrees(np.arccos(motion_data['acc_z'] / motion_data['r'])),
            2
        )
        motion_data['phi'] = np.round(
            np.degrees(np.arctan2(motion_data['acc_y'], motion_data['acc_z'])),
            2
        )

        # Add data to Queue
        self.motion_data.put_nowait((time_stamp, motion_data))

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
        quat_data = {}

        result = unpack_from('<hhhh', data)

        # Retrieve time stamp
        time_stamp = result[0]

        # Retrieve First Quaternion
        quat_data['raw_i'] = result[1]
        quat_data['raw_j'] = result[2]
        quat_data['raw_k'] = result[3]

        """
        Calculate Euler Angles
        """
        # Normalize Incoming vector quaternion.
        norm = np.sqrt(np.dot(result[1:], result[1:]))
        vec_q = list(i / norm for i in result[1:]) \
            if norm > 0 else list(result[1:])

        # Add real component to the quaternion.
        q = [self.quat_w] + vec_q

        # Normalize all 4 quaternion values.
        norm = np.sqrt(np.dot(q, q))
        q = list(i / norm for i in q)

        quat_data['norm_w'] = np.round(q[0], 2)
        quat_data['norm_i'] = np.round(q[1], 2)
        quat_data['norm_j'] = np.round(q[2], 2)
        quat_data['norm_k'] = np.round(q[3], 2)

        # Roll is the rotation about the x axis.
        quat_data['roll'] = np.round(np.degrees(
            np.arctan2(
                2 * (q[0] * q[1] + q[2] * q[3]),
                1 - 2 * (q[1] ** 2 + q[2] ** 2)
            )),
            2
        )

        # Pitch is the rotation about the y axis.
        pitch = 2 * (q[0] * q[2] - q[1] * q[3])
        # Prevent passing a value outside the arcsine input range,
        # which is -1 to 1 inclusive.
        if pitch > 1:
            quat_data['pitch'] = np.round(np.degrees(np.arcsin(1)), 2)
        elif pitch < -1:
            quat_data['pitch'] = np.round(np.degrees(np.arcsin(-1)), 2)
        else:
            quat_data['pitch'] = np.round(np.degrees(np.arcsin(pitch)), 2)

        # Yaw is the rotation about the z axis.
        quat_data['yaw'] = np.round(np.degrees(
            np.arctan2(
                2 * (q[0] * q[3] + q[1] * q[2]),
                1 - 2 * (q[2] ** 2 + q[3] ** 2)
            )),
            2
        )

        self.quat_w = q[0]

        # Add data to Queue.
        self.quaternions_data.put_nowait((time_stamp, quat_data))


async def find_ST(firmware_name: str) -> Union[str, None]:
    """
    Scan for addresses that match a given name, and then verify that
    the retrieved address is a string. If that is the case, then return
    the address. If not, offer the user the possibility to search again.
    """
    print("\n\tScanning BLE Devices")
    search_for_ST = True
    while search_for_ST:
        # Find SensorTile address
        address = await scan_ST_address(firmware_name)

        # Check if an address was returned, and break scan
        # if ST address was found.
        if address:
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
        device = await BleakScanner.find_device_by_filter(
            lambda device, _: device.name == firmware_name,
            timeout=10.0
        )
        # print(f"\n\tFound {str(len(devices))} devices.")
        # Find SensorTile
        if device:
            print(f"\n\tFound SensorTile with {firmware_name} firmware.")
            if platform == 'darwin':
                print(f"\tUUID Address: {device.address}")
            else:
                print(f"\tMAC Address: {device.address}")
            return device.address

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
