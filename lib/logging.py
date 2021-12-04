import uuid
import pandas as pd
import numpy as np
import os

def data_frame_append(environment, motion, quaternions):
    if environment and len(environment) == 2:
        environment_columns  = ['e_ticks'] + list(environment[1].keys())

        environment_data = [environment[0]] + list(environment[1].values())

    else:
        raise ValueError("environment parameter is null or incorrect shape")
    
    if motion and len(motion) == 2:
        motion_columns = ['m_ticks'] + list(motion[1].keys())

        motion_data = [motion[0]] + list(motion[1].values())

    else:
        raise ValueError("motion parameter is null or incorrect shape")
    if quaternions and len(quaternions) == 2:
        # Since column headings need to be unique, hard coding ws required for i, j,k values
        quaternions_columns = ['m_ticks'] + ['i0', 'j0', 'k0', 'roll',
                                             'pitch', 'yaw', 'i1', 'j1', 'k1', 'roll',
                                             'pitch', 'yaw', 'i2', 'j2', 'k2', 'roll',
                                             'pitch', 'yaw']

        quaternions_data = [quaternions[0]] + list(quaternions[1][0].values()) \
                           + list(quaternions[1][1].values()) \
                           + list(quaternions[1][2].values())

    else:
        raise ValueError("quaternions parameter is null or incorrect shape")

    columns = environment_columns + motion_columns + quaternions_columns
    all_data = environment_data + motion_data + quaternions_data

    record = dict(zip(columns, all_data))
    record_uuid = uuid.uuid4()

    df = pd.DataFrame(record, index=str(record_uuid))
    return df