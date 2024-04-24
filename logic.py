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
        
        #    ap_name = 
        ip = [10,10,10,100]
        range_from = [10,10,10,100]
        range_to = [10,10,10,255]


    def logic_skeleton(self):
        '''
        Look at isolation status
        '''
        


        '''
        An .ini file was supplied, so....
        let's see if it is working and can be used
        '''
        if len(self.ini_file) > 0:
            self.ini_choice()



    def ini_choice(self):
        '''
        Purpose:
            Review the .ini file status 
        Return:
        '''
        # Create an boolean that is true, and run it through tests
        # if any test fail, set the variable to False
        ini_verified = True
        print("\x1b[34m[?]\x1b[0m .ini file used  : "+ self.ini_file)
        # See if file exist
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


    def use_ini_files(self):
        '''
        Purpose:
            See if an ini_file has been supplied and can be
            used.
        Return:
            None if the file does not exist or cannot be used
        '''


        # check if file argument is supplied
        if not self.ini_file_path:
            return None

        if not configurations.ini_exist(self.ini_file_path): # does not exist
            print("\x1b[31m[!]\x1b[0m \x1b[5;34;41mEdge case\x1b[0m         : No Wireless Interface located")
            return None

        config_settings = configurations.read_ini_config(self.ini_file_path, self.verbose)
        if not config_settings:
            print("\x1b[31m[!]\x1b[0m \x1b[5;34;41mEdge case\x1b[0m       : No Wireless Interface located")

