import pytest
from lib.df_logging import data_frame_logger

def test_df_logging():
    dfl = data_frame_logger("test.csv")

    environment = (7745, {'pressure': -29824, 'humidity': 362, 'temp2': 257, 'temp1': 241})
    motion = (7474, {'acc_x': -32, 'acc_y': 0, 'acc_z': 1037, 'gyr_x': -900, 'gyr_y': 300, 'gyr_z': 0, 'mag_x': 146, 'mag_y': 12, 'mag_z': -996, 'acc_mag': 1037.4936144381804, 'gyr_mag': 948.6832980505138, 'mag_mag': 1006.715451356539})
    quaternions = (7484, [{'i': 169, 'j': 6, 'k': 9992, 'roll': 0.0688296650520866, 'pitch': -1.937962384978148, 'yaw': 179.99883584761844}, {'i': 169, 'j': 5, 'k': 9992, 'roll': 0.0573580563195839, 'pitch': -1.9379625985158244, 'yaw': 179.9990298729084}, {'i': 169, 'j': 5, 'k': 9992, 'roll': 0.0573580563195839, 'pitch': -1.9379625985158244, 'yaw': 179.9990298729084}])
    
    new_dataframe = dfl.new_record(environment, motion, quaternions)
    dfl.add_record(new_dataframe)
    dfl.write_log()
    assert not new_dataframe is None


if __name__ == "__main__":
    test_df_logging()