'''
    The logic needed to setup the AP
'''

import configurations

class AP_Setup():
    def __init__(self,
        verbose,                # Boolean
        internet_status,        # Boolean
        ethernetname,           # List of strings
        wifiname,               # String
        ini_file,               # String
        persistence_achieved    # Boolean
    ):    
        self.verbose = verbose
        self.internet_status =  internet_status
        self.ethernetname = ethernetname
        self.wifiname =  wifiname
        self.ini_file =  ini_file

        self.ap_type = None

    def logic_skeleton(self):
        '''
        Purpose:
            Acts as a skeleton, for the logic
            tying it together, and deciding
            upon what to implement and how        
        '''

        changes_made = False


        '''
        An .ini file was supplied, so....
        let's see if it is working and can be used
        '''
        changes_made = self.ini_choice()
        if changes_made:
            changes_made = False
            print()

#        while True:
#            pass


    def ini_choice(self):
        '''
        Purpose:
            Review the .ini file status 
        Return:
            True if changes requiring the restart/setup
                 of hostapd/dnsmasq were made
            False if no changes where made
        '''
        # Create an boolean that is true, and run it through tests
        # if any test fail, set the variable to False
        ini_verified = True
        ini_type = None

        # See if an ini_file was supplied
        if self.ini_verified != None:
            print("\x1b[34m[?]\x1b[0m .ini file used  : "+ self.ini_file)
        else:
            ini_verified = False

        # See if file (supplied argument) exists
        if ini_verified:
            ini_verified = configurations.ini_exist(self.ini_file, self.verbose)
        if ini_verified:
            print(" "*22+"File exists")
        else:
            print(" "*22+"File does not exist")
            ini_verified = False
            
        # Read the content
        if ini_verified:
            settings = configurations.read_ini_config(self.ini_file, self.verbose)
            if settings == None:
                print(" "*20+"- 'Settings' section is \x1b[5;34;41mmissing\x1b[0m.")
                ini_verified = False

        # Evaluate the settings
        # Are the settings enough to create an AP?
        if ini_verified:
            ini_type = configurations.evaluate_ini_settings(settings, self.verbose)
            if ini_type == None:
                ini_verified = False

        # Populate the required settings
        if ini_verified:
            tmp = configurations.ini_populate(settings, ini_type, self.verbose)
            settings = tmp

        # Time to implement
            return self.use_ini_file(settings)
            
        else:
            # Something went wrong with the .ini file
            return False




    def use_ini_file(self, settings = {}, verbose = False):
        '''
        Purpose:
            By this point, everything related to the .ini
            file should have been verified.
            - All packages are installed
            - AP ready to be setup
            Time to implement it.
            There are separate aspects to implement
            unrelated to another
            - Reset AP settings
            - mac_address
            - dnsmasq.conf file for the dhcp server
            - hostapd.conf file for hostapd
        Note:
            Persistence will not be addressed here
        Return:
            True if the implementation succeed
            False if it did not
        '''
        
        # Updating mac_address
        # Easy to do
        if configurations.change_mac(self.wifiname, settings['mac_address']):
            # mac change was successfull
            pass
        else:
            # mac change was unsuccessfull
            pass
        
        # Look at settings related to the
        # dnsmasq.conf file (dhcp server) first.

        # check if file argument is supplied
        if self.ini_file_path == None:
            return None

        # File does not exist
        if not configurations.ini_exist(self.ini_file_path):
            print("\x1b[31m[!]\x1b[0m \x1b[5;34;41mEdge case\x1b[0m         : No Wireless Interface located")
            return None

        # Retrieve the settings, and store them in a dictionary
        config_settings = configurations.read_ini_config(self.ini_file_path, self.verbose)
        if not config_settings:
            print("\x1b[31m[!]\x1b[0m \x1b[5;34;41mEdge case\x1b[0m       : No Wireless Interface located")
            return None

        # Retrieve AP type
        self.ap_type = configurations.determine_ini_ap_type(config_settings, self.verbose)
        if self.ap_type == None:
            print("\x1b[31m[!]\x1b[0m \x1b[5;34;41mEdge case\x1b[0m       : No Wireless Interface located")
            return None

        # Populate the unused settings with default values
        tmp = configurations.ini_populate(config_settings, self.verbose)
        config_settings = tmp



