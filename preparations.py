import os
import subprocess
import sys
import configurations

def get_model(location='/proc/cpuinfo'):
    '''
    Purpose:
        Get the hardware model of the RPi
        Essentially this command
            cat /proc/cpuinfo | grep Model | cut -d: -f2
        along with some additional safety mechanisms.
    '''
    model = None
    model_info = ""
    step = 0
    test = None
    try:
       with open(location, 'r') as file:
           for line in file:
               # Strip leading and trailing whitespaces
               stripped_line = line.lower().strip()
               # Check if the stripped line starts with 'Model'
               if stripped_line.startswith('model'):
                   model_info = line.strip()
                   break  # Optional: break after finding the first match if only one is expected
    except Exception as e:
        print("\x1b[31m[!]\x1b[0m Model           : Unable to determine")
        print(" "*22+"'"+location+"'"+" not found")
        model = None
        return model
    for char in model_info:
        step += 1
        ascii_value = ord(char)  # Get ASCII value using ord()
#        print(f"'{char}' : {ascii_value}")
        if ascii_value == 58:
            test = step
            break

# Model string is not empty
    if step > 4 and step != len(model_info):
        model = model_info[test:].strip()
        print("\x1b[32m[+]\x1b[0m Model           : "+model)
    else: # Model string is missing or empty
        print("\x1b[31m[!]\x1b[0m Model           : Unable to determine")
        model = None
    return model


def check_date(test = 0):
    '''
    Purpose:
        See if the 'sudo date -s' command has ever been called.
        This is done by reviewing the .bash_history file
    Note:
        Need to check the history of both the current user and root.
    Assumption:
        If that command is found in the history, it has
        been used corrrectly and RECENTLY.
        At least to the point where the date is somewhat accurate.
    Return:
        0 for no issues
        >0 for issues
    '''
    if test < 0:
        print("\x1b[33m[?]\x1b[0m Date review     : Skipped for testing")
        return test
    outcome = 0
    result1 = 0
    result2 = 0
    name = os.getlogin()
    '''
    Always check root's history file
    '''
    HISTFILE1 = "/root/.bash_history"
    command1 = 'cat '+HISTFILE1+" | grep 'date -s'"
    result1 = command_length(command1)
    if result2 > 0:
        outcome += 2
    if name != 'root':
        '''
        Check users history file
        '''
        HISTFILE2 = "/home/"+ name + "/.bash_history"
        command2 = 'cat '+HISTFILE2+" | grep 'sudo date -s'"
        # Execute the command as a shell command
        result2 = command_length(command2)

    outcome = len(result1) + len(result2)

    if outcome > 0: 
        print("\x1b[32m[+]\x1b[0m Date review       : Seems updated")                                    
    else: # Model string is missing or empty
        print("\x1b[31m[!]\x1b[0m Date review       : Not updated")

    return outcome


def command_length(command=''):
    '''
    Purpose:
        This function call a shell in a subprocess
        and return the result as a string.
    Note:
        The subprocess method, means that
        environment variables are not transferred
        
    '''
    try:
        # Prepare the command to run in the shell
#        command = 'history | grep "sudo date -s"'
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        output = result.stdout
        return output
    except Exception as e:
        print(f"An error occurred: {e}")



