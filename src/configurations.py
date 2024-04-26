import subprocess
import configparser
import os
import re
import random
import ipaddress

'''
Helper functions needed by logic.py
######### 
+ is_valid_mac_address(mac)
- change_mac(interface, new_mac)
#########ini file
+ ini_exist(file_path="", verbose = False)
+ ini_default_settings(verbose = False)
+ read_ini_config(file_path, verbose)
+ determine_ini_ap_type(settings = {}, verbose = False)
+ ini_populate(settings = {}, ini_type = None, verbose = False)
#########Isolation
- create_isolation()
- remove_isolation()
######### Persistence
- persistence_status(files = [])
- persistence_create(wifiname = [], verbose = False)
+ persistence_remove()
######### Update AP
def update_ap()
'''


######### MAC addresse


def is_valid_mac_address(mac):
    '''
    Purpose:
        Check if the provided string is a valid MAC address
    Return:
        Boolean, whether true or false
    '''
    # Regular expression for validating a MAC address
    pattern = re.compile(r"""
    ^                           # start of string
    ([0-9A-Fa-f]{2}[:-]){5}     # five groups of two hex digits followed by a colon or hyphen
    [0-9A-Fa-f]{2}              # two hex digits
    $                           # end of string
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


######### .ini file


def ini_exist(file_path="", verbose = False):
    '''
    Simply check if the .ini file exists
    '''
    return os.path.exists(file_path)


def ini_default_settings(verbose = False):
    '''
    Purpose:
        Define some default settings
    Return:
        A dictionary with the default settings
    '''
    default_settings = {
        'ssid': None,                   # str
        'mac_address': None,            # str
        'encryption': None,             # str
        'password': None,               # str
        'range_from': "10.10.10.100",   # str
        'range_to': "10.10.10.255",     # str
        'channel': "1",                 # str
        'persistence': None             # str
    }

    ap_name_file = 'ap_names.txt'
    selected_line = None
    try:
        with open(ap_name_file, 'r') as file:
            for index, line in enumerate(file):
                # With a probability of 1/(index+1), replace the previous line with the current line
                if random.randint(0, index) == 0:
                    selected_line = line.strip()
                
            default_settings['ssid'] = selected_line
    except FileNotFoundError:
        default_settings['ssid'] = 'MyTeacherIsADummy'
        if verbose:
            print(f"Error: The file {ap_name_file} does not exist.")
    except Exception as e:
        default_settings['ssid'] = 'MyTeacherIsADummy'
        print(f"An error occurred reading file {ap_name_file}:\n{e}")
    return default_settings


def read_ini_config(file_path, verbose):
    '''
    Purpose:
       Read the settings from a .ini file.
       Initialize default values or None for each setting
    Return:

    '''
    settings = {
        'ssid': None,           # str
        'mac_address': None,    # str
        'encryption': None,     # str
        'password': None,       # str
        'range_from': None,     # str
        'range_to': None,       # str
        'channel': None,        # str
        'persistence': None     # 'yes'/'no'

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



def determine_ini_ap_type(settings = {}, verbose = False):
    '''
    Purpose:
        Review which type of AP is chosen
        and if the settings are sufficient to
        support an AP.
        Each type of AP have some required and
        optional settings based on the security.
    Return:
        The type of AP to be used
        Otherwise return None
    '''
    variable = settings.get('encryption', None)
    # Need to evaluate using the security aspect
    if variable == None:
        return None
    if variable.lower == "none":
        '''
        Required: 
            - encryption : none
        Optional:
            - ssid
            - mac_address
            - password
            - range_from
            - range_to
            - channel
        '''
        return 'none'
    elif variable.lower == "wpa2":
        '''
        Required: 
            - encryption : wpa2
            - password
        Optional:
            - ssid
            - mac_address
            - range_from
            - range_to
            - channel
        '''
        if settings.get('password', None) != None:
            return 'wpa2'
        elif verbose:
            print(" "*22+"WPA2 has been chosen in the .ini file,")
            print(" "*22+"but a password was not supplied.")
            print(" "*22+"Therefore the .ini file is \x1b[5;34;41mREJECTED\x1b[0m")
    return None


def ini_populate(settings = {}, ini_type = None, verbose = False):
    '''
    Purpose
        Insert default values, depending on
        the chosen AP type.
        While at it, verify the values as well.
    Details:
        Need to populate:
        ssid           : str (random from p_names.txt)
        range_from     : str 
        range_to       : str 
        channel        : str
    Optional:
        mac_address    : str
    Return:
        New settings dictionary
    '''
    default_settings = ini_default_settings(verbose)
    # Review ssid
    if settings['ssid'] == None:
        # Pick a random AP name
        settings['ssid'] = default_settings['ssid']
    # Review channel
    if settings['channel'] == None:
        settings['channel'] = '1'
    else:
        '''
        Verify if the supplied argument can be parsed as an integer
        and that the integer is valid
        '''
        try:
            channel = int(settings['channel'])
            available = list(range(1, 11))
            available.extend(range(34, 65, 4))
#            available.extend(range(100, 145, 4))
#            available.extend(range(149, 166, 4))
            if not channel in set:
                settings['channel'] = '1'
            else:
                # Channel set correctly, nothing to do
                # other than letting you (the reader) know
                pass
        except:
            '''
            Channel set incorrectly
            '''
            settings['channel'] = '1'

    # Review mac address
    if settings['mac_address'] != None:
        if not is_valid_mac_address(settings['mac_address']):
            settings['mac_address'] = None
            if verbose:
                print(" "*22+"The supplied mac address from the .ini file")
                print(" "*22+"is not valid, and therefore ignored")

    # Review ranges, to and from.
    acceptable_range = True
    if settings['range_from'] != None and settings['range_to'] != None:
        try:
            ip_from = ipaddress.IPv4Address(settings['range_from'])
            ip_to = ipaddress.IPv4Address(settings['range_to'])
            if ip_from.packed[:3] != ip_to.packed[:3]:
                acceptable_range = False
                # Not the same /24 subnet (i.e. the first 3 octets are different)
            else:
                if max(int(ip_from) - int(ip_to)+1) > 5:
                    # Sufficient range space, do nothing, other than notify
                    # you the reader
                    pass
                else:
                    acceptable_range = False
        except:
            acceptable_range = False
    else:
        acceptable_range = False
    if acceptable_range == False:
        settings['range_from'] = default_settings['range_from']
        settings['range_to'] = default_settings['range_to']
    
    return settings


######### Isolation

def create_isolation(ethernetnames = [], verbose = False):
    '''
    Purpose:
        Create isolation on the machine.
        Execute some commands
        - sudo airmon-ng check kill
        Then active a firewall by blocking all traffic
        on ALL ethernet devices
    '''

    return True


def remove_isolation(verbose = False):
    '''
    Purpose:
        Remove isolation
    '''


    pass

######### Persistence

def persistence_status(files = []):
    '''
    Purpose:
        Check whether the files related to isolation exist
        - /root/firewall.sh
        - /root/create_ap.sh
        - /etc/cron.d/ap_persistence
    Assumption:
        If the files exist, that the content is correct.
    Return:
        True if the files needed for isolation is in place
        else return False
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


def persistence_create(wifiname = [], verbose = False):
    '''
    Purpose:
        Creating persistence on the machine
        File(s) to create
        - /root/firewall.sh
        - /root/create_ap.sh
        - /etc/cron.d/ap_persistence
        Updating these are the responsibilites of other functions
        - hostapd.con
        - dnsmasq.conf

        Intent:
        - Firewall should block all traffic on ALL ethernet interfaces
        - reset_ap

        Afterwards the ap_settings should be reset.
        to ensure that the AP is created
    '''

    # Step 1, create files
    ## Step 1a /root/firewall.sh, if it exist delete it to create it anew
    ## Make sure to change file attributes as well, chmod 700 $file, + chattr +i $file
    filename = '/root/firewall.sh'
    if os.path.exists(filename):
        try:
            subprocess.run(['chattr', '-i', filename], check=True)
        except subprocess.CalledProcessError as e:
            if verbose:
                print(""*4+f"Failed to remove immutable flag from {filename}:\n    {str(e)}")
            return False

        os.remove(filename)  # Delete the file
        # Attempt to open the file to write
    try:
        #This will create the file
        with open(filename, 'w') as file:
            file.write("#!/bin/sh\n\n")
            file.write("# Flush all rules on all chains, essentially resetting the firewall\n")
            file.write("iptables -F\n\n")
            
            file.write("# Setting default policies to DROP\n\n")
            file.write(f"iptables -P INPUT DROP\n")
            file.write(f"iptables -P OUTPUT DROP\n")
            file.write(f"iptables -P FORWARD DROP\n\n")
            
            file.write(f"# Only allow traffic on {wifiname}\n")
            file.write(f"iptables -A INPUT -i {wifiname} -j ACCEPT\n")
            file.write(f"iptables -A OUTPUT -i {wifiname} -j ACCEPT\n")
            file.write(f"iptables -A FORWARD -i {wifiname} -j ACCEPT\n")
            file.write(f"iptables -A INPUT -o {wifiname} -j ACCEPT\n")
            file.write(f"iptables -A OUTPUT -o {wifiname} -j ACCEPT\n")
            file.write(f"iptables -A FORWARD -o {wifiname} -j ACCEPT\n")
            file.write("\n")
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}: {str(e)}")
        return False

    #step 1a Change file metadata (permissions and attributes)
    os.chmod(filename, 0o500)  # Make the script executable by the owner only
    try:
        subprocess.run(['chattr', '+i', filename], check=True)  # Make the file immutable
    except subprocess.CalledProcessError as e:
        if verbose:
            print(" "*4+f"Failed to set immutable flag on {filename}:\n    {str(e)}")
        return False


    # Step 1b, /root/reset_ap.sh
    ## If file exist, delete it
    filename = '/root/create_ap.sh'
    if os.path.exists(filename):
        try:
            subprocess.run(['chattr', '-i', filename], check=True)
        except subprocess.CalledProcessError as e:
            if verbose:
                print(""*4+f"Failed to remove immutable flag from {filename}:\n    {str(e)}")
            return False

        os.remove(filename)  # Delete the file
    # Attempt to open the file to write
    try:
        #This will create the file
        with open(filename, 'w') as file:
            file.write("sudo airmon-ng check kill\n")
            file.write("sudo systemctl unmask hostapd\n")
            file.write("sudo systemctl unmask dnsmasq\n")
            file.write("sudo systemctl restart hostapd\n")
            file.write("sudo systemctl restart dnsmasq\n")
################ IF MAC SETTING, REMEMBER TO UP INCLUDE IT HERE
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}:\n    {str(e)}")
        return False

    #step 1b Change file metadata (permissions and attributes)
    os.chmod(filename, 0o500)  # Make the script executable by the owner only
    try:
        subprocess.run(['chattr', '+i', filename], check=True)  # Make the file immutable
    except subprocess.CalledProcessError as e:
        if verbose:
            print(" "*4+f"Failed to set immutable flag on {filename}:\n    {str(e)}")
        return False

    # Step 1c, /etc/cron.d/ap_persistence
    ## If file exist, delete it
    filename = '/etc/cron.d/ap_persistence'
    if os.path.exists(filename):
        try:
            subprocess.run(['chattr', '-i', filename], check=True)
        except subprocess.CalledProcessError as e:
            if verbose:
                print(""*4+f"Failed to remove immutable flag from {filename}:\n    {str(e)}")
            return False

        os.remove(filename)  # Delete the file
    # Attempt to open the file to write
    try:
        #This will create the file
        with open(filename, 'w') as file:
            file.write("## Settings for persistence, may require a full PATH\n")
            file.write("## And SHELL, like this:\n")
            file.write("# SHELL=/bin/sh\n")
            file.write("## Grap your current PATH and insert it\n")
            file.write("# PATH=...\n\n")
            file.write("@reboot root /bin/sh /root/firewall.sh\n")
            file.write("@reboot root /bin/sh /root/reset_ap.sh\n")
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}: {str(e)}")
        return False

    #step 1c Change file metadata (permissions and attributes)
    os.chmod(filename, 0o500)  # Make the script executable by the owner only
    try:
        subprocess.run(['chattr', '+i', filename], check=True)  # Make the file immutable
    except subprocess.CalledProcessError as e:
        if verbose:
            print(" "*4+f"Failed to set immutable flag on {filename}:\n    {str(e)}")
        return False

    return True



def persistence_remove(verbose = False):
    '''
    Purpose:
        Deletes the files used to enforce persistence on reboot.
    Return:
        True if success
        False if failure
    '''

    persistence_files = ['/root/firewall.sh', '/root/create_ap.sh', '/etc/cron.d/ap_persistence']

    for filename in persistence_files:
        if os.path.exists(filename):
            try:
                subprocess.run(['chattr', '-i', filename], check=True)
            except subprocess.CalledProcessError as e:
                if verbose:
                    print(""*4+f"Failed to remove immutable flag from {filename}:\n    {str(e)}")
                return False
            os.remove(filename)  # Delete the file
        else:
            print(""*4+f"'{filename}' does not exist and can therefore not be removed")
    return True

######### 

def update_ap():
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
#    test = ["Configuration_files/default.ini", "Configuration_files/extended.ini", "Configuration_files/standard1.ini", "Configuration_files/standard2.ini", "Configuration_files/minimal1.ini"]
#    for file in test:
#        config_settings = read_ini_config(file, False)
#
#        print("\x1b[33m[!]\x1b[0m")
#        print(config_settings)
#        print("\x1b[31m[!]\x1b[0m")
#        print(config_settings)
    settings = ini_default_settings(True)
    print(settings)






############# supported .ini settings
# 'ssid'          : str 
# 'mac_address'   : str 
# 'encryption'    : str 'none'/'wpa2'
# 'password'      : str 
# 'range_from'    : str 
# 'range_to'      : str 
# 'channel'       : str 
# 'persistence'   : str 'yes'/'no'


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