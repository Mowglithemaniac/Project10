import unittest
import tempfile
import os
import src.configurations as config
from unittest.mock import patch, mock_open


class TestVerification(unittest.TestCase):

# BEGIN MAC
    def test_mac_good_one(self):
        result = config.is_valid_mac_address("1A:2B:3C:4D:5E:6F")
        self.assertTrue(result)

    def test_mac_good_two(self):
        result = config.is_valid_mac_address("00:00:00:00:00:00")
        self.assertTrue(result)

    def test_mac_bad_one(self):
        result = config.is_valid_mac_address("00:00:00:00:00:GK")
        self.assertFalse(result)

    def test_mac_bad_two(self):
        result = config.is_valid_mac_address("foobarfoobar")
        self.assertFalse(result)

    def test_mac_bad_three(self):
        result = config.is_valid_mac_address(None)
        self.assertFalse(result)

    def test_mac_bad_four(self):
        result = config.is_valid_mac_address("")
        self.assertFalse(result)
# END MAC

# BEGIN IP
    def test_ip_good_one(self):
        result = "0.0.0.0"
        self.assertTrue(result)


    def test_ip_good_two(self):
        result = config.is_valid_ip_address("255.255.255.255")
        self.assertTrue(result)


    def test_ip_good_one(self):
        result = config.is_valid_ip_address("10.10.10.10")
        self.assertTrue(result)


    def test_ip_bd_one(self):
        result = config.is_valid_ip_address("")
        self.assertFalse(result)


    def test_ip_bad_two(self):
        result = config.is_valid_ip_address("foobar")
        self.assertFalse(result)

    def test_ip_bad_three(self):
        result = config.is_valid_ip_address("555.123.123.123")
        self.assertFalse(result)
# END IP

# BEGIN RANGE
    def test_range_good_(self):
        result = config.is_valid_range("0.0.0.0", "0.0.0.255")
        self.assertTrue(result)

    def test_range_good_(self):
        result = config.is_valid_range("10.10.10.100", "10.10.10.155")
        self.assertTrue(result)


    def test_range_bad_(self):
        result = config.is_valid_range("", "10.10.10.10")
        self.assertFalse(result)
        
    
    def test_range_bad_one(self):
        result = config.is_valid_range("10.10.10.10", "")
        self.assertFalse(result)


    def test_range_bad_two(self):
        result = config.is_valid_range("foobar", "10.10.10.10")
        self.assertFalse(result)


    def test_range_bad_three(self):
        result = config.is_valid_range("10.10.10.10", "foobar")
        self.assertFalse(result)


    def test_range_bad_four(self):
        result = config.is_valid_range("10.10.10.200", "10.10.10.10")
        self.assertFalse(result)


    def test_range_bad_five(self):
        result = config.is_valid_range("10.10.10.10", "110.10.10.10")
        self.assertFalse(result)


    def test_range_bad_six(self):
        result = config.is_valid_range("110.10.10.10", "10.10.10.10")
        self.assertFalse(result)
# END RANGE

