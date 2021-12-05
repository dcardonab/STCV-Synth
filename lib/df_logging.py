import uuid
import pandas as pd
import numpy as np
import os

def data_frame_append(environment, motion, quaternions):
    """
    This method creates a pandas dataframe.  The pandas dataframe
    can be added as a record(s) to an existing dataframe
    :param environment: 
    :param motion: 
    :param quaternions: 
    :return: pandas data frame 
    """
    
    if environment and len(environment) == 2:
        # Grabbing the column headings from the tuples
        environment_columns  = ['e_ticks'] + list(environment[1].keys())
        # Retrieving the column values from the environment tuple
        environment_data = [environment[0]] + list(environment[1].values())

    else:
        # Raise a value error if invalid data is passed into the function
        raise ValueError("environment parameter is null or incorrect shape")

    if motion and len(motion) == 2:
        # Grabbing the column headings from the tuples
        motion_columns = ['m_ticks'] + list(motion[1].keys())
        # Retrieving the column values from the motion tuple
        motion_data = [motion[0]] + list(motion[1].values())

    else:
        # Raise a value error if invalid data is passed into the function
        raise ValueError("motion parameter is null or incorrect shape")
    
    if quaternions and len(quaternions) == 2:
        # Since column headings need to be unique, hard coding ws required for i, j,k values
        quaternions_columns = ['m_ticks'] + ['i0', 'j0', 'k0', 'roll',
                                             'pitch', 'yaw', 'i1', 'j1', 'k1', 'roll',
                                             'pitch', 'yaw', 'i2', 'j2', 'k2', 'roll',
                                             'pitch', 'yaw']
        # Retrieving the column values from the motion tuple
        #  lists can be concatenated through the addition sign
        quaternions_data = [quaternions[0]] + list(quaternions[1][0].values()) \
                           + list(quaternions[1][1].values()) \
                           + list(quaternions[1][2].values())

    else:
        # Raise a value error if invalid data is passed into the function
        raise ValueError("quaternions parameter is null or incorrect shape")

    # lists can be concatenated through the addition sign
    # concatenating all the columns to form a single values row in the data frame
    columns = environment_columns + motion_columns + quaternions_columns
   
    all_data = environment_data + motion_data + quaternions_data
    print(columns)
    print(all_data)
    # Using zip to create a new dictionary that form the row for the
    # data frame
    record = dict(zip(columns, all_data))
    # Uniquely identify all the records by creating a UUID column
    # Makes data matching more simple
    record_uuid = uuid.uuid4()
    
    print(record)
    # returning a pandas dataframe to be merged with other data frames
    df = pd.DataFrame(record, index=str(record_uuid))
    
    return df