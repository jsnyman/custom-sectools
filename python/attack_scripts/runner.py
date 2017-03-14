import re
import shlex
import subprocess
import time
from console import Console
from creator import FolderCreator
from objects import Project, Port


class Runner(object):

    @staticmethod
    def check_password_file(project):
        if '' == project.get_password_file_name():
            Console.inform('The password file has not been set')
            project.password_file = Console.prompt('Enter the password file name:')
        a = Console.prompt('Use the project password file - %s (Y/N)? [y]' % project.password_file)
        pwf = project.password_file
        if 'n' != a.lower():
            pwf = Console.prompt('Enter the password file name:')
        return pwf

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


class NmapCommands(object):

    _max_nmap_scans = 5

    _ip_regex = '(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})'

    _live_host_flags = '-sn'
    _live_host_flags_pe = '-sn -PE'
    _tcp_quick_flags = '-Pn -n --top-ports 1000'
    _tcp_all_ports_flags = '-Pn -n -sS -T4 -p-'
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
        all_ips = set()

        # 'Liveness test1: nmap -sn [ip ranges] -oG [filename]
        fn = NmapCommands.get_safe_filename(project.get_evidence_folder_name(), NmapCommands._live_host_flags, ipr)
        fng = NmapCommands.get_grep_filename(fn)

        # Run nmap and write evidence file
        cmd = 'nmap %s -oG %s %s' % (NmapCommands._live_host_flags, fng, ipr)
        proc = Runner.run(cmd)
        proc.communicate()
        ips1 = NmapCommands.get_ips_from_sn_pe(fng)
        all_ips.update(ips1)

        # 'Liveness test2: nmap -sn -PE [ip ranges] -oG [filename]
        fn = NmapCommands.get_safe_filename(project.get_evidence_folder_name(), NmapCommands._live_host_flags_pe, ipr)
        fng = NmapCommands.get_grep_filename(fn)

        # Run nmap and write evidence file
        cmd = 'nmap %s -oG %s %s' % (NmapCommands._live_host_flags_pe, fng, ipr)
        proc = Runner.run(cmd)
        proc.communicate()
        ips2 = NmapCommands.get_ips_from_sn_pe(fng)
        all_ips.update(ips2)

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
        # This next line blocks the program from continuing
        proc.communicate()
        NmapCommands.add_ports_to_host(fn, host)

    @staticmethod
    def nmap_scan_add_nonblocking(fn, flags, ip):
        # Run nmap
        cmd = 'nmap %s %s' % (flags, ip)
        return Runner.run(cmd, fn)

    @staticmethod
    def scan_paralel(project, flags):
        arr = NmapCommands.prompt_hosts(project)
        ps = list()
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                fn = NmapCommands.get_safe_filename(host.get_folder_name(), flags, ip)
                proc = NmapCommands.nmap_scan_add_nonblocking(fn, flags, ip)
                ps.append(proc)
                # Throttle
                while len(ps) >= NmapCommands._max_nmap_scans:
                    print '.'
                    time.sleep(5)
                    for p in ps:
                        if p.poll() is not None:
                            ps.remove(p)
        # Wait for scans to complete
        while len(ps) > 0:
            print '.'
            time.sleep(5)
            for p in ps:
                if p.poll() is not None:
                    ps.remove(p)

        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                fn = NmapCommands.get_safe_filename(host.get_folder_name(), flags, ip)
                NmapCommands.add_ports_to_host(fn, host)

    @staticmethod
    def add_ports_to_host(filename, host):
        ps = list()
        pattern = '(\d{1,5}[/](udp|tcp))\s+(\S+)\s+(\S+)(.*)'
        with open(filename, 'r') as f:
            for line in f:
                m = re.match(pattern, line)
                if m is not None:
                    po = Port(host=host, port_num=m.group(1), status=m.group(3), service=m.group(4),
                              version=m.group(5).strip())
                    ps.append(po)
        for po in ps:
            host.add_port(po)
        host.write_ports_to_file()

    @staticmethod
    def scan_quick_tcp(project):
        arr = NmapCommands.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                fn = NmapCommands.get_safe_filename(host.get_folder_name(), NmapCommands._tcp_quick_flags, ip)
                NmapCommands.nmap_scan_add(host, fn, NmapCommands._tcp_quick_flags, ip)

    @staticmethod
    def scan_quick_tcp_paralel(project):
        NmapCommands.scan_paralel(project, NmapCommands._tcp_quick_flags)

    @staticmethod
    def scan_udp(project):
        arr = NmapCommands.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                fn = NmapCommands.get_safe_filename(host.get_folder_name(), NmapCommands._udp_flags, ip)
                NmapCommands.nmap_scan_add(host, fn, NmapCommands._udp_flags, ip)

    @staticmethod
    def scan_udp_paralel(project):
        NmapCommands.scan_paralel(project, NmapCommands._udp_flags)

    @staticmethod
    def scan_all_tcp_ports(project):
        arr = NmapCommands.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                fn = NmapCommands.get_safe_filename(host.get_folder_name(), NmapCommands._tcp_all_ports_flags, ip)
                NmapCommands.nmap_scan_add(host, fn, NmapCommands._tcp_all_ports_flags, ip)

    @staticmethod
    def scan_full_tcp_ports(project):
        arr = NmapCommands.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                flags = NmapCommands._tcp_all_options_flags
                flags += host.get_tcp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_tcp_services_' + ip + '.txt'
                NmapCommands.nmap_scan_add(host, fn, NmapCommands._tcp_all_options_flags, ip)

    @staticmethod
    def scan_full_udp_ports(project):
        arr = NmapCommands.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                flags = NmapCommands._udp_all_options_flags
                flags += host.get_udp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_udp_services_' + ip + '.txt'
                NmapCommands.nmap_scan_add(host, fn, NmapCommands._udp_all_options_flags, ip)

    @staticmethod
    def scan_all_ports(project):
        arr = NmapCommands.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                # UDP
                fn = NmapCommands.get_safe_filename(host.get_folder_name(), NmapCommands._udp_flags, ip)
                NmapCommands.nmap_scan_add(host, fn, NmapCommands._udp_flags, ip)
                # TCP All ports
                fn = NmapCommands.get_safe_filename(host.get_folder_name(), NmapCommands._tcp_all_ports_flags, ip)
                NmapCommands.nmap_scan_add(host, fn, NmapCommands._tcp_all_ports_flags, ip)
                # fn = host.get_folder_name() + '/masscan_all_tcp.txt'
                # NmapCommands.run_masscan(host, ip, fn)
                # UDP Version scanning
                flags = NmapCommands._udp_all_options_flags
                flags += host.get_udp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_udp_services_' + ip + '.txt'
                NmapCommands.nmap_scan_add(host, fn, flags, ip)
                # TCP Version scanning
                flags = NmapCommands._tcp_all_options_flags
                flags += host.get_tcp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_tcp_services_' + ip + '.txt'
                NmapCommands.nmap_scan_add(host, fn, flags, ip)

    @staticmethod
    def scan_all_ports_paralel(project):
        arr = NmapCommands.prompt_hosts(project)
        i = 0
        ps = list()
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                # UDP
                fn = NmapCommands.get_safe_filename(host.get_folder_name(), NmapCommands._udp_flags, ip)
                cmd = 'nmap %s %s' % (NmapCommands._udp_flags, ip)
                pudp = Runner.run(cmd, fn)
                tup = (i, fn, pudp)
                i += 1
                ps.append(tup)
                cmd = 'nmap %s %s' % (NmapCommands._tcp_all_ports_flags, ip)
                ptcp = Runner.run(cmd, fn)
                tup = (i, fn, ptcp)
                i += 1
                ps.append(tup)
                # wait for both to be done
                while len(ps) > 0:
                    for tup in ps:
                        pr = tup[2]
                        if pr.poll() is not None:
                            NmapCommands.add_ports_to_host(tup[1], host)
                            ps.remove(tup)
                    print '.'
                    time.sleep(5)

                Console.inform('Done with the long nmap scans')
                # UDP Version scanning
                flags = NmapCommands._udp_all_options_flags
                flags += host.get_udp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_udp_services_' + ip + '.txt'
                cmd = 'nmap %s %s' % (flags, ip)
                pudp = Runner.run(cmd, fn)
                tup = (i, fn, pudp)
                print 'Adding udp nmap scan'
                i += 1
                ps.append(tup)
                # TCP Version scanning
                flags = NmapCommands._tcp_all_options_flags
                flags += host.get_tcp_ports_as_string()
                fn = host.get_folder_name() + '/nmap_tcp_services_' + ip + '.txt'
                cmd = 'nmap %s %s' % (flags, ip)
                ptcp = Runner.run(cmd, fn)
                tup = (i, fn, ptcp)
                i += 1
                ps.append(tup)
                print 'Adding tcp nmap scan'
                # wait for both to be done
                while len(ps) > 0:
                    for tup in ps:
                        pr = tup[2]
                        if pr.poll() is not None:
                            NmapCommands.add_ports_to_host(tup[1], host)
                            ps.remove(tup)
                    print '.'
                    time.sleep(5)

    @staticmethod
    def get_ips_from_sn_pe(fn):
        ips = []
        with open(fn, 'r') as f:
            for line in f:
                if 'up' in line.lower():
                    line_ips = re.findall(NmapCommands._ip_regex, line)
                    if len(line_ips) > 0:
                        for ip in line_ips:
                            ips.append(ip)
        return ips

    @staticmethod
    def scan_all_tcp_ports_masscan(project):
        arr = NmapCommands.prompt_hosts(project)
        for ip in arr:
            host = project.get_host_from_ip(ip)
            if host is not None:
                fn = host.get_folder_name() + '/masscan_all_tcp.txt'
                NmapCommands.run_masscan(host, ip, fn)

    @staticmethod
    def run_masscan(host, ip, filename):
        cmd = 'masscan %s -p1-65535 -oL %s' % (ip, filename)
        proc = Runner.run(cmd)
        proc.communicate()

        # Read ports from file
        ps = list()
        with open(filename, 'r') as f:
            for line in f:
                if line.find('open') >= 0:
                    arr = line.split(' ')
                    po = Port(host=host, port_num=arr[2], status=arr[0], service='', version='')
                    ps.append(po)
        for po in ps:
            host.add_port(po)
        host.write_ports_to_file()


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
    def run_webscans(project): # evidence_folder, host, port='80'):
        ip_list = WebCommands.prompt_hosts(project)
        for i in ip_list:
            a = i.split(':')
            h = a[0]
            p = a[1]
            port = project.get_port_from_ip_port_num(ip=h, port_num=p)
            if port is not None:
                FolderCreator.create_port_folder(port)
                fn = port.get_folder_name() + '/whatweb.txt'
                WebCommands.whatweb(url=i, filename=fn)
                fn = port.get_folder_name() + '/nikto'
                WebCommands.nikto(host=h, port=p, filename=fn)
                fn = port.get_folder_name() + '/dirsearch'
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
        if '' == ext:
            ext = 'htm'
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


