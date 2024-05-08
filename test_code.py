import subprocess

def test_colors():
    RED = '\033[91m'  # Red for errors
    GREEN = '\033[92m'  # Green for success
    RESET = '\033[0m'  # Reset to default terminal color
#    print(f"")
#    print(f"{RED}Error executing command:{RESET}")
#    print("\x1b[31mError:\x1b[0m")
#    print(f"{GREEN}SUCCESS executing command:{RESET}")
#    print("\x1b[32mSUCCESS:\x1b[0m")

    print("\x1b[1;34;40mPython coloring test\x1b[0m")
    print(f"GREY    \t\x1b[30m[30]\033[0m\t"
           "\x1b[40m[40]\033[0m\t"
           "\x1b[90m[90]\033[0m\t"
           "\x1b[100m[100]\033[0m")
    print(f"RED     \t\x1b[31m[31]\033[0m\t"
           "\x1b[41m[41]\033[0m\t"
           "\x1b[91m[91]\033[0m\t"
           "\x1b[101m[101]\033[0m")
    print(f"GREEN   \t\x1b[32m[32]\033[0m\t"
           "\x1b[42m[42]\033[0m\t"
           "\x1b[92m[92]\033[0m\t"
           "\x1b[102m[102]\033[0m")
    print(f"YELLOW  \t\x1b[33m[33]\033[0m\t"
           "\x1b[43m[43]\033[0m\t"
           "\x1b[93m[93]\033[0m\t"
           "\x1b[103m[103]\033[0m")
    print(f"BLUE    \t\x1b[34m[34]\033[0m\t"
           "\x1b[44m[44]\033[0m\t"
           "\x1b[94m[94]\033[0m\t"
           "\x1b[104m[104]\033[0m")
    print(f"PURPLE  \t\x1b[35m[35]\033[0m\t"
           "\x1b[45m[45]\033[0m\t"
           "\x1b[95m[95]\033[0m\t"
           "\x1b[105m[105]\033[0m")
    print(f"CYAN    \t\x1b[36m[36]\033[0m\t"
           "\x1b[46m[46]\033[0m\t"
           "\x1b[96m[96]\033[0m\t"
           "\x1b[106m[106]\033[0m")
    


######### Isolation

def command_execution_color(verbose = False):
    '''
    Purpose:
        Create isolation on the machine.
        Execute some commands
        - Activate a firewall by blocking all traffic
          on ALL ethernet devices, allowing only the wifi device
        - sudo airmon-ng check kill
    '''
    commands = [
        ["cat", "sdfadsf"],
        ["ls", "-la"]
    ]
    if verbose:
        print(" "*4+"Executing commands: (RED - Fail, GREEN - Success)")
    for command in commands:
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if verbose:
                if result.returncode == 0:
                    print(" "*4+"\x1b[32m[+]\033[0m"+f" \x1b[35m{' '.join(command)}\033[0m")
                else:
                    print(" "*4+"\x1b[31m[!]\033[0m"+f" \x1b[35m{' '.join(command)}\033[0m")
        except subprocess.CalledProcessError as e:
            if verbose:
                print(" "*4+f"\x1b[41m[!] Error executing command\033[0m:\n"+" "*4+f"\x1b[35m{' '.join(command)}\033[0m\n    Error: {str(e)}")
    return True




# Example usage
if __name__ == '__main__':
    devices = ['derp', 'derpina', 'troll']
#    create_write(devices)
#    services = interfering_services()
#    for service in services:
#        print(service)
    test_colors()
    command_execution_color(True)