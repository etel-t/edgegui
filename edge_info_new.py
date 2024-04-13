#!/usr/bin/python3
import netifaces
import psutil
import time
import subprocess
import os


def countdown_timer(seconds):
    for remaining in range(seconds, 0, -1):
        minutes, secs = divmod(remaining, 60)
        timer = '{:02d}:{:02d}'.format(minutes, secs)
        print(f"Time left: {timer}", end='\r')
        time.sleep(1)    

def get_interface_details():  
    interface = psutil.net_if_addrs()  
    for intfc_name in interface:
        if intfc_name == "Reach_int2":
            return True
    print("Initializing ReachEdge pl wait. Don't Restart or Power OFF the VM ")
    countdown_timer(60)
    return get_interface_details()

def get_interface_addresses():
    addresses = {}
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        iface_details = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in iface_details:
            ipv4_address = iface_details[netifaces.AF_INET][0]['addr']
        else:
            ipv4_address = None        
        addresses[interface] = {'ipv4': ipv4_address}
    return addresses

def get_default_route_info():
    try:
        # Execute the VPP CLI command to display FIB table information
        output = subprocess.check_output(['sudo', 'vppctl', 'show ip fib'], text=True)
        # Parse the output to extract the default route information
        default_route_info = None
        i = 0
        for line in output.split('\n'):
            if '0.0.0.0/0' in line:                
                i = 1
            if i > 0 and i < 5:
                i = i+1
            if i == 5:
                i = i+1
                default_route_info = line.split("via")[1].split(" ")[1] 
                print(default_route_info)
                break
        return default_route_info
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e)
        return None
    
def update_motd_with_network_info():
    print("\nWelcome to ReachWAN!\n")
    print("***********************************************************")    
    get_interface_details()
    default_gw = get_default_route_info()
    if default_gw == None:
        os.system("sudo python3 /etc/reach/ip_assign.py")     
        
    interface_addresses = get_interface_addresses()    
    print("ReachEdge Local Web Interface is enabled on all interfaces.")
    print("It can be accessed using any of your device IP & port 5005.")
    print("If not registered pl Register your device with ReachManage.")
    print("Access ReachEdge User Interface with the following URL:\n") 
    for interface, address_info in interface_addresses.items():
        if interface != "lo" and interface != "tun0":                
            print(f'\t"http://{address_info["ipv4"]}:5005/login/"')              
    print("\nUse below credentials for Login.")  
    print("Username: etel")
    print("Password: reachwan")          
    print("***********************************************************")   


if __name__ == "__main__":
    update_motd_with_network_info()
