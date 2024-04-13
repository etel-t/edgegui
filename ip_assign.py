import subprocess
import ipaddress
import os

def validate_ip():
    try:
        print("Enter IPv4 Address (Example: 192.168.1.2/24):")
        ip = input()
        ipaddress.ip_interface(ip)
        return ip
    except ValueError:
        print("Pl enter a valid IP address")
        return validate_ip()
    
def validate_gateway(ip):
    try:
        print("Enter the default gateway")
        gw = input()
        network = ipaddress.ip_network(ip, strict=False)
        gateway_ip = ipaddress.ip_address(gw)
        if gateway_ip in network.hosts():
            return gw
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
        print("Pl enter a valid Gateway address")
        return validate_gateway(ip)
    
def main():
    try:
        print(f"WAN interface doesn't get address from DHCP.\nPl assign static IP.")
        ip = validate_ip()
        gw = validate_gateway(ip)
        with open("/etc/vpp/bootstrap.vpp", "r") as f:
            data_boot = f.read()
            f.close()
        with open("/etc/vpp/backup.vpp", "r") as f:
            data_backup = f.read()
            f.close()        
        data_backup = data_backup.replace(f"set dhcp client intfc GigabitEthernet0/3/0", f"set int ip address GigabitEthernet0/3/0 {ip}")
        data_boot = data_boot.replace(f"set dhcp client intfc GigabitEthernet0/3/0", f"set int ip address GigabitEthernet0/3/0 {ip}")
        data_backup = data_backup + f"\nip route add 0.0.0.0/0 via {gw}"
        data_boot = data_boot + f"\nip route add 0.0.0.0/0 via {gw}"
        with open("/etc/vpp/bootstrap.vpp", "w") as f:
            f.write(data_boot)
            f.close()
        with open("/etc/vpp/backup.vpp", "w") as f:
            f.write(data_backup)
            f.close()
        os.system(f"ip addr add {ip} dev Reach_int1")
        with open("/etc/frr/frr.conf", "a") as f:
            f.write("\n!\nip route 0.0.0.0/0 {gw}\n!\n")
            f.close()
        os.system("systemctl restart frr")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
