import argparse
import os
import subprocess
import sys

# Additional files
import preparations
import user_info
#import user_decision
from logic import AP_Setup

'''
Hardware:
/etc/cpuinfo
cat /proc/cpuinfo | grep Model | cut -d: -f2
'''
parser = argparse.ArgumentParser(description='Simplified configuration tool.')
parser.add_argument('-q', action='store_true', help="Testing environment")
parser.add_argument('-n', type=str, default=None,
                    help='Name of the AP to be generated')
parser.add_argument('-v', action='store_true', help="Verbose mode")
parser.add_argument('-i', type=str, default=None,
                    help='Name of the .ini file to be used')



if __name__ == "__main__":
    args = parser.parse_args()    
    model = None
    fixed_date = None
    terminate = 0
    missing_packages = []
    internet_status = False
    isolation_files = ['/var/spool/cron/crontabs/root', '/root/isolation.sh']

    '''
    Default settings
    '''
    verbose = False
    ini_file = ''
    model_file = '/proc/cpuinfo'
    test_date = 0
    requirements_file = 'requirements.txt'
    persistence_achieved = False
    

    # Reviewing preparations to acquire the current
    # state of the machine (preparation.py file)
    if args.v:
        verbose = True
    if args.q:
        model_file = 'cpuinfo'
        test_date = -1
        requirements_file = 'requirements.txt'
    if args.i:
        ini_file = args.i

####################################
    print("\x1b[44mConfiguration tool\x1b[0m")
    print(25*"=")
    print("\x1b[34mSystem status\x1b[0m")

    '''
    Verifying the current status of the machine
    '''
    model = preparations.get_model(model_file) # default argument, "/proc/cpuinfo"
    fixed_date = preparations.check_date(test_date) # test < ? test : run normally
    missing_packages = preparations.installed_prerequisites(requirements_file)
    wifiname = preparations.get_wireless_interfaces(verbose)
    ethernetname = preparations.get_ethernet_interfaces(verbose)
    # Check if there is access to the internet through each separate interface
    internet_status = preparations.internet_status(wifiname, verbose)
    for interface in ethernetname:
        if preparations.internet_status(interface, verbose):
            if not internet_status:
                internet_status = True
    persistence_achieved, _  = preparations.isolation_status(isolation_files, verbose)

####################################
    print(25*"=")
    print("\x1b[34mUser feedback\x1b[0m")
    '''
    Acting on the acquired information to notify the user of relevant
    information to reprequisities for the project and how to solve it.
    '''
    user_info.review_model(model)
    user_info.review_date(fixed_date, verbose)
    user_info.review_isolation_status(persistence_achieved, isolation_files, verbose)
    terminate += user_info.review_requirements(missing_packages)
    
    if terminate > 0:
        print("Please resolve the prerequisites before running this tool")
        print("    \x1b[41mTerminating the program\x1b[0m\n")        
        exit(1)


####################################
    print("="*25)
    # Project ready for setting up an access point
    print("\x1b[34mAccess point configuration\x1b[0m")

    AP_logic = AP_Setup(
        verbose,             # Boolean
        internet_status,     # Boolean
        ethernetname,        # List of strings
        wifiname,            # String
        ini_file,            # String
        persistence_achieved # Boolean
    )

    AP_logic.logic_skeleton()
    