# BEGIN default
    # BEGIN key exist
    def test_default_exist_one(self):
        '''
        Check if ssid exist
        '''
        result = config.ini_default_settings()
        self.assertIn('ssid', result)

   
    def test_default_exist_two(self):
        '''
        Check if mac_address exist
        '''
        result = config.ini_default_settings()
        self.assertIn('mac_address', result)

   
    def test_default_exist_three(self):
        '''
        Check if encryption exist
        '''
        result = config.ini_default_settings()
        self.assertIn('encryption', result)


    def test_default_exist_four(self):
        '''
        Check if password exist
        '''
        result = config.ini_default_settings()
        self.assertIn('password', result)

   
    def test_default_exist_five(self):
        '''
        Check if range_from exist
        '''
        result = config.ini_default_settings()
        self.assertIn('range_from', result)


    def test_default_exist_six(self):
        '''
        Check if range_to exist
        '''
        result = config.ini_default_settings()
        self.assertIn('range_to', result)

   
    def test_default_exist_seven(self):
        '''
        Check if channel exist
        '''
        result = config.ini_default_settings()
        self.assertIn('channel', result)

    def test_default_exist_seven(self):
        '''
        Check if channel exist
        '''
        result = config.ini_default_settings()
        self.assertIn('persistence', result)
    # END key exist
    ##############################################
    # BEGIN key content
    def test_default_content_one(self):
        '''
        Check the content of ssid
        '''
        result = config.ini_default_settings()
        self.assertIsNotNone(result['ssid'])

   
    def test_default_content_two(self):
        '''
        Check that the length of the ssid is greater than 0
        '''
        result = config.ini_default_settings()
        self.assertTrue(0 < len(result['ssid']))

   
    def test_default_content_three(self):
        '''
        Check that the length of the ssid is less than 33
        '''
        result = config.ini_default_settings()
        self.assertTrue(len(result['ssid']) < 33)


    def test_default_content_four(self):
        '''
        Check content of mac_address
        '''
        result = config.ini_default_settings()
        self.assertIsNone(result['mac_address'])


    def test_default_content_five(self):
        '''
        Check content of mac_address
        '''
        result = config.ini_default_settings()
        self.assertIsNone(result['mac_address'])


    def test_default_content_six(self):
        '''
        Check content of encryption
        '''
        result = config.ini_default_settings()
        self.assertIsNone(result['encryption'])

   
    def test_default_content_seven(self):
        '''
        Check content of password
        '''
        result = config.ini_default_settings()
        self.assertIsNone(result['password'])


    def test_default_content_eight(self):
        '''
        Check content of range_from
        '''
        result = config.ini_default_settings()
        self.assertEqual("10.10.10.100", result['range_from'])


    def test_default_content_nine(self):
        '''
        Check content of channel
        '''
        result = config.ini_default_settings()
        self.assertEqual("1", result['channel'])


    def test_default_content_ten(self):
        '''
        Check content of persistence
        '''
        result = config.ini_default_settings()
        self.assertIsNone(result['persistence'])
    # END key content
# END default
    def test_populate_content_one(self):
        '''
        Check if content of ssid is string
        '''
        result = config.ini_default_settings()
        self.assertIsInstance(result['ssid'], str)


    def test_populate_content_two(self):
        '''
        Check that the length of the ssid is less than 33
        '''
        result = config.ini_default_settings()
        self.assertTrue(len(result['ssid']) < 33)


    def test_populate_content_three(self):
        '''
        Check that the length of the ssid is greater than 0
        '''
        result = config.ini_default_settings()
        self.assertTrue(0 < len(result['ssid']))


    def test_populate_content_four(self):
        '''
        Check the mac_address
        '''
        result = config.ini_default_settings()
        self.assertTrue(0 < len(result['ssid']))


