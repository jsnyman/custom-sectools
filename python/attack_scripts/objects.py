import os
import sys
from creator import FolderCreator
from console import Console


class Project:
    def __init__(self, path=''):
        self.hosts = list()
        self.path = path
        if '' == path:
            pa = Console.prompt('Enter the project folder: ')
            self.path = os.path.abspath(pa)
            print ''
        self.password_file = ''
        self.check_structure()

    def __str__(self):
        s = '\n---------\n'
        s += 'Project:\n'
        s += '---------\n'
        for h in self.hosts:
            s += '%s \n' % h

        return s

    def check_structure(self):
        if self.path is not None:
            if not os.path.exists(self.path):
                a = Console.prompt('%s does not exist, create this folder (Y/N)? [y]' % self.path)
                if 'n' == a.lower():
                    print 'Well I have no idea what you would like to achieve here, bugger off then.'
                    sys.exit(1)
            # New or old, both folders go through the same process:
            FolderCreator.create_project_structure(self.path)
        else:
            print 'Buddy, hier\'s groot fout, project got no path set'
            sys.exit(1)

    def get_folder_name(self):
        return self.path

    def get_evidence_folder_name(self):
        return self.path + '/evidence'

    def get_hosts_file_name(self):
        return self.path + '/evidence/hosts.txt'

    def get_notes_file_name(self):
        return self.path + '/evidence/notes.md'

    def get_userlist_file_name(self):
        return self.path + '/users.txt'

    def get_password_file_name(self):
        return self.password_file

    def get_host_from_ip(self, ip=''):
        for h in self.hosts:
            if ip == h.ip:
                return h

    def get_port_from_ip_port_num(self, ip='', port_num=''):
        print 'get_port_from_ip_port_num %s:%s' % (ip, port_num)
        for h in self.hosts:
            if h is not None:
                print "found host"
            if ip == h.ip:
                if ip is not None:
                    print 'found ip'
                for p in h.ports:
                    if p is not None:
                        print 'port is not none: %s' % p.port_num
                    if port_num == p.port_num[:-4]:
                        print 'returning the fucking port: %s' % p
                        return p

    def read_existing_from_file(self):
        Console.inform('Reading from existing files')
        # Read hosts
        fn = self.get_hosts_file_name()
        with open(fn, 'r') as f:
            for ip in f.read().splitlines():
                self.add_host(ip.replace(' ', ''))
        # Read ports for each host
        for host in self.hosts:
            fn = host.get_ports_file_name()
            with open(fn, 'r') as f:
                for pds in f.read().splitlines():
                    pdsarr = pds.split('==')
                    p = Port(host=host, port_num=pdsarr[0], status=pdsarr[1], service=pdsarr[2], version=pdsarr[3])
                    host.add_port(p)

    # def write_hosts_to_file(self):
    #     with open(self.get_hosts_file_name(), 'w') as f:
    #         for host in self.hosts:
    #             f.write('%s \n' % host.ip)

    def add_host(self, ip):
        # Check if this host has not been added already
        for h in self.hosts:
            if ip == h.ip:
                return
        # Add ip that has not been added
        Console.add('Adding host %s' % ip)
        h = Host(self, ip)
        self.hosts.append(h)

    def update_project_hosts(self):
        with open(self.get_notes_file_name(), 'a') as ns:
            ns.write('## Hosts')
            ns.write('\n')
            with open(self.get_hosts_file_name(), 'w') as hs:
                for host in self.hosts:
                    hs.write('%s \n' % host.ip)
                    ns.write('# %s \n' % host.ip)


class Host:
    def __init__(self, project, ip):
        self.ip = ip
        self.path = project.get_evidence_folder_name() + '/' + self.ip
        self.ports = list()
        self.check_structure()

    def __str__(self):
        s = '%s:\n' % self.ip
        for p in self.ports:
            s = s + p.__str__() + '\n'
        return s

    def check_structure(self):
        if self.path is not None:
            if not os.path.exists(self.path):
                FolderCreator.create_host_folder(self)
        else:
            print 'Buddy, hier\'s groot fout, project got no path set'
            sys.exit(1)

    def get_folder_name(self):
        return self.path

    def get_ports_file_name(self):
        return self.path + '/ports.txt'

    def get_notes_file_name(self):
        return self.path + '/notes.md'

    def get_tcp_ports_as_string(self):
        tcp_ports = ''
        for p in self.ports:
            if 'tcp' in p.port_num:
                tcp_ports += p.port_num[:-4] + ','
        return tcp_ports[:-1]

    def get_udp_ports_as_string(self):
        udp_ports = ''
        for p in self.ports:
            if 'udp' in p.port_num:
                udp_ports += p.port_num[:-4] + ','
        return udp_ports[:-1]

    def add_port(self, po):
        for p in self.ports:
            if po.port_num == p.port_num:
                Console.inform('Updating port %s' % po.port_num)
                p.status = po.status
                p.service = po.service
                p.version = po.version
                return
        # If this port has not been added before
        Console.add('Adding port %s' % po.port_num)
        self.ports.append(po)

    def add_port_details(self, port_num, status='', service='', version=''):
        # Check first if port already exists, then update
        for p in self.ports:
            if port_num == p.port_num:
                Console.inform('Updating port %s' % port_num)
                p.status = status
                p.service = service
                p.version = version
                return
        # If this port has not been added before
        Console.add('Adding port %s' % port_num)
        p = Port(self, port_num, status, service, version)
        self.ports.append(p)

    def write_ports_to_file(self):
        with open(self.get_notes_file_name(), 'a') as nf:
            nf.write('Port Num | Service | Version\n')
            nf.write('---|---|---\n')
            with open(self.get_ports_file_name(), 'w') as pf:
                for p in self.ports:
                    pf.write('%s==%s==%s==%s\n' % (p.port_num, p.status, p.service, p.version))
                    if 'open' == p.status:
                        nf.write('%s | %s | %s\n' % (p.port_num, p.service, p.version))


class Port:

    def __init__(self, host, port_num, status='', service='', version=''):
        self.port_num = port_num
        self.status = status
        self.service = service
        self.version = version
        self.path = host.get_folder_name() + '/' + self.port_num[:-4]

    def __str__(self):
        return '\t%s: %s \t\t%s\t\t%s' % (self.port_num, self.status, self.service, self.version)

    def get_folder_name(self):
        return self.path
