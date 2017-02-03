import re
import shlex
import subprocess
from console import Console
from objects import Port


class Runner(object):
    @staticmethod
    def get_safe_filename(filename):
        return filename.replace(':', '_')

    @staticmethod
    def run(cmd, out_filename=''):
        Console.run(cmd)
        args = shlex.split(cmd)
        if '' != out_filename.lower():
            outfile = open(Runner.get_safe_filename(out_filename), 'w')
            errfile = open(Runner.get_safe_filename(out_filename) + '.err', 'w')
            proc = subprocess.Popen(args, stdout=outfile, stderr=errfile)
        else:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc
        # to block execution on the process returned from here use the statement below
        # out, err = p.communicate()


class NmapScans(object):

    _live_host_flags = '-sn' # -PE'
    _tcp_quick_flags = '-Pn -n --top-ports 1000'
    _tcp_all_ports_flags = '-Pn -n -p-'
    _tcp_all_options_flags = '-Pn -n -A -p '
    _udp_flags = '-Pn -n -sUV -F'
    _udp_all_options_flags = '-Pn -n -sU -A -p '

    @staticmethod
    def get_safe_filename(filepath, flags, iprange):
        return filepath + '/nmap' + flags.replace(' ', '') + '-' + iprange.replace('/', '_') + '.txt'

    @staticmethod
    def get_grep_filename(filename):
        return filename[:-4] + '-oG.txt'

    @staticmethod
    def prompt_hosts(project):
        s = list()
        a = Console.prompt('Do you want to scan all known hosts (Y/N)? [y]')
        if 'n' == a.lower():
            for host in project.hosts:
                a = Console.prompt('Scan %s (Y/N)? [y]' % host.ip)
                if 'n' != a.lower():
                    s.append(host.ip)
        else:
            Console.inform('Scanning all known hosts')
            for host in project.hosts:
                s.append(host.ip)
        return s

    @staticmethod
    def scan_for_live_hosts(project):
        print ''
        # Scan for live hosts
        ipr = Console.prompt('Enter the IP range to test for liveness: ')

        # 'Liveness test: nmap -sn -PE [ip ranges] -oG [filename]
        fn = NmapScans.get_safe_filename(project.get_evidence_folder_name(), NmapScans._live_host_flags, ipr)
        fng = NmapScans.get_grep_filename(fn)

        # Run nmap and write evidence file
        cmd = 'nmap %s -oG %s %s' % (NmapScans._live_host_flags, fng, ipr)
        proc = Runner.run(cmd)
        proc.communicate()
        all_ips = NmapParser.get_ips_from_sn_pe(fng)
        Console.inform('The following IP addresses were live:')
        for ip in all_ips:
            print '    %s' % ip
        print ''

        # Check if all the IP's should be included, add what is necessary
        i = Console.prompt('Include all IP\'s in testing (Y/N)? [y]')
        if 'n' == i.lower():
            Console.inform('Choose the IP addresses to be included:')
            for ip in all_ips:
                a = Console.prompt('%s (Y/N)? [y]' % ip)
                if 'n' != a.lower():
                    project.add_host(ip)
        else:
            for ip in all_ips:
                project.add_host(ip)

        Console.inform('Using %d IP addresses out of the %d originally found' % (len(project.hosts), len(all_ips)))
        print ''

        # update the necessary files after new hosts added
        project.update_project_hosts()

    @staticmethod
    def nmap_scan_add(host, fn, flags, ip):
        # Run nmap
        cmd = 'nmap %s %s' % (flags, ip)
        proc = Runner.run(cmd, fn)
        proc.communicate()
        # Read ports from file
        ps = NmapParser.get_ports(fn)
        for po in ps:
            host.add_port(po)
        host.write_ports_to_file()

    @staticmethod
    def scan_quick_tcp(project):
        arr = NmapScans.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                fn = NmapScans.get_safe_filename(host.get_folder_name(), NmapScans._tcp_quick_flags, ip)
                NmapScans.nmap_scan_add(host, fn, NmapScans._tcp_quick_flags, ip)

    @staticmethod
    def scan_udp(project):
        arr = NmapScans.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                fn = NmapScans.get_safe_filename(host.get_folder_name(), NmapScans._udp_flags, ip)
                NmapScans.nmap_scan_add(host, fn, NmapScans._udp_flags, ip)

    @staticmethod
    def scan_all_tcp_ports(project):
        arr = NmapScans.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                fn = NmapScans.get_safe_filename(host.get_folder_name(), NmapScans._tcp_all_ports_flags, ip)
                NmapScans.nmap_scan_add(host, fn, NmapScans._tcp_all_ports_flags, ip)

    @staticmethod
    def scan_full_tcp_ports(project):
        arr = NmapScans.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                flags = NmapScans._tcp_all_options_flags
                flags += host.get_tcp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_tcp_services_' + ip + '.txt'
                NmapScans.nmap_scan_add(host, fn, NmapScans._tcp_all_ports_flags, ip)

    @staticmethod
    def scan_full_udp_ports(project):
        arr = NmapScans.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                flags = NmapScans._udp_all_options_flags
                flags += host.get_udp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_udp_services_' + ip + '.txt'
                NmapScans.nmap_scan_add(host, fn, NmapScans._tcp_all_ports_flags, ip)

    @staticmethod
    def scan_all_ports(project):
        arr = NmapScans.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                # UDP
                fn = NmapScans.get_safe_filename(host.get_folder_name(), NmapScans._udp_flags, ip)
                NmapScans.nmap_scan_add(host, fn, NmapScans._udp_flags, ip)
                # TCP All ports
                fn = NmapScans.get_safe_filename(host.get_folder_name(), NmapScans._tcp_all_ports_flags, ip)
                NmapScans.nmap_scan_add(host, fn, NmapScans._tcp_all_ports_flags, ip)
                # UDP Version scanning
                flags = NmapScans._udp_all_options_flags
                flags += host.get_udp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_udp_services_' + ip + '.txt'
                NmapScans.nmap_scan_add(host, fn, flags, ip)
                # TCP Version scanning
                flags = NmapScans._tcp_all_options_flags
                flags += host.get_tcp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_tcp_services_' + ip + '.txt'
                NmapScans.nmap_scan_add(host, fn, flags, ip)


