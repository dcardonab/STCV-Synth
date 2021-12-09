from struct import unpack_from
from typing import Union

from bleak import BleakClient, BleakError, BleakScanner

from constants import ST_handles
from droppingLifoQueue import droppingLifoQueue
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

        time_stamp = unpack_from("<h", data[:2])[0]

        # Pressure is represented by 4 bytes
        environment_data['pressure'] = unpack_from("<h", data[2:6])[0]

        environment_data['humidity'] = unpack_from("<h", data[6:8])[0]

        # The order of the temp sensors is swapped in the ST GATT transfer.
        environment_data['temp2'] = unpack_from("<h", data[8:10])[0]
        environment_data['temp1'] = unpack_from("<h", data[10:])[0]
        
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

        time_stamp = unpack_from("<h", data[:2])[0]

        # Acceleration
        motion_data['acc_x'] = unpack_from("<h", data[2:4])[0]
        motion_data['acc_y'] = unpack_from("<h", data[4:6])[0]
        motion_data['acc_z'] = unpack_from("<h", data[6:8])[0] 

        # Gyroscope
        # Data is multiplied by 100 to compensate for the division
        # applied in the firmware. This division is so that the
        # gyroscope data fits in two bytes of data.
        motion_data['gyr_x'] = unpack_from("<h", data[8:10])[0] * 100
        motion_data['gyr_y'] = unpack_from("<h", data[10:12])[0] * 100
        motion_data['gyr_z'] = unpack_from("<h", data[12:14])[0] * 100

        # Magnetometer
        # Incoming magnetometer data has the magnetometer offset
        # subtracted from it prior to being sent.
        motion_data['mag_x'] = unpack_from("<h", data[14:16])[0]
        motion_data['mag_y'] = unpack_from("<h", data[16:18])[0]
        motion_data['mag_z'] = unpack_from("<h", data[18:])[0]

        # Calculate Orientation, where:
        # * 'r' is radial distance (i.e., distance to origin), or magnitude
        # * 'theta' is polar angle (i.e., angle with respect to polar axis)
        # * 'phi' is azimuth angle (i.e., angle of rotation from initial
        #   meridian plane)
        motion_data['r'], motion_data['theta'], motion_data['phi'] = \
            orientation_from_acceleration(
                motion_data['acc_x'],
                motion_data['acc_y'],
                motion_data['acc_z']
        )

        # print(f"r: {motion_data['r']}\
        #     \ttheta: {motion_data['theta']}\
        #     \tphi: {motion_data['phi']}", end='\r', flush=True)
        
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

        # Retrieve time stamp
        time_stamp = unpack_from("<h", data[:2])[0]

        # Retrieve First Quaternion
        quat_data['i'] = unpack_from("<h", data[2:4])[0]
        quat_data['j'] = unpack_from("<h", data[4:6])[0]
        quat_data['k'] = unpack_from("<h", data[6:])[0]

        # Calculate Euler angles for first quaternion.
        # Euler angles are rounded to 2 decimal places in 'util.py'.
        quat_data['roll'], quat_data['pitch'], quat_data['yaw'] = \
            vecQ_to_euler(quat_data['i'], quat_data['j'], quat_data['k'])
        
        # Add data to Queue. Note that the quaternion dictionaries are passed
        # as a single list. Since this list is contained in a tuple, the
        # syntax to retrieve quaternion data is: quaternion[1][0]['roll']

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
