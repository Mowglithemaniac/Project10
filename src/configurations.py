import subprocess
import configparser
import os
import re
import random
import ipaddress


'''
Helper functions needed by logic.py
######### File creation/deletion
- safe_lock(filename='', verbose=False)
- safe_delete(filename='', verbose=False)
######### 
+ is_valid_mac_address(mac, verbose=False)
- change_mac(interface='', new_mac='', verbose=False)
#########ini file
+ ini_exist(file_path="")
+ ini_default_settings(verbose = False)
+ read_ini_config(file_path='', verbose=False):
+ determine_ini_ap_type(settings = {}, verbose = False)
+ ini_populate(settings = {}, verbose = False)
#########Isolation
+ create_isolation(ip='', wifiname = '', verbose = False)
+ remove_isolation()
######### Persistence
- persistence_status(files = [])
- persistence_create(ip='',wifiname = [], verbose = False)
+ persistence_remove(verbose = False)
######### Update AP
- is_valid_ip_address(ip='')
- is_valid_range(range_from='', range_to='')
- retrieve_ip_from_conf(verbose = False)
- find_usable_ip(range_from ='', range_to='')
- update_dnsmasq(settings = {}, verbose=False)
- update_hostapd(settings = {}, ap_type='', verbose=False)
- update_ap(settings={}, wifiname='', verbose=False)
'''


