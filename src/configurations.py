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
- retrieve_ip_from_conf(verbose = False)
- find_usable_ip(range_from ='', range_to='')
- update_dnsmasq(settings = {}, verbose=False)
- update_hostapd(settings = {}, ap_type='', verbose=False)
- update_ap(settings={}, wifiname='', verbose=False)
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


def change_mac(interface='', new_mac=''):
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
    if not is_valid_mac_address(new_mac):
        return False
    try:
        # Bring down the network interface
        result = subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        returncode += result.returncode
        # Change the MAC address
        result = subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'address', new_mac], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        returncode += result.returncode

        # Bring up the network interface
        result = subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        returncode += result.returncode
    except Exception as e:
        print("")
        return False
    if result.returncode != 0:
        print("Failed to change MAC address. Error was:")
        print(result.stderr.decode())
        return False
    print(" "*4+f"MAC address for {interface} changed to {new_mac}.")
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
                print(" "*22+"is not valid, and is therefore ignored")

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


    if verbose:
        print(" "*4+"Executing commands: (RED - Fail, GREEN - Success)")
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
        ["sudo", "systemctl", "restart", "wpa_supplicant"],
        ["sudo", "systemctl", "restart", "NetworkManager"],
        ["sudo", "systemctl", "restart", "networking"]
    ]
    if verbose:
        print(" "*4+"Executing commands: (RED - Fail, GREEN - Success)")
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

    for file in files:
        if not os.path.exists(file):
            status = False

    return status


def persistence_create(ip='',wifiname = [], verbose = False):
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
            subprocess.run(['chattr', '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
        # Make the file immutable
        subprocess.run(['chattr', '+i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  
    except subprocess.CalledProcessError as e:
        if verbose:
            print(" "*4+f"Failed to set immutable flag on {filename}:\n    {str(e)}")
        return False


    # Step 1b, /root/reset_ap.sh
    ## If file exist, delete it
    filename = '/root/create_ap.sh'
    if os.path.exists(filename):
        try:
            subprocess.run(['chattr', '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
            file.write("sudo ip link set "+wifiname+"down\n")
            file.write("sudo ip addr add "+f"{ip}/24 dev "+wifiname+"\n")
            file.write("sudo ip link set "+wifiname+"up\n")
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
        subprocess.run(['chattr', '+i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  # Make the file immutable
    except subprocess.CalledProcessError as e:
        if verbose:
            print(" "*4+f"Failed to set immutable flag on {filename}:\n    {str(e)}")
        return False

    # Step 1c, /etc/cron.d/ap_persistence
    ## If file exist, delete it
    filename = '/etc/cron.d/ap_persistence'
    if os.path.exists(filename):
        try:
            subprocess.run(['chattr', '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
#            PATH= os.environ.get('PATH') 
#            file.write("# PATH="+f"{PATH}\"\n\n")
            file.write("@reboot root /bin/sh /root/firewall.sh\n")
            file.write("@reboot root /bin/sh /root/reset_ap.sh\n")
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}: {str(e)}")
        return False

    #step 1c Change file metadata (permissions and attributes)
    os.chmod(filename, 0o500)  # Make the script executable by the owner only
    try:
        # Make the file immutable
        subprocess.run(['chattr', '+i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
                subprocess.run(['chattr', '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except subprocess.CalledProcessError as e:
                if verbose:
                    print(""*4+f"Failed to remove immutable flag from {filename}:\n    {str(e)}")
                return False
            os.remove(filename)  # Delete the file
        else:
            if verbose:
                print(""*4+f"'{filename}' does not exist and can therefore not be removed")
    return True

######### 

def retrieve_ip_from_conf(verbose = False):
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
                            ip_from = ip_range[0]
                            ip_to = ip_range[1]
                            break  # Stop searching after finding the first dhcp-range
    except Exception as e:
        print(f"Error: {e}")
    if range_from != None and range_to != None:
        return find_usable_ip(range_from, range_to)
    return None


def find_usable_ip(range_from ='', range_to=''):
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


def update_dnsmasq(settings = {}, wifiname='', verbose=False):
    '''
    Purpose
        Update the /etc/dnsmasq.conf file 
    '''
    filename = '/etc/dnsmasq.conf'
    if os.path.exists(filename):
        try:
            subprocess.run(['sudo', 'chattr', '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            if verbose:
                print(""*4+f"Failed to remove immutable flag from {filename}:\n    {str(e)}")
            return False
        os.remove(filename)  # Delete the file

    try:
        #This will create the file
        with open(filename, 'w') as file:
            file.write(f"interface={wifiname}\n")
            file.write("bind-dynamic\n")
            file.write("domain-needed\n")
            file.write("bogus-priv\n")
            file.write(f"dhcp-range={settings['range_from']},{settings['range_to']},12h\n")
            file.write("no-resolv\n")
            try:
                subprocess.run(['sudo', 'chattr', '+i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except subprocess.CalledProcessError as e:
                if verbose:
                    print(""*4+f"Failed to add immutable flag to {filename}:\n    {str(e)}")
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}:\n    {str(e)}")
        return False
    return True

def update_hostapd(settings = {}, wifiname = '', ap_type='', verbose=False):
    '''
    Purpose
        Update the /etc/hostapd/hostapd.conf file 
    '''
    filename = '/etc/hostapd/hostapd.conf'
    if os.path.exists(filename):
        try:
            subprocess.run(['sudo', 'chattr', '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            if verbose:
                print(""*4+f"Failed to remove immutable flag from {filename}:\n    {str(e)}")
            return False
        os.remove(filename)  # Delete the file

    try:
        #This will create the file
        with open(filename, 'w') as file:
            if ap_type.lower() == 'none':
                file.write("driver=nl80211\n")
                file.write(f"channel={settings['channel']}\n")
                file.write(f"interface={wifiname}\n")
                file.write(f"ssid={settings['ssid']}\n")
            elif ap_type.lower() == 'wpa2':
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
                file.write('wpa_passphrase=password\n')
                file.write('wpa_key_mgmt=WPA-PSK\n')
                file.write('wpa_pairwise=TKIP\n')
                file.write('rsn_pairwise=CCMP\n')
            else:
                #This is where ap expansions would be
                print("Something went wrong\nIf the code ever executes this line, terminating program")
                exit(1)
            try:
                subprocess.run(['sudo', 'chattr', '+i', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except subprocess.CalledProcessError as e:
                if verbose:
                    print(""*4+f"Failed to add immutable flag to {filename}:\n    {str(e)}")
    except IOError as e:
        if verbose:
            print(f"    Failed to write to {filename}:\n    {str(e)}")
        return False
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
    if change_mac(wifiname, settings['mac_address']):
        # mac change was successfull
        pass
    else:
        # mac change was unsuccessfull
        pass

    status = update_dnsmasq(settings, wifiname, verbose)
    # Note: The verification that the settings['encryption']
    # is valid, i.e. != None or 'none' or 'wpa2' has been clarified at this stage
    update_hostapd(settings, wifiname, settings['encryption'].lower(), verbose)
    ip = find_usable_ip(settings['range_from'], settings['range_to'])
    create_isolation(ip, wifiname, verbose)


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


    ip = find_usable_ip("10.10.10.100", "10.10.10.255")
    print(ip)




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


                     