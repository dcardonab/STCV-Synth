"""
Logger stores sensor data into a CSV file.
"""

# Python Libraries
import os
from typing import Tuple
import uuid

# Third-Patry Libraries
import pandas as pd


class Logger:
    """Class to store sensor data into CSV file."""

    def __init__(self, file_path: str, max_record: int = 10000) -> None:
        """
        file_path is the path to the log file
        max_record is the maximum number of records that can accumulate
        before they are automatically dumped to a file
        """
        self.data_frame_logger = None
        self.file_path = file_path
        self.max_record = max_record

    async def add_record(self, data_frame: pd.DataFrame) -> None:
        """
        Add_record uses the ability to combine two dataframes together
        if the there is no dataframe created, the first dataframes forms the
        main table.
        """
        if self.data_frame_logger is None:
            self.data_frame_logger = data_frame
        else:
            self.data_frame_logger = pd.concat(
                [self.data_frame_logger, data_frame],
                axis=0, join='outer'
            )

        if len(self.data_frame_logger) > self.max_record:
            await self.write_log()
            self.data_frame_logger = None

    async def write_log(self) -> None:
        """
        Write data to a CSV file.
        """
        # If there are no records to write, the logger just returns
        if self.data_frame_logger is None:
            return
        # Write data to existing file.
        elif os.path.isfile(self.file_path):
            self.data_frame_logger.to_csv(
                self.file_path, mode='a', header=False
            )
        # Create file if it doesn't exist.
        else:
            self.data_frame_logger.to_csv(
                self.file_path, mode='a', header=True
            )

    def new_record(self, data: Tuple[int, dict]) -> pd.DataFrame:
        """
        This method creates a pandas dataframe. The pandas dataframe
        can be added as a record(s) to an existing dataframe.
        """
        if data and len(data) == 2:
            # Grabbing the column headings from the tuples
            # lists can be concatenated through the addition sign
            columns = ['ticks'] + list(data[1].keys())
            # Retrieving the column values from the data tuple
            all_data = [data[0]] + list(data[1].values())

        else:
            # Raise a value error if invalid data is passed into the function
            raise ValueError("Data is null or incorrect shape for logging.")

        # Using zip to create a new dictionary that form the row for the
        # data frame
        record = dict(zip(columns, all_data))
        # Uniquely identify all the records by creating a UUID column
        # Makes data matching more simple
        record_uuid = uuid.uuid4()

        # returning a pandas dataframe to be merged with other data frames
        data_frame = pd.DataFrame(record, index=[str(record_uuid)])

        return data_frame