######### File creation/deletio
def safe_lock(filename='', verbose=False):
    #step 1a Change file metadata (attributes)
    command = ['sudo', 'chattr', '+i', filename]
    try:
        # Make the file immutable
        result =subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  
        if verbose:
            if result.returncode == 0:
                print(" "*4+"\x1b[32m[+]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
            else:
                print(" "*4+"\x1b[31m[!]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
    except subprocess.CalledProcessError as e:
        if verbose:
            print(" "*4+f"\x1b[41m[!] Error executing command\033[0m:\n"+" "*4+f"\x1b[35m{' '.join(command)}\033[0m\n    Error: {str(e)}")
        return False
    return True


def safe_delete(filename='', verbose=''):
    if os.path.exists(filename):
        flags = ['-i', '-e']
        for flag in flags:
            command = ['sudo', 'chattr', flag, filename]
            try:
                subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if verbose:
                    print(" "*4+"\x1b[32m[+]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
            except subprocess.CalledProcessError as e:
                if verbose:
                    print(" "*4+"\x1b[31m[!]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
                return False

        os.remove(filename)  # Delete the file
        if os.path.exists(filename):
            print(" "*4+"\x1b[41mError\x1b[0m unable to delete '"+filename+"' before recreation")
        # Attempt to open the file to write
            return False
        if verbose:
            print(" "*4+"\x1b[34m[?]\x1b[0m Deleted file: \x1b[100m"+filename+"\x1b[0m")
    else:
        return True
    return True


######### MAC addresse

def is_valid_mac_address(mac, verbose = False):
    '''
    Purpose:
        Check if the provided string is a valid MAC address
        and ensure it is a globally unique unicast address (LSB = 0)
    Return:
        Boolean, whether true or false
    '''
    if mac is None:
        return False
    
    # Regular expression for validating a MAC address
    pattern = re.compile(r"""
    ^                           # start of string
    ([0-9A-Fa-f]{2}[:-]){5}     # five groups of two hex digits followed by a colon or hyphen
    [0-9A-Fa-f]{2}              # two hex digits
    $                           # end of string
    """, re.VERBOSE)
    
    if pattern.match(mac) is None:
        return False
    
    # Extract the first byte and convert it to an integer
    first_byte = int(mac.split(mac[2])[0], 16)
    
    # Check if the least significant bit is 1 of the first byte
    # Should be 0 for valid MAC address
    if first_byte & 0b00000001 == 1:
        if verbose:
            print(" "*4+"\x1b[5;34;41m[!]\x1b[0m Invalid MAC because LSB of 1st byte is set to 1")
        return False
    else:
        return True
    


def change_mac(interface='', new_mac='', verbose=False):
    '''
    Purpose:
        Changes the MAC address of a given network interface to a new MAC address.
    Args:
        interface (str): The name of the interface whose MAC should be changed.
        new_mac (str): The new MAC address to assign to the interface.
    Returns:
        bool: True if the MAC address was changed successfully, False otherwise.
    '''
    if new_mac == None:
        return False
    returncode = 0
    if not is_valid_mac_address(new_mac, verbose):
        return False

    commands = [
        ['sudo', 'ip', 'link', 'set', interface, 'down'],
        ['sudo', 'ip', 'link', 'set', interface, 'address', new_mac],
        ['sudo', 'ip', 'link', 'set', interface, 'up']
    ]
    count = 0
    for command in commands:
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                count += 1
            if verbose:
                if result.returncode == 0:
                    print(" "*4+"\x1b[32m[+]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
                else:
                    print(" "*4+"\x1b[31m[!]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
        except subprocess.CalledProcessError as e:
            if verbose:
                print(" "*4+f"\x1b[41m[!] Error executing command\033[0m:\n"+" "*4+f"\x1b[35m{' '.join(command)}\033[0m\n    Error: {str(e)}")
                count += 1
            return False
    if count > 0:
        print(" "*4+"\x1b[31m[!]\033[0m Failed to change MAC address")
        return False
    print(" "*4+f"\x1b[34m[?]\x1b[0m MAC address for {interface} changed to {new_mac}.")
    return True


######### .ini file


def ini_exist(file_path=""):
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


def read_ini_config(file_path='', verbose=False):
    '''
    Purpose:
       Read the settings from a .ini file.
       Initialize default values or None for each setting
    Return:
        A settings dictionary, or None
    '''
    settings = {
        'ssid': None,           # str 'none'/'wpa2'
        'mac_address': None,    # str
        'encryption': None,     # str
        'password': None,       # str
        'range_from': None,     # str
        'range_to': None,       # str
        'channel': None,        # str
        'persistence': None     # str 'yes'
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
            for key in settings.keys():
                if key in config['Settings']:
                    settings[key] = config['Settings'][key]
            print(" "*4+"Settings loaded :")
        # Individually check each setting
            max_key_length = max(len(key) for key in settings)

            # Print each key-value pair with aligned values
            for key, value in settings.items():
                if value == None:
                    continue
                print(" "*22+f"{key.ljust(max_key_length)} | '{value}'")
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
        print("Variable set to None")
        return None
    if variable.lower() == "none":
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
    elif variable.lower() == "wpa1":
        '''
        Required: 
            - encryption : wpa1
            - password
        '''
        if settings.get('password', None) != None:
            return 'wpa1'
        elif verbose:
            print(" "*22+"WPA1 has been chosen in the .ini file,")
            print(" "*22+"but a password was not supplied.")
            print(" "*22+"Therefore the .ini file is \x1b[5;34;41mREJECTED\x1b[0m")
    elif variable.lower() == "wpa2":
        '''
        Required: 
            - encryption : wpa2
            - password
        '''
        if settings.get('password', None) != None:
            return 'wpa2'
        elif verbose:
            print(" "*22+"WPA2 has been chosen in the .ini file,")
            print(" "*22+"but a password was not supplied.")
            print(" "*22+"Therefore the .ini file is \x1b[5;34;41mREJECTED\x1b[0m")
    return None


def ini_populate(settings = {}, verbose = False):
    '''
    Purpose
        Insert default values, depending on
        the chosen AP type.
        While at it, verify the values as well.
    Details:
        Need to populate:
        - ssid           : str (random from p_names.txt)
        - range_from     : str 
        - range_to       : str 
        - channel        : str
        Optional:
        - mac_address    : str
        - persistence    : str
    Return:
        New settings dictionary
    '''
    default_settings = ini_default_settings(verbose)
    # Review ssid
    if settings['ssid'] == None:
        # Pick a random AP name
        settings['ssid'] = default_settings['ssid']
    elif len(settings['ssid']) == 0:
        settings['ssid'] = default_settings['ssid']
    elif 32 < len(settings['ssid']):
        settings['ssid'] = default_settings['ssid']

    # Review mac address
    if settings['mac_address'] != None:
        if not is_valid_mac_address(settings['mac_address'], verbose):
            settings['mac_address'] = None
            if verbose:
                print(" "*22+"The supplied mac address from the .ini file")
                print(" "*22+"is not valid, and is therefore ignored")

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
            available = list(range(1, 12))
#            available.extend(range(34, 65, 4))
#            available.extend(range(100, 145, 4))
#            available.extend(range(149, 166, 4))
            if not channel in available:
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
    
    # Review ranges, to and from.
    if is_valid_range(settings['range_from'], settings['range_to']) == False:
        settings['range_from'] = default_settings['range_from']
        settings['range_to'] = default_settings['range_to']

    # Review persistence
    if settings['persistence'] != None:
        if settings['persistence'].lower() != "yes":
            settings['persistence'] = None

    return settings


######### Isolation

def create_isolation(ip='', wifiname = '', verbose = False):
    '''
    Purpose:
        Create isolation on the machine.
        Execute some commands
        - Activate a firewall by blocking all traffic
          on ALL ethernet devices, allowing only the wifi device
        - sudo airmon-ng check kill
    Note:
        It is assumed that hostapd.conf and dnsmasq.conf files
        are already in place.
        And that these commands will run flawlessly, as all prerequisites
        have been met.
    '''
    commands = [
        ["sudo", "iptables", "-F",],
        ["sudo", "iptables", "-P", "INPUT", "DROP"],
        ["sudo", "iptables", "-P", "OUTPUT", "DROP"],
        ["sudo", "iptables", "-P", "FORWARD", "DROP"],
        ["sudo", "iptables", "-A", "INPUT", "-i", wifiname, "-j", "ACCEPT"],
        ["sudo", "iptables", "-A", "FORWARD", "-i", wifiname, "-j", "ACCEPT"],
        ["sudo", "iptables", "-A", "OUTPUT", "-o", wifiname, "-j", "ACCEPT"],
        ["sudo", "iptables", "-A", "FORWARD", "-o", wifiname, "-j", "ACCEPT"],
        ["sudo", "airmon-ng", "check", "kill"],
        ["sudo", "ip", "link", "set", wifiname, "down"],
        ["sudo", "ip", "addr", "add", f"{ip}/24", "dev", wifiname],
        ["sudo", "ip", "link", "set", wifiname, "up"],
        ["sudo", "systemctl", "unmask", "hostapd"],
        ["sudo", "systemctl", "unmask", "dnsmasq"],
        ["sudo", "systemctl", "restart", "hostapd"],
        ["sudo", "systemctl", "restart", "dnsmasq"]
    ]

    for command in commands:
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if verbose:
                if result.returncode == 0:
                    print(" "*4+"\x1b[32m[+]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
                else:
                    print(" "*4+"\x1b[31m[!]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
        except subprocess.CalledProcessError as e:
            if verbose:
                print(" "*4+f"\x1b[41m[!] Error executing command\033[0m:\n"+" "*4+f"\x1b[35m{' '.join(command)}\033[0m\n    Error: {str(e)}")
            return False
    return True


def remove_isolation(verbose = False):
    '''
    Purpose:
        Remove isolation.
        iptables -F # Flush all rules
    '''
    commands = [
        ["sudo", "iptables", "-F"],
        ["sudo", "systemctl", "stop", "hostapd"],
        ["sudo", "systemctl", "stop", "dnsmasq"],
        ["sudo", "systemctl", "mask", "hostapd"],
        ["sudo", "systemctl", "mask", "dnsmasq"],
        ["sudo", "systemctl", "unmask", "wpa_supplicant"],
        ["sudo", "systemctl", "restart", "wpa_supplicant"],
        ["sudo", "systemctl", "restart", "NetworkManager"],
        ["sudo", "systemctl", "restart", "networking"]
    ]
    for command in commands:
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if verbose:
                if result.returncode == 0:
                    print(" "*4+"\x1b[32m[+]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
                else:
                    print(" "*4+"\x1b[31m[!]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
        except subprocess.CalledProcessError as e:
            if verbose:
                print(" "*4+f"\x1b[41m[!] Error executing command\033[0m:\n"+" "*4+f"\x1b[35m{' '.join(command)}\033[0m\n    Error: {str(e)}")

######### Persistence

def persistence_status():
    '''
    Purpose:
        Check whether the files related to isolation exist
        - /root/firewall.sh
        - /root/create_ap.sh
        - ~~/etc/cron.d/ap_persistence~~
        - /etc/systemd/system/ap_setup.service
    Assumption:
        If the files exist, that the content is correct.
    Return:
        True if the files needed for isolation is in place
        else return False
    '''
    files=[
        '/root/firewall.sh',
        '/root/create_ap.sh',
        '/etc/systemd/system/ap_setup.service'
    ]
    status = True

    for file in files:
        if not os.path.exists(file):
            status = False

    return status


def persistence_create(ip='',wifiname = [], mac_address='', verbose = False):
    '''
    Purpose:
        Creating persistence on the machine
        File(s) to create
        - /root/firewall.sh
        - /root/create_ap.sh
        - ~~/etc/cron.d/ap_persistence~~
        - /etc/systemd/system/ap_setup.service
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
    ## Make sure to change file attributes as well, chmod 500 $file, + chattr +i $file
    filename = '/root/firewall.sh'
    safe_delete(filename, verbose)
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
            file.write(f"iptables -A FORWARD -o {wifiname} -j ACCEPT\n\n")
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}: {str(e)}")
        return False
    if verbose:
        print(" "*4+"\x1b[34m[?]\x1b[0m Created file: \x1b[100m"+filename+"\x1b[0m")
    os.chmod(filename, 0o500)  # Make the script executable by the owner only
    safe_lock(filename, verbose)

    # Step 1b, /root/create_ap.sh
    ## If file exist, delete it
    filename = '/root/create_ap.sh'
    safe_delete(filename, verbose)
    # Attempt to open the file to write
    try:
        #This will create the file
        with open(filename, 'w') as file:
            file.write("sudo airmon-ng check kill\n")
            file.write("sudo ip link set "+wifiname+" down\n")
            file.write("sudo ip addr add "+f"{ip}/24 dev "+wifiname+"\n")
            file.write("sudo ip link set "+wifiname+" up\n")
            file.write("sudo systemctl unmask hostapd\n")
            file.write("sudo systemctl unmask dnsmasq\n")
            file.write("sudo systemctl mask wpa_supplicant\n")
            file.write("sudo systemctl restart hostapd\n")
            file.write("sudo systemctl restart dnsmasq\n")
            if is_valid_mac_address(mac_address, verbose):
                file.write("sudo ip link set "+wifiname+" down\n")
                file.write("sudo ip link set "+wifiname+" address "+ mac_address+"\n")
                file.write("sudo ip link set "+wifiname+" up\n")
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}:\n    {str(e)}")
        return False

    #step 1b Change file metadata (permissions and attributes)
    if verbose:
        print(" "*4+"\x1b[34m[?]\x1b[0m Created file: \x1b[100m"+filename+"\x1b[0m")
    os.chmod(filename, 0o500)  # Make the script executable by the owner only

    safe_lock(filename, verbose)

#    # Step 1c, /etc/cron.d/ap_persistence
#    ## If file exist, delete it
#    filename = '/etc/cron.d/ap_persistence'
#    safe_delete(filename, verbose)
#
#    # Using cron, attempt failed. File location: /etc/cron.d/ap_persistence
#    try:
#        #This will create the file
#        with open(filename, 'w') as file:
#            file.write("## Settings for persistence, may require a full PATH\n")
#            file.write("## And SHELL, like this:\n")
#            file.write("# SHELL=/bin/sh\n")
#            file.write("## Grap your current PATH and insert it\n")
#            file.write("# PATH=...\n\n")
##            PATH= os.environ.get('PATH') 
##            file.write("# PATH="+f"{PATH}\"\n\n")
#            file.write("@reboot root /bin/sh /root/firewall.sh\n")
#            file.write("@reboot root /bin/sh /root/reset_ap.sh\n")
#    except IOError as e:
#        if verbose:
#            print(f"    Failed to write to {filename}: {str(e)}")
#        return False

#    # Step 1c, 2nd attempt /etc/systemd/system/ap_setup.service
    ## If file exist, delete it
    filename = '/etc/systemd/system/ap_setup.service'

    safe_delete(filename, verbose)

    try:
        #This will create the daemon service file
        with open(filename, 'w') as file:
            file.write("[Unit]\n")
            file.write("Description=Setup AP at boot after network and hostapd are ready\n")
            file.write("After=network.target\n\n")
            file.write("\n")
            file.write("[Service]\n")
            file.write("Type=oneshot\n")
            file.write("ExecStart=/bin/bash -c '/root/create_ap.sh; /root/firewall.sh'\n")
            file.write("RemainAfterExit=No\n\n")
            file.write("[Install]\n")
            file.write("WantedBy=multi-user.target\n")

    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}: {str(e)}")
        return False

    #step 1c Change file metadata (permissions and attributes)
    if verbose:
        print(" "*4+"\x1b[34m[?]\x1b[0m Created file: \x1b[100m"+filename+"\x1b[0m")
    os.chmod(filename, 0o744)  # Make the script executable by the owner only

    if not safe_lock(filename, verbose):
        return False

    commands = [
        ["sudo", "systemctl", "daemon-reload"],
        ["sudo", "systemctl", "enable", "ap_setup.service"],
        ["sudo", "systemctl", "start", "ap_setup.service"]
    ]
    for command in commands:
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if verbose:
                if result.returncode == 0:
                    print(" "*4+"\x1b[32m[+]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
                else:
                    print(" "*4+"\x1b[31m[!]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
        except subprocess.CalledProcessError as e:
            if verbose:
                print(" "*4+f"\x1b[41m[!] Error executing command\033[0m:\n"+" "*4+f"\x1b[35m{' '.join(command)}\033[0m\n    Error: {str(e)}")
    return True

def persistence_remove(verbose = False):
    '''
    Purpose:
        Deletes the files used to enforce persistence on reboot.
    Return:
        True if success
        False if failure
    '''
    # Stop and disable the service, before removing the associated files
    commands = [
        ["sudo", "systemctl", "stop", "ap_setup.service"],
        ["sudo", "systemctl", "disable", "ap_setup.service"]
    ]      
    
    for command in commands:
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if verbose:
                if result.returncode == 0:
                    print(" "*4+"\x1b[32m[+]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
                else:
                    print(" "*4+"\x1b[31m[!]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
        except subprocess.CalledProcessError as e:
            if verbose:
                print(" "*4+f"\x1b[41m[!] Error executing command\033[0m:\n"+" "*4+f"\x1b[35m{' '.join(command)}\033[0m\n    Error: {str(e)}")

    # Delete associated files used in persistence
    persistence_files = ['/root/firewall.sh', '/root/create_ap.sh', '/etc/systemd/system/ap_setup.service']
    for filename in persistence_files:
        safe_delete(filename, verbose)

    #reload systemd
    commands = [
        ["sudo", "systemctl", "daemon-reload"],
        ["sudo", "systemctl", "reset-failed"]
    ]

    for command in commands:
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if verbose:
                if result.returncode == 0:
                    print(" "*4+"\x1b[32m[+]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
                else:
                    print(" "*4+"\x1b[31m[!]\033[0m "+f"\x1b[35m{' '.join(command)}\033[0m")
        except subprocess.CalledProcessError as e:
            if verbose:
                print(" "*4+f"\x1b[41m[!] Error executing command\033[0m:\n"+" "*4+f"\x1b[35m{' '.join(command)}\033[0m\n    Error: {str(e)}")
    return True
    ## WARNING, UNKNOWN IF IPTABLE RULES PERSIST AFTER REBOOT
    ## IF THAT IS THE CASE, A 'sudo iptables -F' COMMAND
    ## MAY BE REQUIRED AT STARTUP

######### 

def is_valid_ip_address(ip=''):
    '''
    Purpose:
        Check if the provided string is a valid IP address
    Return:
        Boolean, whether true or false
    '''
    # Regular expression for validating an IP address
    pattern = re.compile(r"""
    ^                           # start of string
    (                           # start of group
    [1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]  # matches 0-199, 100-199, 200-249, 250-255
    )                           # end of group
    \.                          # literal dot
    (                           # start of group
    [0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]  # matches 0-9, 10-99, 100-199, 200-249, 250-255
    )                           # end of group
    \.                          # literal dot
    (                           # start of group
    [0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]  # matches 0-9, 10-99, 100-199, 200-249, 250-255
    )                           # end of group
    \.                          # literal dot
    (                           # start of group
    [0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]  # matches 0-9, 10-99, 100-199, 200-249, 250-255
    )                           # end of group
    $                           # end of string
    """, re.VERBOSE)
    
    return pattern.match(ip) is not None


def is_valid_range(range_from='', range_to=''):
    '''
    Purpose
        Determine if an ip range is valid
    Return
        True if valid
        False if not valid
    '''
    acceptable_range = True
    if range_from != None and range_to != None:
        try:
            ip_from = ipaddress.IPv4Address(range_from)
            ip_to = ipaddress.IPv4Address(range_to)
            if ip_from.packed[:3] != ip_to.packed[:3]:
                acceptable_range = False
                # Not the same /24 subnet (i.e. the first 3 octets are different)
            else:
                if int(ip_to) - int(ip_from)+1 < 5:
                    # Insufficient range space 
                    acceptable_range = False
                else:
                    # Acceptable range
                    pass

        except Exception as e:
            acceptable_range = False

    else:
        acceptable_range = False
        print(acceptable_range)

    return acceptable_range


def retrieve_ip_from_conf(verbose = False):
    '''
    Purpose
        Read '/etc/dnsmasq.conf' and extract
        the range.
    '''
    filename = '/etc/dnsmasq.conf'
    if not os.path.exists(filename):
        # File does not exist
        return False
    range_from = None
    range_to = None

    try:
        with open(filename, "r") as file:
            for line in file:
                if line.startswith("dhcp-range"):
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        ip_range = parts[1].split(",")
                        if len(ip_range) == 3:
                            range_from = ip_range[0]
                            range_to = ip_range[1]
                            break  # Stop searching after finding the first dhcp-range
    except Exception as e:
        print(f"Error: {e}")
    if range_from != None and range_to != None:
        return find_usable_ip(range_from, range_to)
    return None


def find_usable_ip(range_from ='', range_to='', verbose=False):
    '''
    Purpose
        Find a usable IP which the interface
        can use, in order to setup the AP
        Requires a range_from, range_to
    '''
    # Convert start and end IP from string to IPv4Address objects
    start = ipaddress.IPv4Address(range_from)
    end = ipaddress.IPv4Address(range_to)
    
    # Calculate networks from the range and capture them in a list
    networks = list(ipaddress.summarize_address_range(start, end))
    
    if not networks:
        return None  # Return None if no network can be summarized

    # Use the first network (smallest subnet that fits the range)
    network = networks[0]
    
    # Get all usable hosts in this network
    usable_hosts = list(network.hosts())
    
    # Select a usable IP
    if usable_hosts:
        return str(usable_hosts[-1])  # You can choose another strategy for selecting the IP
    else:
        return None


def update_dnsmasq(settings = {}, wifiname='', verbose=False, filename='/etc/dnsmasq.conf'):
    '''
    Purpose
        Update the /etc/dnsmasq.conf file 
    '''
    if not safe_delete(filename, verbose):
        return False


    try:
        #This will create the file
        with open(filename, 'w') as file:
            file.write(f"interface={wifiname}\n")
            file.write("bind-dynamic\n")
            file.write("domain-needed\n")
            file.write("bogus-priv\n")
            file.write(f"dhcp-range={settings['range_from']},{settings['range_to']},12h\n")
            file.write("no-resolv\n")
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}:\n    {str(e)}")
        return False
    try:
        subprocess.run(['sudo', 'chattr', '+i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        if verbose:
            print(""*4+f"Failed to add immutable flag to {filename}:\n    {str(e)}")
    if verbose:
            print(" "*4+"\x1b[34m[?]\x1b[0m Created file: \x1b[100m"+filename+"\x1b[0m")
    safe_lock(filename, verbose)

    return True


def update_hostapd(settings = {}, wifiname = '', ap_type='', verbose=False, filename = '/etc/hostapd/hostapd.conf'):
    '''
    Purpose
        Update the /etc/hostapd/hostapd.conf file 
    '''
    if not safe_delete(filename, verbose):
        return False
    try:
        #This will create the file
        with open(filename, 'w') as file:
            if ap_type.lower() == 'none':
                file.write("driver=nl80211\n")
                file.write(f"channel={settings['channel']}\n")
                file.write(f"interface={wifiname}\n")
                file.write(f"ssid={settings['ssid']}\n")
            elif ap_type.lower() == 'wpa1':
                file.write(f"interface={wifiname}\n")
                file.write('driver=nl80211\n')
                file.write(f"ssid={settings['ssid']}\n")
                file.write('hw_mode=g\n')
                file.write(f"channel={settings['channel']}\n")
                file.write('wme_enabled=1\n')
                file.write('ieee80211n=1\n')
                file.write('macaddr_acl=0\n')
                file.write('auth_algs=1\n')
                file.write('ignore_broadcast_ssid=0\n')
                file.write('wpa=3\n')
                file.write(f"wpa_passphrase={settings['password']}\n")
                file.write('wpa_key_mgmt=WPA-PSK\n')
                file.write('wpa_pairwise=TKIP\n')
                file.write('rsn_pairwise=CCMP\n')
            elif ap_type.lower() == 'wpa2':
                file.write(f"interface={wifiname}\n")
                file.write('driver=nl80211\n')
                file.write(f"ssid={settings['ssid']}\n")
                file.write('hw_mode=g\n')
                file.write(f"channel={settings['channel']}\n")
                file.write('ieee80211n=1\n')
                file.write('ieee80211ac=1\n')
                file.write('wmm_enabled=1\n')
                file.write('auth_algs=1\n')
                file.write('wpa=2\n')
                file.write('wpa_key_mgmt=WPA-PSK\n')
                file.write('wpa_pairwise=CCMP\n')
                file.write(f"wpa_passphrase={settings['password']}\n")
            else:
                #This is where ap expansions would be
                print("Something went wrong\nIf the code ever executes this line, terminating program")
                exit(1)
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}:\n    {str(e)}")
        return False
    safe_lock(filename, verbose)
    if verbose:
        print(" "*4+"\x1b[34m[?]\x1b[0m Created file: \x1b[100m"+filename+"\x1b[0m")

    return True


def update_ap(settings={}, wifiname='', verbose=False):
    '''
    Purpose:
        A combination of all the necessary functions
        needed to update the Access Point.
        By this stage, it is assumed that the settings variable
        has been populated and can be used for this purpose.
        - write to dnsmasq
        - write to hostapd
        - Execute commands to activate the AP
    '''

    # Updating mac_address / Easy to do
    if change_mac(wifiname, settings['mac_address'], verbose):
        # mac change was successfull
        pass
    else:
        # mac change was unsuccessfull
        pass

    status = update_dnsmasq(settings, wifiname, verbose)
    if status == False: 
        return status
    # Note: The verification that the settings['encryption']
    # is valid, i.e. != None or 'none' or 'wpa1' has been clarified at this stage
    status = update_hostapd(settings, wifiname, settings['encryption'].lower(), verbose)
    if status == False: 
            return status
    ip = find_usable_ip(settings['range_from'], settings['range_to'])
    status = create_isolation(ip, wifiname, verbose)
    if status == False: 
            return status
    
    if settings['persistence'] == None:
        return status
    if settings['persistence'].lower() == 'yes':
        status = persistence_create(ip, wifiname, settings['mac_address'], verbose)
    if status == False:
        print(" "*4+"Creation of persistence failed")
    elif status == True:
        print(" "*4+"Successfully created files for persistence")
    return status


############# Isolation status of the machine.
# Isolation is forced by using iptables to block
# all traffic through the ethernet device
### Persistence of Isolation
# Created via crontab, with the @reboot tag
# File will be located at '/etc/cron.d/ap_persistence'
# and an iptables file called /root/firewall.sh
# to isolate the machine. 
# As well well as /root/create_ap.sh for AP initialization
# This can verified by using a cat, and then
# looking at the return code, to determine
# whether it exist or not.



#############

# Example usage
if __name__ == "__main__":
    pass


#    ip = find_usable_ip("10.10.10.100", "10.10.10.255")
#    print(ip)
#    print(retrieve_ip_from_conf(True))

############# supported .ini settings
# 'ssid'          : str 
# 'mac_address'   : str 
# 'encryption'    : str 'none'/'wpa1'
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

# wpa1
'''
# change wlan0 to your wireless device
interface=[WIFINAME]
driver=nl80211
ssid=[AP_NAME]
hw_mode=g
channel=[NUMBER]

wme_enabled=1
ieee80211n=1

macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=3                       # WPA and WPA2
wpa_passphrase=password
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
'''


# wpa2
'''
interface=[WIFINAME]           # Name of the WiFi interface we are configuring
driver=nl80211                 # Use the nl80211 driver with the modern Linux kernel
ssid=[AP_NAME]                 # Set your desired network name (SSID)
hw_mode=g                      # Set the hardware mode to 802.11g, you can also use a, b, or n
channel=[CHANNEL]              # Set the channel you want to use
ieee80211n=1                   # Enable 802.11n (HT)
ieee80211ac=1                  # Enable 802.11ac (VHT), if supported
wmm_enabled=1                  # Enable WMM for QoS

# Security configuration for WPA2 Personal
auth_algs=1                    # 1=wpa, 2=wep, 3=both
wpa=2                          # Use WPA2 only
wpa_key_mgmt=WPA-PSK           # Key management
wpa_pairwise=CCMP              # Use CCMP encryption (AES, for WPA2)
wpa_passphrase=YourPassphrase  # Set the WPA2 passphrase
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


                     