class NmapParser(object):

    IP_REGEX = '(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})'

    @staticmethod
    def get_ips_from_sn_pe(fn):
        ips = []
        with open(fn, 'r') as f:
            for line in f:
                if 'up' in line.lower():
                    line_ips = re.findall(NmapParser.IP_REGEX, line)
                    if len(line_ips) > 0:
                        for ip in line_ips:
                            ips.append(ip)
        return ips

    @staticmethod
    def get_ports(fn):
        ps = list()
        patstr = '(\d{1,5}[/](udp|tcp))\s+(\S+)\s+(\S+)(.*)'
        with open(fn, 'r') as f:
            for line in f:
                # print line
                m = re.match(patstr, line)
                if m is not None:
                    po = Port(port_num=m.group(1), status=m.group(3), service=m.group(4), version=m.group(5).strip())
                    ps.append(po)
        return ps


class WebCommands(object):
    @staticmethod
    def get_safe_filename(filename):
        return filename.replace('://', '-').replace('/', '-')

    @staticmethod
    def prompt_hosts(project):
        str_list = list()
        for host in project.hosts:
            for port in host.ports:
                if 'http' == port.service or 'https' == port.service.lower():
                    str_list.append(host.ip + ':' + port.port_num[:-4])
        Console.inform('The following http(s) ports were found:')
        for s in str_list:
            Console.inform('\t%s' % s)

        a = Console.prompt('Do you want to run web scans on all of these (Y/N)? [y])')
        if 'n' != a.lower():
            Console.inform('Adding all identified ports')
        else:
            r_list = list()
            for s in str_list:
                b = Console.prompt('Add %s to the list (Y/N)? [y]' % s)
                if 'n' == b.lower():
                    r_list.append(s)
                    Console.inform('%s removed' % s)
                else:
                    Console.inform('%s added to the scan list' % s)
            for s in r_list:
                str_list.remove(s)

        a = Console.prompt('Do you want to manually add ports (Y/N)? [n]')
        while 'y' == a.lower():
            ip = Console.prompt('Please enter the host IP address: ')
            po = Console.prompt('Now the port number: ')
            s = ip + ':' + po
            str_list.append(s)
            Console.inform('Added %s to the scan list' % s)
            a = Console.prompt('Do you want to add any more ports (Y/N)? [n]')

        return str_list

    @staticmethod
    def prompt_hosts_manual(project):
        str_list = list()
        return str_list

    @staticmethod
    def run_webscans(project): # evidence_folder, host, port='80'):
        ip_list = WebCommands.prompt_hosts(project)
        for i in ip_list:
            print i
            a = i.split(':')
            h = a[0]
            p = a[1]
            host = project.get_host_from_ip(h)
            if host is not None:
                fn = host.get_folder_name() + '/whatweb_' + i
                WebCommands.whatweb(url=i, filename=fn)
                fn = host.get_folder_name() + '/dirsearch_' + i
                WebCommands.nikto(host=h, port=p, filename=fn)
                fn = host.get_folder_name() + '/nikto_' + i
                WebCommands.dirsearch(url=i, filename=fn)

    @staticmethod
    def run_whatweb(project):
        url = Console.prompt('Enter the URL to run WhatWeb on: ')
        fn = project.get_evidence_folder_name() + '/whatweb_' + WebCommands.get_safe_filename(url)
        WebCommands.whatweb(url, fn)

    @staticmethod
    def whatweb(url, filename):
        cmd = 'whatweb %s' % url
        p = Runner.run(cmd, filename)
        out, err = p.communicate()

    @staticmethod
    def run_nikto(project):
        host = Console.prompt('Enter the host to run nikto on (NOT URL): ')
        port = Console.prompt('Enter the port to run nikto on: [80]')
        root = Console.prompt('Enter the root folder: [/]')
        if '' == port:
            port = '80'
        if '' == root:
            root ='/'
        host + '_' + port
        s = host + '_' + port + root
        fn = project.get_evidence_folder_name() + '/nikto_' + WebCommands.get_safe_filename(s)
        WebCommands.nikto(host=host, port=port, filename=fn, root=root)

    @staticmethod
    def nikto(host, port, filename, root='/'):
        cmd = 'nikto -Tuning x6 -host %s -port %s -root %s' % (host, port, root)
        p = Runner.run(cmd, filename)
        out, err = p.communicate()

    @staticmethod
    def run_dirsearch(project):
        url = Console.prompt('Enter the URL to run dirsearch on: ')
        ext = Console.prompt('Enter the extensions to test for: [htm]')
        wl = Console.prompt('Enter the wordlist you want to use: [default]')
        fn = project.get_evidence_folder_name() + '/dirsearch_' + WebCommands.get_safe_filename(url)
        WebCommands.dirsearch(url=url, filename=fn, wordlist=wl, extensions=ext)

    @staticmethod
    def dirsearch(url, filename, wordlist='', extensions='htm'):
        cmd = 'python3 /root/tools/dirsearch/dirsearch.py -u %s -e %s' % (url, extensions)
        if '' != wordlist:
            cmd += ' -w ' + wordlist
        cmd += ' --simple-report=%s' % filename
        p = Runner.run(cmd)
        out, err = p.communicate()