class FtpCommands(object):

    @staticmethod
    def prompt_hosts(project):
        str_list = list()
        for host in project.hosts:
            for port in host.ports:
                if 'ftp' == port.service: # or 'tftp' == port.service.lower():
                    str_list.append(host.ip + ':' + port.port_num[:-4])
        Console.inform('The following FTP ports were found:')
        for s in str_list:
            Console.inform('\t%s' % s)

        a = Console.prompt('Do you want to run web scans on all of these (Y/N)? [y]')
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
    def run_ftpscans(project):
        ip_list = FtpCommands.prompt_hosts(project)
        for i in ip_list:
            print i
            a = i.split(':')
            h = a[0]
            p = a[1]
            host = project.get_host_from_ip(h)
            if host is not None:
                print '.'

    @staticmethod
    def run_nmap_scripts(project):
        ip_list = FtpCommands.prompt_hosts(project)
        for i in ip_list:
            print i
            a = i.split(':')
            h = a[0]
            p = a[1]
            host = project.get_host_from_ip(h)
            if host is not None:
                fn = host.get_folder_name() + '/nmap_ftp_' + p + '.txt'
                FtpCommands.nmap_scripts(host=h, port=p, filename=fn)

    @staticmethod
    def nmap_scripts(host, port, filename):
        cmd = 'nmap -Pn -n -sV --script=ftp-anon,ftp-bounce,ftp-libopie,ftp-proftpd-backdoor,' + \
              'ftp-vsftpd-backdoor,ftp-vuln-cve2010-4221 -p %s %s' % (port, host)
        p = Runner.run(cmd, filename)
        out, err = p.communicate()

    @staticmethod
    def run_hydra_ftp(project):
        ip_list = FtpCommands.prompt_hosts(project)
        for i in ip_list:
            print i
            a = i.split(':')
            h = a[0]
            p = a[1]
            host = project.get_host_from_ip(h)
            if host is not None:
                fn = host.get_folder_name() + '/hydra_ftp_' + p + '.txt'
                ulfn = project.get_userlist_file_name()
                pwf = Runner.check_password_file(project)
                FtpCommands.hydra_ftp(host=h, port=p, userlist_filename=ulfn, password_filename=pwf, output_filename=fn)

    @staticmethod
    def hydra_ftp(host, port, userlist_filename, password_filename, output_filename):
        cmd = 'hydra -u -f -L %s -P %s -o %s %s -s %s ftp' \
              % (userlist_filename, password_filename, output_filename, host, port)
        p = Runner.run(cmd)
        out, err = p.communicate()


