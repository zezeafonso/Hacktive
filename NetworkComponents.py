import queue
import threading 
import multiprocessing

import SpecificExceptions as SE
import Methods
from AbstractClasses import AbstractNetworkComponent
import ThreadShares as TS
from Events import Run_Event


def throw_run_event_to_command_listener(event:Run_Event) -> None:
    TS.cmd_queue.put(event)



class Port(AbstractNetworkComponent):
    def __init__(self, port_number:str, service:str):
        self.port_number = port_number
        self.service = service

    def display(self):
        pass

    def updateComponent(self, add_nc:AbstractNetworkComponent):
        pass

    def auto(self):
        if self.service == 'domain':
            return []
        elif self.service == 'kerberos-sec':
            return []
        elif self.service == 'microsoft-ds' or port_number == '445' or port_number == '135':
            return []
        elif self.service == 'ldap':
            return []
        elif self.service == 'msrpc':
            return []
        else:
            return []



class Host(AbstractNetworkComponent):
    """
    to add:
    - service scan 
    - hostname translation
    """
    #methods = {Methods.PortScan._name: Methods.PortScan}
    methods = {Methods.NBNSIPTranslation._name: Methods.NBNSIPTranslation}
    ports = dict()
    hostname = None
    ip = None
    dc = False
    netbios_hostname = None
    netbios_groups = dict() # each group will hold a list of the roles this machines takes
    DNS_hostname = None
    fqdn = None
    
    def __init__(self, path:dict, ip:str=None,hostname:str=None):
        if hostname is not None:
            self.hostname = hostname     
        if ip is not None:
            self.ip = ip
        self.path = path.copy()
        self.path['host'] = self

    def to_str(self):
        return f"{self.hostname}"

    def display(self):
        print(f"Host:{self.hostname}")

    def auto(self):
        for method in self.methods:
            list_events = self.methods[method].create_run_events(self)
            for event in list_events:
                throw_run_event_to_command_listener(event)
        pass

    def update_hostname(self, hostname:str):
        if self.hostname is not None:
            if self.hostname != hostname:
                print("Found new hostname: {hostname} for host with ip: {self.ip} and hostname {self.hostname}")
        else:
            self.hostname = hostname
            # TODO - CALL AUTO METHODS FOR THIS (NOTHING FOR NOW)

    def get_ip(self):
        return self.ip

    def updateComponent(self, add_nc:AbstractNetworkComponent):
        if isinstance(add_nc, Port):
            if add_nc.port_number in self.ports:
                pass
            else:
                self.ports[add_nc.port_number] = add_nc
                if not self.dc:
                    dc_services = ['domain', 'kerberos-sec', 'msrpc', 'ldap', 'microsoft-ds']
                    # Check if all elements are in the dictionary
                    all_present = all(service in services_dict for service in dc_services)
                    if all_present:
                        self.dc = True
                        print(f"[+] We found a new DC with ip: {self.ip}")

        else:
            raise SE.NoUpdateComponentForThatClass()


    def merge_host_ip_with_another_host_hostname(self, host_hostname:'Host'):
        """
        [IMPORTANT] : in the network don't forget to change the host in the
        hostname dict, otherwise it will just keep referencing the 'previous' host.

        The host_hostname is supposed to be the same host as this one. 
        We just found the hostname first when we didn't knew the ip address,
        and now we want to merge the information from the both.

        + [IMPORTANT]: i will assume that it's impossible for us to have read 
        different services for the same port number. 

        only different values might be: ports, dc, hostname
        """
        for port_number in host_hostname.ports:
            if port_number not in self.ports:
                self.ports[port_number] = host_hostname.ports[port_number]

        # if we knew that it was a DC, only using the hostname
        if host_hostname.dc != self.dc:
            if host_hostname.dc == True:
                self.dc = True

        # update the hostname
        self.hostname = host_hostname.hostname


    def activate_port(self, port_number:str):
        # the port was already found
        if port_number in self.ports:
            return [] # no new methods
        else:
            self.ports[port_number] = Port(port_number=port_number, service='')
            auto_methods = self.ports[port_number].auto()
            return auto_methods

    def activate_smb_methods(self):
        """
        No smb methods for now.
        """
        return []

    def update_netbios_group(self, group_name:str):
        if group_name in self.netbios_groups:
            pass
        elif group_name not in self.netbios_groups:
            self.netbios_groups[group_name] = list() # emtpy list

    def add_role_to_netbios_group(self, role:str, group:str):
        if group not in self.netbios_groups:
            self.netbios_groups[group] = list()
        if role not in self.netbios_groups[group]:
            self.netbios_groups[group].append(role)
            if role == '1b':
                return self.found_dc_methods()


    def found_dc_methods(self):
        """
        the methods for when we find a dc
        """
        print("dc methods")
        return [] # for now
        

    def found_hostname_methods(self, hostname:str):
        """
        the methods for when we found a hostname
        """
        return [] # for now

    def get_root(self):
        return self.path['root']

    def get_interface(self):
        return self.path['interface']

    def get_network(self):
        return self.path['network']

    def get_host(self):
        return self.path['host']