# This method used for testing
if __name__ == '__main__':
    print ''
    # p = Project()
    # p.add_host('192.168.56.102')
    # # # NmapScans.scan_quick_tcp(p)
    # # # NmapScans.scan_udp(p)
    # # NmapScans.scan_all_tcp_ports(p)
    # # # NmapParser.add_ports_project(p, NmapScans._udp_flags, tcp=0)
    #
    # Commands.run_whatweb('192.168.56.102:80', '/root/automation/evidence/whatweb_80.txt')
    # Commands.run_dirsearch('192.168.56.102:80', '/root/automation/evidence/dirsearch_80.txt')
    # Commands.run_whatweb('192.168.56.102:666', '/root/automation/evidence/whatweb_666.txt')
    # Commands.run_dirsearch('192.168.56.102:666', '/root/automation/evidence/dirsearch_666.txt')
    # Commands.run_whatweb('192.168.56.102:12380', '/root/automation/evidence/whatweb_12380.txt')
    # Commands.run_dirsearch('192.168.56.102:12380', '/root/automation/evidence/dirsearch_12380.txt')
    # Commands.run_nikto('192.168.56.102', '12380', '/root/automation/evidence/nikto_12380.txt')

    # filename = '/root/automation/test/evidence/192.168.56.102/nmap-Pn-n-p--192.168.56.102.txt'
    # filename = '/root/automation/test/evidence/192.168.56.102/nmap-Pn-n-sUV-F-192.168.56.102.txt'
    # listt = NmapParser.get_ports(filename)