class DnsCommands(object):
    @staticmethod
    def get_safe_filename(filename):
        return filename.replace(':', '_')

    @staticmethod
    def prompt_hosts(project):
        str_list = list()
        for host in project.hosts:
            for port in host.ports:
                if 'domain' == port.service and (port.port_num.find("tcp") > 0):
                    str_list.append(host.ip + ':' + port.port_num)
        Console.inform('The following DNS ports were found:')
        for s in str_list:
            Console.inform('\t%s' % s)

        a = Console.prompt('Do you want to run web scans on all of these (Y/N)? [y]')
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
    def run_dnsscans(project):
        ip_list = DnsCommands.prompt_hosts(project)
        for i in ip_list:
            a = i.split(':')
            h = a[0]
            p = a[1]
            port = project.get_port_from_ip_port_num(ip=h, port_num=p)
            if port is not None:
                FolderCreator.create_port_folder(port)
                fn = port.get_folder_name() + '/nmblookup.txt'
                DnsCommands.nmblookup(ip=h, filename=fn)
                fn = port.get_folder_name() + '/zone_transfer.txt'
                DnsCommands.zone_transfer(ip=h, filename=fn)

    @staticmethod
    def nmblookup(ip, filename):
        cmd = 'nmblookup -A %s' % ip
        p = Runner.run(cmd, filename)
        out, err = p.communicate()

    @staticmethod
    def zone_transfer(ip, filename):
        cmd = 'dig %s.thinc.local thinc.local axfr' % ip
        p = Runner.run(cmd, filename)
        out, err = p.communicate()

        class DnsCommands(object):
            @staticmethod
            def get_safe_filename(filename):
                return filename.replace(':', '_')

            @staticmethod
            def prompt_hosts(project):
                str_list = list()
                for host in project.hosts:
                    for port in host.ports:
                        if 'domain' == port.service and (port.port_num.find("tcp") > 0):
                            str_list.append(host.ip + ':' + port.port_num)
                Console.inform('The following DNS ports were found:')
                for s in str_list:
                    Console.inform('\t%s' % s)

                a = Console.prompt('Do you want to run web scans on all of these (Y/N)? [y]')
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
            def run_dnsscans(project):
                ip_list = DnsCommands.prompt_hosts(project)
                for i in ip_list:
                    print i
                    a = i.split(':')
                    h = a[0]
                    p = a[1]
                    print '^^^^ %s:%s' % (h, p)
                    port = project.get_port_from_ip_port_num(ip=h, port_num=p)
                    if port is not None:
                        fn = port.get_folder_name() + '/nmblookup.txt'
                        print fn
                        DnsCommands.nmblookup(ip=h, filename=fn)
                        fn = port.get_folder_name() + '/zone_transfer.txt'
                        DnsCommands.zone_transfer(ip=h, filename=fn)

            @staticmethod
            def nmblookup(ip, filename):
                cmd = 'nmblookup -A %s' % ip
                p = Runner.run(cmd, filename)
                out, err = p.communicate()