class Network(AbstractNetworkComponent):
    """
    to add:
    - get the dns server for it

    """
    methods = {Methods.ArpScan._name: Methods.ArpScan}
    #methods = {}
    network_address = None
    
    def __init__(self, network_address:str, path:dict):
        self.network_address = network_address
        #TODO: search for hosts using ip address
        self.hosts = {}
        self.hostnames = {} # point to the same hosts as hosts, but uses hostnames
        self.path = path.copy()
        self.path['network'] = self

    def auto(self):
        print("auto network")
        # no need for lock, the methods don't change
        list_events = []
        for method in self.methods:
            list_events = self.methods[method].create_run_events(self)
            for event in list_events:
                throw_run_event_to_command_listener(event)

    def add_our_ip(self, ip:str):
        self.our_ip = ip

    # LOCK
    def attach_host(self, ip:str):
        with TS.shared_lock:
            if ip in self.hosts:
                pass
            else:
                # TODO: must also accept hostnames
                print(f"creating new host: {ip}")
                new_host = Host(ip=ip, path=self.path)
                self.hosts[ip] = new_host
                return new_host

    # PLEASE USE A LOCK
    def check_for_host_with_ip(self, host_ip:str):
        """
        if host exists, return the object
        """
        if host_ip in self.hosts:
            return {'exists':'yes', 'object':self.hosts[host_ip]}
        return {'exists':'no'}

    # PLEASE USE A LOCK
    def create_host_with_ip(self, ip:str):
        """
        creates the host; attaches it to the network obj;
        returns the list of methods to run
        """
        new_host_obj = Host(ip=ip, path=self.path)
        self.hosts[ip] = new_host_obj
        res = {'object': new_host_obj, 'methods':self.found_ip_host_methods(new_host_obj)}
        return res

    # PLEASE USE A LOCK
    def found_ip_host_methods(self, host:Host):
        """
        the methods that we'll run when we find a host
        MUST RETURN A LIST
        """
        return [host.auto]

    def reference_new_host_using_NetBIOS_hostname(self, host:Host, hostname:str):
        self.hostnames[hostname] = host
    
    def attach_NetBIOS_hostname_to_ip_host(self, hostname:str, ip:str) -> list:
        # TODO: check if the hostname didn't already exist in the self.hostnames
        # get the host with the ip
        ip_host = self.hosts[ip]
        
        # check if the host with that hostname exists, 
        if ip_host.hostname != None:
            # we found a different one
            if ip_host.hostname != hostname:
                print(f"We found a new hostname {hostname} for a host {ip} that already had a hostname {self.hostname}")
                return []
            # we found the same one
            if ip_host.hostname == hostname:
                return []

        # check if the hostname was referencing a host
        if hostname in self.hostnames:
            # merge information with the ip host (will give methods)
            ip_host.merge_host_ip_with_another_host_hostname(self.hostnames[hostname])
            # update the hostname referencing
            self.reference_new_host_using_NetBIOS_hostname(host=ip_host, hostname=hostname)
            return []

        # if it's a completely new hostname
        else: 
            # update the hostname in host
            ip_host.update_hostname(hostname)
            # reference a host using hostname
            self.reference_new_host_using_NetBIOS_hostname(host=ip_host, hostname=hostname)
            return ip_host.found_hostname_methods(hostname)


    """
    returns:
    + host object
    + auto methods to call (only if we found something new)
    """
    def found_NetBIOS_hostname(self, hostname:str):
        if hostname in self.hostnames:
            return {'object':self.hostnames[hostname], 'methods':[]}
        else:
            # create hostname
            host_hostname = Host(hostname=hostname, path=self.path)
            # reference it
            self.reference_new_host_using_hostname(host=host_hostname, hostname=hostname)
            methods_to_call = host_hostname.found_hostname_methods(hostname)
            return {'object':host_hostname, 'methods':methods_to_call}

    def get_host_with_ip(self, ip:str):
        if ip not in self.hosts:
            return None
        return self.hosts[ip]

    def updateComponent(self, add_nc:AbstractNetworkComponent):
        if isinstance(add_nc, Host):
            print(f"[+] Found new Livehost {add_nc.ip} for network {self.network_address}")
            self.hosts[add_nc.ip] = add_nc
        pass

    def get_network_address(self):
        n_a = None
        with TS.shared_lock:
            n_a = self.network_address
        return n_a

    def get_root(self):
        return self.path['root']

    def get_interface(self):
        return self.path['interface']

    def get_network(self):
        return self.path['network']

    def to_str(self):
        return f"{self.network_address}"