# BEGIN populate
class TestIniPopulate(unittest.TestCase):

    def setUp(self):
        """Set up default settings for each test."""
        self.default_settings = {
            'ssid': 'DefaultSSID',
            'mac_address': None,
            'encryption': None,
            'password': None,
            'range_from': '10.10.10.100',
            'range_to': '10.10.10.255',
            'channel': '1',
            'persistence': None
        }

    def test_ssid_none(self):
        """Test when ssid is None."""
        settings = self.default_settings.copy()
        settings['ssid'] = None
        result = config.ini_populate(settings)
        self.assertIsNotNone(result['ssid'])
        self.assertGreaterEqual(len(result['ssid']), 1)
        self.assertLessEqual(len(result['ssid']), 32)

    def test_ssid_empty(self):
        """Test when ssid is an empty string."""
        settings = self.default_settings.copy()
        settings['ssid'] = ''
        result = config.ini_populate(settings)
        self.assertIsNotNone(result['ssid'])
        self.assertGreaterEqual(len(result['ssid']), 1)
        self.assertLessEqual(len(result['ssid']), 32)


    def test_ssid_too_long(self):
        """Test when ssid is longer than 32 characters."""
        settings = self.default_settings.copy()
        settings['ssid'] = 'A' * 33
        result = config.ini_populate(settings)
        self.assertIsNotNone(result['ssid'])
        self.assertGreaterEqual(len(result['ssid']), 1)
        self.assertLessEqual(len(result['ssid']), 32)

    def test_mac_address_none(self):
        """Test when mac_address is None."""
        settings = self.default_settings.copy()
        settings['mac_address'] = None
        result = config.ini_populate(settings)
        self.assertIsNone(result['mac_address'])

    def test_channel_none(self):
        """Test when channel is None."""
        settings = self.default_settings.copy()
        settings['channel'] = None
        result = config.ini_populate(settings)
        self.assertEqual(result['channel'], '1')

    def test_channel_invalid(self):
        """Test when channel is invalid."""
        settings = self.default_settings.copy()
        settings['channel'] = 'invalid_channel'
        result = config.ini_populate(settings)
        self.assertEqual(result['channel'], '1')

    def test_channel_valid(self):
        """Test when channel is valid."""
        settings = self.default_settings.copy()
        settings['channel'] = '6'
        result = config.ini_populate(settings)
        self.assertEqual(result['channel'], '6')

    def test_range_invalid(self):
        """Test when range_from and range_to are invalid."""
        settings = self.default_settings.copy()
        settings['range_from'] = '10.10.10.300'
        settings['range_to'] = '10.10.10.400'
        result = config.ini_populate(settings)
        self.assertEqual(result['range_from'], '10.10.10.100')
        self.assertEqual(result['range_to'], '10.10.10.255')

    def test_range_valid(self):
        """Test when range_from and range_to are valid."""
        settings = self.default_settings.copy()
        settings['range_from'] = '10.10.10.110'
        settings['range_to'] = '10.10.10.150'
        result = config.ini_populate(settings)
        self.assertEqual(result['range_from'], '10.10.10.110')
        self.assertEqual(result['range_to'], '10.10.10.150')

    def test_persistence_yes(self):
        """Test when persistence is 'yes'."""
        settings = self.default_settings.copy()
        settings['persistence'] = 'yes'
        result = config.ini_populate(settings)
        self.assertEqual(result['persistence'], 'yes')

    def test_persistence_no(self):
        """Test when persistence is 'no'."""
        settings = self.default_settings.copy()
        settings['persistence'] = 'no'
        result = config.ini_populate(settings)
        self.assertIsNone(result['persistence'])



# END populate




