import unittest
from app.tracker.convert_date import *

class TestEpochToUtc(unittest.TestCase):

    def test_epoch_to_utc_happy_path_1(self):
        """
        Test to see if epoch successfully converts to the correct date, 2023-11-21 16:40:01 cst
        """
        #Arrange actual date in epoch
        sec = 1700606401
        nanos = 199675000

        # Call the action in testing
        datetime_obj_utc = epoch_to_UTC(sec, nanos)

        # Convert UTC datetime to Chicago time
        datetime_obj_chicago = UTC_to_Timezone(datetime_obj_utc, 'America/Chicago')
        date_str = datetime_obj_chicago.strftime('%Y-%m-%d %H:%M:%S')

        self.assertEqual(date_str, "2023-11-21 16:40:01")

    def test_epoch_to_utc_happy_path_2(self):
        """
        Test to see if epoch successfully converts to the correct date, 2023-06-16 12:04:41 cst
        """
        #Arrange actual date in epoch
        sec = 1686935081
        nanos = 628439000

        # Call the action in testing
        datetime_obj_utc = epoch_to_UTC(sec, nanos)

        # Convert UTC datetime to Chicago time
        datetime_obj_chicago = UTC_to_Timezone(datetime_obj_utc, 'America/Chicago')
        date_str = datetime_obj_chicago.strftime('%Y-%m-%d %H:%M:%S')

        self.assertEqual(date_str, "2023-06-16 12:04:41")

    def test_epoch_to_utc_happy_path_3(self):
        """
        Test to see if epoch successfully converts to the correct date, 2023-07-13 14:19:21 cst
        """
        #Arrange actual date in epoch
        sec = 1689275961
        nanos = 482305000

        # Call the action in testing
        datetime_obj_utc = epoch_to_UTC(sec, nanos)

        # Convert UTC datetime to Chicago time
        datetime_obj_chicago = UTC_to_Timezone(datetime_obj_utc, 'America/Chicago')
        date_str = datetime_obj_chicago.strftime('%Y-%m-%d %H:%M:%S')

        self.assertEqual(date_str, "2023-07-13 14:19:21")