class Interface(AbstractNetworkComponent):
    """
    add: 
    - dhcp broadcast discover 
    - responder analyzer (more on this later)
    """
    methods = {}
    path = {}

    def __init__(self, interface_name:str, path:dict):
        self.interface_name = interface_name
        self.networks = {}
        self.path = path.copy()
        self.path['interface'] = self

    def add_network(self, network:Network):
        # TODO: check if already exists
        self.networks[network.network_address] = network

    # LOCK
    def attach_network(self, network_name:str):
        with TS.shared_lock:
            if network_name in self.networks:
                pass
            else:
                print(f"creating new network: {network_name}")
                new_network = Network(network_name, self.path)
                self.networks[network_name] = new_network
                return new_network

    # please use a LOCK
    def check_for_network_str(self, network_name:str):
        """
        if network exists, return the object
        """
        if network_name in self.networks:
            return {'exists': 'yes', 'object': self.networks[network_name]}
        return {'exists':'no'}

    def create_network_with_network_str(self, network_name:str):
        """
        creates the network; attaches it to the interface obj;
        returns the list of methods to run
        """
        new_network_obj = Network(network_name, self.path)
        self.networks[network_name] = new_network_obj
        res = {'object': new_network_obj, 'methods':self.found_network_methods(new_network_obj)}
        return res

    def found_network_methods(self, network:Network):
        """
        the methods that we'll run when we find a network
        MUST RETURN A LIST
        """
        return [network.auto]

    def get_network(self, network_name:str):
        if network_name not in self.networks:
            return None
        return self.networks[network_name]

    def user_interaction(self, banner:str):
        self.display()
        interface_banner = banner+' '+self_interface_name+' >'
        while True:
            user_choice = input(interface_banner)

            if user_choice == 'display':
                self.display()
            elif user_choice in self.networks:
                network = self.networks[user_choice]
                network.user_interaction(interface_banner)
            else:
                print("typo, try again")
                continue

    """
    Run this when we find a new interface
    """
    def auto(self):
        print("auto for interface")
        return # NOTHING FOR NOW
        # no need for lock, the methods don't change
        for method in self.methods:
            list_events = self.methods[method].create_run_events(self)
            for event in list_events:
                throw_run_event_to_command_listener(event)

    def display(self):
        print(f"Interface: {self.interface_name}")
        display_str = "networks:\n"
        for network_address in self.networks:
            display_str += " - "+self.networks[network_address].to_str() + '\n'
            display_str += "methods:"
        for method in self.__class__.methods:
            continue
        print(display_str)

    def updateComponent(self, nc_to_add:AbstractNetworkComponent):
        if isinstance(nt_to_add, Network):
            print(f"[+] Found new network {nc_to_add.network_address} for interface {self.interface_name}")
            self.add_network(nc_to_add)
        else:
            raise SE.NoUpdateComponentForThatClass()

    def get_root(self):
        return self.path['root']

    def get_interface(self):
        return self.path['interface']

    def get_interface_name(self):
        return self.interface_name




class Root(AbstractNetworkComponent):
    methods = {Methods.ListInterfaces._name: Methods.ListInterfaces}

    def __init__(self):
        self.interfaces = {}
        self.path = {'root':self} # the path to this object

    def add_interface(self, interface:Interface):
        # call the methods from the interface
        self.interfaces[interface.interface_name] = interface

    # LOCK.
    # if new object return it 
    def attach_interface(self, interface_name:str):
        with TS.shared_lock:
            if interface_name in self.interfaces:
                pass
            else:
                print(f"creating new interface: {interface_name}")
                new_interface = Interface(interface_name, self.path)
                self.interfaces[interface_name] = new_interface
                return new_interface

    def get_interface(self, interface_name:str):
        if interface_name not in self.interfaces:
            return None
        return self.interfaces[interface_name]

    # please use a LOCK
    def check_for_interface_name(self, interface_name:str):
        """
        if interface exists, return the object
        """
        if interface_name in self.interfaces:
            return {'exists': 'yes', 'object': self.interfaces[interface_name]}
        return {'exists':'no'}

    def create_interface_with_name(self, interface_name:str):
        """
        creates the interface; attaches it to the root obj;
        returns the list of methods to run
        """
        new_interface_obj = Interface(interface_name, self.path)
        self.interfaces[interface_name] = new_interface_obj
        res =  {'object':new_interface_obj, 'methods':self.found_interface_methods(new_interface_obj)}
        return res

    def found_interface_methods(self, interface:Interface):
        """
        the methods that we'll run when we find a interface
        MUST BE A LIST
        """
        return [interface.auto]
        

    # TODO: do with lock
    def updateComponent(self, nc_to_add:AbstractNetworkComponent):
        if isinstance(nc_to_add, Interface):
            print(f"Found new interface: {nc_to_add.interface_name} with networks: {nc_to_add.networks}")
            self.add_interface(nc_to_add)
        else:
            raise SE.NoUpdateComponentForThatClass()

    def auto(self, banner:str = 'console >'):
        # no need for lock, the methods don't change
        for method in self.methods:
            list_events = self.methods[method].create_run_events(self)
            for event in list_events:
                throw_run_event_to_command_listener(event)


    def get_root(self):
        return self.path['root']
