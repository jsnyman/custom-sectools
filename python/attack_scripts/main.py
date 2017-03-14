#!/usr/bin/env python
import sys
from console import Console
from runner import FtpCommands, NmapCommands, WebCommands, DnsCommands, SmbCommands
from objects import Project


def main_menu():
    c = ''
    while c != '99':
        print ''
        print '========================================'
        print '            Main hecking menu'
        print '========================================'
        print ''
        if p.hosts and len(p.hosts) > 0:
            print 'Current number of hosts: %i' % len(p.hosts)
        else:
            print 'Currently no hosts added'
        print ''
        print '     1. Add targets'
        print '     2. Port scans'
        print '     3. Web [80/443]'
        print '     4. FTP [21]'
        print '     5. SSH [22]'
        print '     6. DNS [53]'
        print '     7. SMB [139]'
        print '     8. MySQL [3306]'
        print '     80. Configure'
        print '     98. Print'
        print '     99. Quit'
        print ''
        c = Console.prompt('What\'ll it be sweetheart? ')
        # main_menu_items[c]()

        if c == '1':
            add_targets(p)

        elif c == '2':
            manual_port_scans(p)

        elif c == '3':
            web_scans(p)

        elif c == '4':
            ftp_scans(p)

        elif c == '5':
            Console.prompt('No brute forcing implemented')

        elif c == '6':
            dns_scans(p)

        elif c == '7':
            smb_scans(p)

        elif c == '80':
            configure(p)

        elif c == '98':
            print p

        elif c == '99':
            exit_stage()

        else:
            print ''
            print 'Christ guy, there are only so many choices, get it right'
            print ''


def add_targets(project):
    print ''
    print '========================================'
    print '              Add targets'
    print '========================================'
    print ''
    print '     1. Use nmap \'liveness\' scan (-sn + -sn -PE)'
    print '     2. Read existing from files (have you done this before?)'
    print '     99. Return'
    print ''
    a = Console.prompt('What\'ll it be sweetheart? ')

    if a == '1':
        NmapCommands.scan_for_live_hosts(p)
    elif a == '2':
        Project.read_existing_from_file(project)


def manual_port_scans(project):
    a = ''
    while a != '99':
        print ''
        print '========================================'
        print '           Port Scans'
        print '========================================'
        print ''
        print '     1. Full scan (all scans below)'
        print '     2. TCP Quick Scan (top 1000 ports)'
        print '     3. UDP Scan (-sUV -f)'
        print '     4. TCP Full Scan (-p-)'
        print '     5. TCP Scan Services, known ports (-sS -A -p [TCP Ports])'
        print '     6. UDP Scan Services, known ports (-sU -A -p [UDP Ports])'
        print '     99. Return'
        print ''
        a = Console.prompt('What\'ll it be sweetheart? ')

        if '1' == a:
            # NmapCommands.scan_all_ports(project)
            NmapCommands.scan_all_ports_paralel(project)
        elif a == '2':
            # NmapCommands.scan_quick_tcp(project)
            NmapCommands.scan_quick_tcp_paralel(project)
        elif a == '3':
            #NmapCommands.scan_udp(project)
            NmapCommands.scan_udp_paralel(project)
        elif a == '4':
            NmapCommands.scan_all_tcp_ports_masscan(project)
        elif a == '5':
            NmapCommands.scan_full_tcp_ports(project)
        elif a == '6':
            NmapCommands.scan_full_udp_ports(project)
        elif a == '99':
            return

        else:
            print 'Nee fok, ek weet nie wat jy soek nie'


def web_scans(project):
    a = ''
    while a != '99':
        print ''
        print '========================================'
        print '            Web Scans'
        print '========================================'
        print ''
        print '     1. Automagic scan'
        print '     2. Manual WhatWeb Scan'
        print '     3. Manual Nikto Scan'
        print '     4. Manual DirSearch'
        print '     99. Quit'
        print ''
        a = Console.prompt('What\'ll it be sweetheart? ')

        if a == '1':
            WebCommands.run_webscans(project)
        elif a == '2':
            WebCommands.run_whatweb(project)
        elif a == '3':
            WebCommands.run_nikto(project)
        elif a == '4':
            WebCommands.run_dirsearch(project)
        elif a == '99':
            return


def ftp_scans(project):
    a = ''
    while a != '99':
        print ''
        print '========================================'
        print '            FTP Scans'
        print '========================================'
        print ''
        print '     1. Automagic scan'
        print '     2. Manual nmap FTP Scan'
        print '     3. Manual FTP brute force'
        print '     99. Quit'
        print ''
        a = Console.prompt('What\'ll it be sweetheart? ')

        if a == '1':
            FtpCommands.run_ftpscans(project)
        elif a == '2':
            FtpCommands.run_nmap_scripts(project)
        elif a == '3':
            FtpCommands.run_hydra_ftp(project)
        elif a == '99':
            return


def dns_scans(project):
    a = ''
    while a != '99':
        print ''
        print '========================================'
        print '            DNS Scans'
        print '========================================'
        print ''
        print '     1. Automagic scan'
        print '     2. Manual nmblookup'
        print '     3. Manual zone transfer'
        print '     99. Quit'
        print ''
        a = Console.prompt('What\'ll it be sweetheart? ')

        if a == '1':
            DnsCommands.run_dnsscans(project)
        elif a == '2':
            Console.inform('Not implemented')
        elif a == '3':
            Console.inform('Not implemented')
        elif a == '99':
            return


def smb_scans(project):
    a = ''
    while a != '99':
        print ''
        print '========================================'
        print '            SMB Scans'
        print '========================================'
        print ''
        print '     1. Automagic scan'
        print '     2. Manual enum4linux'
        print '     99. Quit'
        print ''
        a = Console.prompt('What\'ll it be sweetheart? ')

        if a == '1':
            SmbCommands.run_smbscans(project)
        elif a == '2':
            Console.inform('Not implemented')
        elif a == '99':
            return


def configure(project):
    a = ''
    while a != '99':
        print ''
        print '========================================'
        print '           Configure'
        print '========================================'
        print ''
        print '     1. Set password file'
        print '     2. ddd'
        print '     3. ddd'
        print '     99. Return'
        print ''
        a = Console.prompt('What\'ll it be sweetheart? ')

        if '1' == a:
            project.password_file = Console.prompt('Enter the password file name:')
        elif a == '2':
            print 'ddd'
        elif a == '3':
            print 'ddd'
        elif a == '99':
            return
        else:
            print 'Nee fok, ek weet nie wat jy soek nie'


def exit_stage():
    Console.inform('Nag ou grote, catch ya ona flipside')


if __name__ == '__main__':
    path = ''
    if len(sys.argv) > 1:
        path = sys.argv[1]
    # Set up project first
    p = Project(path)
    # Now display and choose main menu items
    main_menu()



