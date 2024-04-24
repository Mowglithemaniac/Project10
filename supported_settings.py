from dataclasses import dataclass



@dataclass
class simple_ap:
    '''
    '''
    ssid : int
    range_from : str
    range_to  : str
    channel : int


class wpa2_ap:
    ssid : int
    range_from : str
    range_to  : str
    channel : int
    password : str