class TestUpdateHostapd(unittest.TestCase):


    def setUp(self):
        """Set up the environment for each test."""
        self.default_settings = {
            'ssid': 'TestSSID',
            'channel': '6',
            'password': 'TestPassphrase'
        }
        self.wifiname = 'wlan0'
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_filename = self.temp_file.name

    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)

    @patch('src.configurations.safe_delete', return_value=True)
    @patch('src.configurations.safe_lock')
    def test_update_hostapd_none(self, mock_safe_lock, mock_safe_delete):
        """Test update_hostapd with no encryption (ap_type='none')."""
        result = config.update_hostapd(self.default_settings, self.wifiname, 'none', verbose=True, filename=self.temp_filename)

        # Check if the function returned True
        self.assertTrue(result)

        # Read the content from the temporary file
        with open(self.temp_filename, 'r') as file:
            written_content = file.read()

        # Define the expected content
        expected_content = (
            'driver=nl80211\n'
            f'channel={self.default_settings["channel"]}\n'
            f'interface={self.wifiname}\n'
            f'ssid={self.default_settings["ssid"]}\n'
        )

        # Assert that the written content matches the expected content
        self.assertEqual(written_content, expected_content)

    @patch('src.configurations.safe_delete', return_value=True)
    @patch('src.configurations.safe_lock')
    def test_update_hostapd_wpa1(self, mock_safe_lock, mock_safe_delete):
        """Test update_hostapd with WPA1 encryption (ap_type='wpa1')."""
        result = config.update_hostapd(self.default_settings, self.wifiname, 'wpa1', verbose=True, filename=self.temp_filename)

        # Check if the function returned True
        self.assertTrue(result)

        # Read the content from the temporary file
        with open(self.temp_filename, 'r') as file:
            written_content = file.read()

        # Define the expected content
        expected_content = (
            f'interface={self.wifiname}\n'
            'driver=nl80211\n'
            f'ssid={self.default_settings["ssid"]}\n'
            'hw_mode=g\n'
            f'channel={self.default_settings["channel"]}\n'
            'wme_enabled=1\n'
            'ieee80211n=1\n'
            'macaddr_acl=0\n'
            'auth_algs=1\n'
            'ignore_broadcast_ssid=0\n'
            'wpa=3\n'
            f'wpa_passphrase={self.default_settings["password"]}\n'
            'wpa_key_mgmt=WPA-PSK\n'
            'wpa_pairwise=TKIP\n'
            'rsn_pairwise=CCMP\n'
        )

        # Assert that the written content matches the expected content
        self.assertEqual(written_content, expected_content)

    @patch('src.configurations.safe_delete', return_value=True)
    @patch('src.configurations.safe_lock')
    def test_update_hostapd_wpa2(self, mock_safe_lock, mock_safe_delete):
        """Test update_hostapd with WPA2 encryption (ap_type='wpa2')."""
        result = config.update_hostapd(self.default_settings, self.wifiname, 'wpa2', verbose=True, filename=self.temp_filename)

        # Check if the function returned True
        self.assertTrue(result)

        # Read the content from the temporary file
        with open(self.temp_filename, 'r') as file:
            written_content = file.read()

        # Define the expected content
        expected_content = (
            f'interface={self.wifiname}\n'
            'driver=nl80211\n'
            f'ssid={self.default_settings["ssid"]}\n'
            'hw_mode=g\n'
            f'channel={self.default_settings["channel"]}\n'
            'ieee80211n=1\n'
            'ieee80211ac=1\n'
            'wmm_enabled=1\n'
            'auth_algs=1\n'
            'wpa=2\n'
            'wpa_key_mgmt=WPA-PSK\n'
            'wpa_pairwise=CCMP\n'
            f'wpa_passphrase={self.default_settings["password"]}\n'
        )

        # Assert that the written content matches the expected content
        self.assertEqual(written_content, expected_content)





class TestUpdateDnsmasq(unittest.TestCase):

    def setUp(self):
        """Set up the environment for each test."""
        self.default_settings = {
            'ssid': 'TestSSID',
            'range_from': '10.10.10.100',
            'range_to': '10.10.10.200'
        }
        self.wifiname = 'wlan0'
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_filename = self.temp_file.name

    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)


    @patch('src.configurations.safe_delete', return_value=True)
    @patch('src.configurations.safe_lock')
    @patch('subprocess.run')
    def test_update_dnsmasq(self, mock_subprocess_run, mock_safe_lock, mock_safe_delete):
        """Test update_dnsmasq function."""
        result = config.update_dnsmasq(self.default_settings, self.wifiname, verbose=True, filename=self.temp_filename)

        # Check if the function returned True
        self.assertTrue(result)

        # Read the content from the temporary file
        with open(self.temp_filename, 'r') as file:
            written_content = file.read()

        # Define the expected content
        expected_content = (
            f"interface={self.wifiname}\n"
            "bind-dynamic\n"
            "domain-needed\n"
            "bogus-priv\n"
            f"dhcp-range={self.default_settings['range_from']},{self.default_settings['range_to']},12h\n"
            "no-resolv\n"
        )

        # Assert that the written content matches the expected content
        self.assertEqual(written_content, expected_content)





if __name__ == '__main__':
    unittest.main(verbosity=2)