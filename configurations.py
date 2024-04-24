import subprocess
import configparser
import os
import re

'''
Helper functions needed by logic.py
'''

def is_valid_mac_address(mac):
    '''
    Purpose:
        Check if the provided string is a valid MAC address
    Return:
        Boolean, whether true or false
    '''
    # Regular expression for validating a MAC address
    pattern = re.compile(r"""
    ^                   # start of string
    ([0-9A-Fa-f]{2}[:-]){5}    # five groups of two hex digits followed by a colon or hyphen
    [0-9A-Fa-f]{2}      # two hex digits
    $                   # end of string
    """, re.VERBOSE)
    
    return pattern.match(mac) is not None    

def change_mac(interface, new_mac):
    '''
    Purpose:
        Changes the MAC address of a given network interface to a new MAC address.
    Args:
        interface (str): The name of the interface whose MAC should be changed.
        new_mac (str): The new MAC address to assign to the interface.
    Returns:
        bool: True if the MAC address was changed successfully, False otherwise.
    '''

    # Bring down the network interface
    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Change the MAC address
    result = subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'address', new_mac], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Bring up the network interface
    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        print(f"MAC address for {interface} changed to {new_mac}.")
        return True
    else:
        print("Failed to change MAC address. Error was:")
        print(result.stderr.decode())
        return False



def ini_exist(file_path="", verbose = False):
    '''
    Simply check if the .ini file exists
    '''
    return os.path.exists(file_path)


def read_ini_config(file_path, verbose):
    # Initialize default values or None for each setting
    '''
    Purpose:
       Read the settings from a .ini file.
    Return:

    '''
    settings = {
        'ssid': None,
        'mac_address': None,
        'encryption': None,
        'password': None,
        'range_from': "10.10.10.100",
        'range_to': "10.10.10.255",
        'channel': 1
    }
    
    config = configparser.ConfigParser()
    
    # Safely attempt to read the configuration file
    try:
        with open(file_path, 'r') as f:
            config.read_file(f)
    except configparser.Error as e:
        print(" "*22+f"Warning: Failed to read the config file: {str(e)}")
        return None 

    # Optional 'Settings' section
    if 'Settings' in config:
        if verbose:
            print(" "*4+"Settings loaded:")
        # Individually check each setting
        for key in settings.keys():
            if key in config['Settings']:
                settings[key] = config['Settings'][key]
                if verbose:
                    print(" "*20+"+ "+settings[key])
    else:
        settings = None
    return settings

def evaluate_ini_settings(settings = {}):
    # Need to evaluate using the security aspect

    if settings["security"].lower == "none":
        pass
    elif settings["security"].lower == "wpa2":
        pass
    else:
        pass


def isolation_status(files = []):
    '''
    Purpose:
        Check whether the files related to isolation exist
        - /var/spool/cron/crontabs/root
        - /root/isolation.sh
    Assumption:
        If the files exist, that the content is correct.
    '''
    status = True
    missing_files = []
    
    for file in files:
        try:
            command = ['sudo', 'cat', file]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                missing_files.append(file)
                status = False
        except Exception as e:
            print(" "*22+f"\x1b[5;34;41m[!]\x1b[0m Error accessing file")
            print(" "*22+file)
            print(f"    Error message   : {e}")
            exit(1)

    # Cannot think of how to use the missing_files list.
    return status, missing_files




def create_isolation():

    '''
    Purpose:
        Create isolation on the machine.
 
    '''

    pass

def remove_isolation():
    '''
    Purpose:
        Remove isolation
    '''
    pass




############# Isolation status of the machine.
# Isolation is forced by using iptables to block
# all traffic through the ethernet device
### Persistence of Isolation
# Created via crontab, with the @reboot tag
# File will be located at '/var/spool/cron/crontabs/root'
# and an iptables file called isolation.sh
# should be located at /root/isolation.sh
# This can verified by using a cat, and then
# looking at the return code, to determine
# whether it exist or not.



#############



# Example usage
if __name__ == "__main__":
    # mac_addresses = ["1A:2B:3C:4D:5E:6F", "1G:2H:3I:4J:5K:6L", "00:1A:2B:3C:4D:5E", "derp"]
    # for mac in mac_addresses:
    #    print(f"{mac}: {is_valid_mac_address(mac)}")
    test = ["Configuration_files/default.ini", "Configuration_files/extended.ini", "Configuration_files/standard1.ini", "Configuration_files/standard2.ini"]
    for file in test:
        config_settings = read_ini_config(file, False)

        print("\x1b[33m[!]\x1b[0m")
        print(config_settings)
        print("\x1b[31m[!]\x1b[0m")
#        print(config_settings)














############# hostapd conf file, 
# location /etc/hostapd/hostapd.conf
# Remember to change [WIFINAME] and [AP_NAME]
# No security AP

'''
driver=nl80211
channel=[NUMBER]
interface=[WIFINAME]
ssid=[AP_NAME]
'''

# wpa/wpa2
'''
# change wlan0 to your wireless device
interface=[WIFINAME]
driver=nl80211
ssid=[AP_NAME]
hw_mode=g
channel=[NUMBER]

wme_enabled=1
ieee80211n=1

# WPA and WPA2
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=3
wpa_passphrase=password
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
'''


############# dnsmasq conf file, for dhcp
# Remember to change [WIFINAME], [IP_FROM], [IP_TO]
'''
interface=[WIFINAME]
bind-dynamic
domain-needed
bogus-priv
dhcp-range=[IP_FROM],[IP_TO],12h
'''


