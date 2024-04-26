import subprocess

'''
Purpose:
    Provides relevant information for the user
    and explain how to resolve potential issues.
'''

def review_model(model=''):
    # It appears methods for changing the MAC is the same
    # for all models, although permanent change is different
    return 0


def review_date(date=-1, verbose = False):
    '''
    Purpose:
        Provide information to the user about
        whether or not the time is assumed correct
        and how to fix it, if it is not.
    '''
    if verbose:
        print("\x1b[34m[?]\x1b[0m Date review     : ", end='')
    if date < 0 and date > -10:
        '''
        Testing assumed
        date correct
        '''
        if verbose:
            print("Test called for reviewing correct date")
            print("                      ", end='')         
        date = 0
    elif date <= -10:
        '''
        Testing assumed
        date incorrect
        '''
        if verbose:
            print("Test called for reviewing incorrect date")
            print("                      ", end='')         
        date = 1

    if date == 0:
        if verbose:
            print("No issues discovered")
        return
    else:
        print("    The date needs to be set in order to install")
        print("    the necessary packages.")
        print("    From the shell, use this command")
        print('       \x1b[35msudo date -s "YYYY-MM-DD HH:MM:SS"\x1b[0m')
        print("    This includes apostrophes, and remember to")
        print("    substitue the correct: Year, Month, Date,\n"
              "    and Hours, Minutes, Seconds.")
        print("    Preferably you should not use the root user\n"
              "    to execute commands.")
    return 1

def review_requirements(packages=[]):
    print("\x1b[34m[?]\x1b[0m Missing packages: " + str(len(packages)))
    if len(packages) > 0:
        print("    There are some missing packages needed to run this program")
        print("    To install packages, ensure that the time is correctly set")
        print("    From the shell, use this command:")
        print('       \x1b[35msudo date -s "YYYY-MM-DD HH:MM:SS"\x1b[0m')
        print("    Ensure that the package repository is updated")
        print('       \x1b[35msudo apt update\x1b[0m')
        print("    Finally install the packages:")
        print('       \x1b[35mcat requirements.txt | xargs sudo apt install -y\x1b[0m')
        print("    Or alternatively, one by one, for more granular control:")
        print('       \x1b[35msudo apt install -y [PACKAGE_NAME]\x1b[0m')
        return 1
    
    return 0


def project_status(
        packages=[]
    ):
    '''
    Purpose:
        Some logic to determine if system has been
        configured to set up an access point.
    Argument:
        If packages are not installed, it is impossible
        that the AP can be setup.
        If packages are up, review the status of daemons
        using systemctl
    Return:


    '''
    pass


def get_service_status(service_names):
    statuses = {}
    
    for service in service_names:
        # Query detailed properties of the service
        result = subprocess.run(['systemctl', 'show', service, '--property=LoadState,ActiveState,UnitFileState'], capture_output=True, text=True)
        
        if result.returncode == 0:
            properties = {line.split('=')[0]: line.split('=')[1] for line in result.stdout.strip().split('\n')}
            
            if properties['LoadState'] == 'loaded' and properties['ActiveState'] == 'active':
                statuses[service] = 'Active'
            elif properties['LoadState'] == 'not-found':
                statuses[service] = 'Not Found'
            elif properties['UnitFileState'] == 'masked':
                statuses[service] = 'Masked'
            elif properties['ActiveState'] == 'inactive':
                statuses[service] = 'Inactive'
            else:
                statuses[service] = properties['ActiveState']  # Other states like failed, deactivating, etc.
        else:
            statuses[service] = 'Error retrieving status'

    return statuses

def review_isolation_status(persistence_achieved = None, files =[], verbose = False):
    if persistence_achieved == None:
        print("Programming error\nIncorrect usage of user_info.review_isolation_status\n")
        return
    if verbose:
        print("\x1b[34m[?]\x1b[0m Persistence     : ", end='')
        if persistence_achieved:
            print("Files are located at:")
        else:
            print("If persistence is desired, these files will be created")
        for file in files:
            print(" "*20+"- '"+file+"'")



if __name__ == "__main__":
    # Example usage: Checking the status of various system daemons
    services_to_check = ['hostapd', 'NetworkManager', 'NetworkManager.service', 'apache2.service', 'mysql.service', 'stuff.service', 'wpa_supplicant']
    service_statuses = get_service_status(services_to_check)
    for service, status in service_statuses.items():
        print(f"{service}: {status}")
    print(service_statuses)