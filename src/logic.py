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
        persistence_achieved,   # Boolean
        test,                   # Boolean (For testing purposes)
        autoaccept              # Boolean
    ):    
        self.verbose = verbose
        self.internet_status =  internet_status
        self.ethernetname = ethernetname
        self.wifiname =  wifiname
        self.ini_file =  ini_file
        self.persistence_achieved = persistence_achieved
        self.test = test
        self.autoaccept = autoaccept

        self.ap_type = None

    def logic_skeleton(self):
        '''
        Purpose:
            Acts as a skeleton, for the logic
            tying it together, and deciding
            upon what to implement and how        
        '''

        changes_made = False

        default_settings = configurations.ini_default_settings(self.verbose)
        settings = {
            'ssid': None,                   # str
            'mac_address': None,            # str
            'encryption': None,             # str
            'password': None,               # str
            'range_from': "10.10.10.100",   # str
            'range_to': "10.10.10.255",     # str
            'channel': "1",                 # str
            'persistence': None             # str
        }
        while True:
            print("\x1b[34m[?]\x1b[0m Manual configuration")
            print(" "*4+"0. Terminate this program")
            print(" "*4+"1. Tear down AP and restore connectivity")
            print(" "*4+"2. Disable persistence")
            print(" "*4+"3. Create persistence")
            print(" "*4+"4. Set up an Access Point\n")
            choice = input("Make your choice (0/1/2/3/4):\n")

            try:
                if not (0 <= int(choice) <= 4):
                    print("Input must be in the range of 0 to 4. Please try again.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
            if choice == 0:
                exit(0)
            elif choice == 1:
                print("Removing isolation")
                configurations.remove_isolation(self.verbose)
            elif choice == 2:
                print("Disabling persistence")
                persistence_files = ["/root/firewall.sh", "/root/create_ap.sh", "/etc/cron.d/ap_persistence"]
                status = configurations.persistence_status(persistence_files)
                if status == False:
                    print("There is no persistence to remove.")
                    continue
                configurations.persistence_remove(self.verbose)
            elif choice == 3:
                print("Creating persistence")
                print("Note: It is assumed that the necessary AP configuration")
                print("      files are already in place.")
                print("      If alterations are made to the ip ranges of those files")
                print("      please rerun persistence creation. For security reasons")
                print("      changes in the ip range, cannot be retroactively")
                print("      accounted for once persistence have been set.")
                # Time to get the range_from and range_to from the /etc/dnsmasq.conf file
                # and then by extension an IP which can be used
                ip = configurations.find_usable_ip(self.verbose)
                if ip == None:
                    print("Unable to create persistence, as it was not possible")
                    print("to retrive a range, to generate a static IP needed for")
                    print("correctly configuring a dhcp server.")
                    continue
                configurations.persistence_create(ip, self.wifiname, self.verbose)
            elif choice == 4:
                    # I hate you
                    print("Manually updating the Access Point")
                    print("Note: Only the encryption type is required.")
                    print("      Based on that some additional requirements may appear")
                    user_input = ''
                    ### 1st step, encryption type
                    user_input = input("REQUIRED: Which encryption do you want? (none/wpa2)\n")
                    if user_input.lower() == 'none':
                        settings['encryption'] = 'none'
                    elif user_input.lower() == 'wpa2':
                        settings['encryption'] = 'wpa2'
                    else:
                        print("Unknown choice, starting over")
                        continue
                    if settings["encryption"].lower() == 'wpa2':
                        ### Step 1b, password

                        user_input = input("REQUIRED: Choose a password:\n")
                        # Warning, this could cause issues
                        settings["password"] = user_input
                    ### Step 2, choose an ssid (Note max 31 characters in length)
                    user_input = input("OPTIONAL: Choose a name for the AP (aka. ssid)\n")
                    if len(user_input) == 0 or len(user_input) > 31:
                        # Use a random name
                        settings['ssid'] = default_settings['ssid']
                        print(" "*10+"Using a randomized ssid: \""+default_settings['ssid']+"\"")
                    else:
                        settings['ssid'] = user_input
                    ### Step 3, ip range
                    print("OPTIONAL: Select an ip range for the dhcp server")
                    user_input = input("          Enter the first IP of the range\n")
                    range_from = user_input
                    user_input = input("          Enter the last IP of the range\n")
                    range_to = user_input
                    if configurations.is_valid_ip_address(range_from) and configurations.is_valid_ip_address(range_to):
                        if configurations.is_valid_range(range_from, range_to):
                            print("    Valid range '"+range_from+"' to '"+range_to+"'")
                        else:
                            # Using default values
                            print("    Invalid range, using default range of")
                            print("    10.10.10.100 to 10.10.10.255")
                            range_from = "10.10.10.100"
                            range_to = "10.10.10.255"
                    else: 
                        # Using default values
                        print("    Invalid range, using default range of")
                        print("    10.10.10.100 to 10.10.10.255")
                        range_from = "10.10.10.100"
                        range_to = "10.10.10.255"

                    settings['range_from'] = range_from
                    settings['range_to'] = range_to
                    ### Step 4 channel
                    user_input = input("OPTIONAL: Select a channel to use (1-11)")
                    try:
                        if 0 <= int(user_input) <= 11:
                            settings['channel'] = user_input
                            print("    Channel accepted")
                        else:
                            settings['channel'] = '1'
                            print(" "*10+"Channel rejected, using default channel 1")
                    except ValueError:
                            settings['channel'] = '1'
                            print(" "*10+"Channel rejected, using default channel 1")
            
            print("="*25)
            print("\x1b[34mAccess point activation\x1b[0m")
            print(" "*4+"Settings used   :")
            # Print each key-value pair with aligned values
            max_key_length = max(len(key) for key in settings)
            for key, value in settings.items():
                if value != None:
                    print(" "*22+f"{key.ljust(max_key_length)} | '{value}'")
            print(" "*4+"Settings omitted:")
            for key, value in settings.items():
                if value == None:
                    print(" "*22+f"{key.ljust(max_key_length)} | {value}")

            result = configurations.update_ap(settings,self.wifiname, self.verbose)
            if result:
                print("Successfully setup an AP")
            else:
                print("Failed setting up an AP ")
            ## End choice 4


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
        if self.ini_file == None or self.ini_file == '':
            return None
        else:
            print("\x1b[34m[?]\x1b[0m .ini file used  : "+ self.ini_file)

        # See if file (supplied argument) exists
        if ini_verified:
            ini_verified = configurations.ini_exist(self.ini_file)
            if ini_verified:
                print(" "*22+"File exists")
            else:
                print(" "*22+"File does not exist")
                ini_verified = False
            
        # Read the content
        if ini_verified:
            settings = configurations.read_ini_config(self.ini_file, self.verbose)
            if settings == None:
                ini_verified = False
                if self.verbose:
                    print(" "*20+"- 'Settings' section is \x1b[5;34;41mmissing\x1b[0m.")

        # Evaluate the settings
        # Are the settings enough to create an AP?
        if ini_verified:
            ini_type = configurations.determine_ini_ap_type(settings, self.verbose)
            if ini_type == None:
                ini_verified = False
                if self.verbose:
                    print("ini file failed. Unable to determine AP type")

        # Populate the required settings
        if ini_verified:
            tmp = configurations.ini_populate(settings, self.verbose)
            settings = tmp

        # Time to implement
        # Remember to create/update the hostapd.conf and dnsmasq.conf
            ###### TESTING
            if self.test:
                print("\x1b[46m[?]\x1b[0m .ini file"+" "*7+": \x1b[46mTEST\x1b[0m accepted")
                print(" "*4+"Settings used   :")
                # Print each key-value pair with aligned values
                max_key_length = max(len(key) for key in settings)
                for key, value in settings.items():
                    if value != None:
                        print(" "*22+f"{key.ljust(max_key_length)} | '{value}'")
                print(" "*4+"Settings omitted:")
                for key, value in settings.items():
                    if value == None:
                        print(" "*22+f"{key.ljust(max_key_length)} | {value}")
                return True
            ###### END TEST
            
            ## MANUAL ACCEPT
            user_input = ''
            print("Ready to implement!")
            if self.autoaccept:
                user_input = 'y'
                print("Auto accept, implementing AP based on supplied settings")
            else:
                user_input = input("Do you wish to proceed (Y/N)?")
            if user_input.lower() == 'y':
                '''
                Purpose:
                    Create the AP
                    By this point, everything related to the .ini
                    file should have been verified.
                    - All packages are installed
                    - AP ready to be setup
                    There are separate aspects to implement
                    unrelated to another
                    - mac_address
                    - Update dnsmasq.conf file
                    - Update hostapd.conf file
                    - Reset/initialize AP settings
                      This includes isolation
                Return:
                    True if the implementation succeed
                    False if it did not
                '''
                print(" "*4+"Settings used   :")
                # Print each key-value pair with aligned values
                max_key_length = max(len(key) for key in settings)
                for key, value in settings.items():
                    if value != None:
                        print(" "*22+f"{key.ljust(max_key_length)} | '{value}'")
                print(" "*4+"Settings omitted:")
                for key, value in settings.items():
                    if value == None:
                        print(" "*22+f"{key.ljust(max_key_length)} | {value}")

                result = configurations.update_ap(settings,self.wifiname, self.verbose)

                ## TODO: REVIEW AND IMPLEMENT PERSISTENCE

                return result
            else:
                return False
        else:
            # Something went wrong with the .ini file
            print("\x1b[34m[?]\x1b[0m .ini file       : Not used")
            return False