class SmbCommands(object):

    @staticmethod
    def prompt_hosts(project):
        str_list = list()
        for host in project.hosts:
            for port in host.ports:
                if 'netbios-ssn' == port.service and (port.port_num.find("tcp") > 0):
                    str_list.append(host.ip + ':' + port.port_num)
        Console.inform('The following SMB ports were found:')
        for s in str_list:
            Console.inform('\t%s' % s)

        a = Console.prompt('Do you want to run web scans on all of these (Y/N)? [y]')
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
    def run_smbscans(project):
        ip_list = SmbCommands.prompt_hosts(project)
        for i in ip_list:
            a = i.split(':')
            h = a[0]
            p = a[1]
            port = project.get_port_from_ip_port_num(ip=h, port_num=p)
            if port is not None:
                FolderCreator.create_port_folder(port)
                fn = port.get_folder_name() + '/enum4linux.txt'
                SmbCommands.enum4linux(ip=h, filename=fn)

    @staticmethod
    def enum4linux(ip, filename):
        cmd = 'enum4linux %s' % ip
        p = Runner.run(cmd, filename)
        out, err = p.communicate()

# This method used for testing
if __name__ == '__main__':
    print ''
    p = Project()
    p.add_host('192.168.56.104')
    NmapCommands.scan_all_ports_paralel(p)

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
    #
    # FtpCommands.run_nmap_scripts('192.168.56.102', '21', 'nmap_tst')