def installed_prerequisites(location='requirements.txt'):
    '''
    Purpose:
        Review if the necessary files have been installed.
        Looks at a requirements.txt file, line by line for packages to review
        It works by reviewing the return code of a 'dpkg -s [PACKAGE]' command.
    Note:
        Due to calling shell commands, extra sanitation is required
    '''
    problems = []
    try:
        with open(location, 'r') as file:
            for line in file:
                result = -1
                package_name = line.strip()
                if len(package_name) == 0: # Ignoring empty lines
                    continue
                if package_name.find(' ') != -1: # Checking for multiple packages on the same line
                    print("\x1b[31m[!]\x1b[0m Requirements    : Incorrect format in requirements.txt")
                    print("                      Packages should be placed on separate lines.")
                    print("                      \x1b[41mTerminating the program\x1b[0m")
                    exit(1)
                if package_name.find(';') != -1 or package_name.find('/') != -1:
                    ''' Vulnerability prevention'''
                    print("\x1b[41mSeriously....\x1b[0m")
                    exit(2)
                try:
                    # Execute the rpm command and suppress error messages
                    result = subprocess.run(['dpkg', '-s', package_name], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception as e:
                    print("\x1b[31m[!]\x1b[0m \x1b[5;34;41mCritical Error\x1b[0m  : ", e)
                    print("                          Unable to verify if")
                    print("                          "+package_name)
                    print("                          is installed")
                    exit(1)
                if result.returncode != 0:
                    '''
                    Package not installed
                    '''
                    problems.append(package_name)
    except Exception as e:
        print("\x1b[31m[!]\x1b[0m Requirements    : '"+location+"' \x1b[5;34;41mFile not found\x1b[0m")
        print(" "*22+"Unable to determine whether the")
        print(" "*22+"required packages have been installed")
        print("                      \x1b[41mTerminating the program\x1b[0m")
        exit(1)

 
    if len(problems) == 0: 
        print("\x1b[32m[+]\x1b[0m Requirements    : Installed")                                    
    else: # Model string is missing or empty
        print("\x1b[31m[!]\x1b[0m Requirements    : Package(s) not installed")
        for package in problems:
            print("                    - "+ package)
    return problems


def get_wireless_interfaces(verbose = False):
    '''
    Purpose:
        Acquire the name of the Wireless Interface
        Usually "wlan0" on a Raspberry Pi but
        better be safe, in case 
    '''
    base_path = '/sys/class/net/'
    wireless_interfaces = []

    if not os.path.exists(base_path):
        print("\x1b[31m[!]\x1b[0m Error           : Unable to access '/sys/class/net/'.")
        print("                    - Please check your system configuration.")
        exit(1)
    # Check each interface in /sys/class/net to see if it's wireless
    for iface in os.listdir(base_path):
        # Construct the path to the possible wireless directory
        wireless_path = os.path.join(base_path, iface, 'wireless')
        
        # Check if the 'wireless' directory exists
        if os.path.exists(wireless_path):
            wireless_interfaces.append(iface)
    if len(wireless_interfaces) > 1:
        print("\x1b[31m[!]\x1b[0m \x1b[5;34;41mEdge case\x1b[0m     : Multiple Wireless Interfaces identified")
        for wlan in wireless_interfaces:
            print("                    -", wlan)
        print("    There should not exist multiple interfaces.")
        print("    Please check if there is an external wifi adapter")
        print("    If there is, remove it.")
        exit(1)
    elif len(wireless_interfaces) == 0:
        print("\x1b[31m[!]\x1b[0m \x1b[5;34;41mEdge case\x1b[0m       : No Wireless Interface located")
        exit(1)
    else:
        if verbose:
            print("\x1b[32m[+]\x1b[0m Interface       : "+wireless_interfaces[0])
        
    return wireless_interfaces[0]


def get_ethernet_interfaces(verbose = False):
    '''
    Purpose:
        Locate all ethernet interfaces
    Return:
        The name of an ethernate interface if found
        If none, or multipe are found, return an empty string
    '''
    base_path = '/sys/class/net/'
    ethernet_interfaces = []

    # Loop through all entries in /sys/class/net to find network interfaces
    for iface_name in os.listdir(base_path):
        iface_path = os.path.join(base_path, iface_name)

        # Check if the directory has the typical Ethernet interface files
        if os.path.exists(os.path.join(iface_path, 'device')) and not os.path.exists(os.path.join(iface_path, 'wireless')):
            # Read the 'type' to ensure it's Ethernet (type 1)
            try:
                with open(os.path.join(iface_path, 'type'), 'r') as f:
                    if f.read().strip() == '1':
                        ethernet_interfaces.append(iface_name)
                        if verbose:
                            print("\x1b[32m[+]\x1b[0m Interface       : "+iface_name)
            except IOError:
                continue  # If reading 'type' fails, skip this interface

    return ethernet_interfaces


def internet_status(interface, verbose = False):
    '''
    Purpose:
        Check if there is internet connection through
        a specific interface.
    '''
    url = "http://google.com"
    status = None
    try:
        # Using curl to make an HTTP GET request through a specific interface
        # The -k flag is to proceed even if the timing is off
        command = ['curl', '--interface', interface, '-k', '-s', '--connect-timeout', '5', url]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if verbose:
            print("\x1b[34m[?]\x1b[0m Checking access : "+ interface)
        if result.returncode == 0:
            if verbose:
                print(f"                      Successfully accessed {url} via {interface}.")
            status = True
        else:
            if verbose:
                print(f"                      Failed to access {url} via {interface}: {result.stderr}")
            status = False
    except Exception as e:
        print("\x1b[31m[!]\x1b[0m Checking access : "+ interface)
        print(" "*22+f"Error checking internet access: {e}")
        status = False


###################
## Isolation status of the machine.
# Isolation is forced by using iptables to block
# all traffic through the ethernet device


def isolation_status(files=[], verbose = False):
    '''
    Purpose:
        Check whether the files related to isolation exist
        - /var/spool/cron/crontabs/root
        - /root/isolation.sh
    Assumption:
        If the files exist, that the content is correct.
    '''
    # status = Boolean
    missing_files = []
    status, missing_files = configurations.isolation_status(files)
    print("\x1b[33m[?]\x1b[0m Persistence     : ", end='')
    if status:
        print("Files in place")
    else:
        print("Not prepared")

    # Cannot think of how to use the missing_files list.
    return status, missing_files
