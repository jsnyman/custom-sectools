#!/usr/bin/env python
import sys
from console import Console
from runner import NmapScans
from runner import WebCommands
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
        print '     3. Web scans'
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
    print '     1. Use nmap \'liveness\' scan (-sn -PE)'
    print '     2. Read existing from files (have you done this before?)'
    print '     99. Return'
    print ''
    a = Console.prompt('What\'ll it be sweetheart? ')

    if a == '1':
        NmapScans.scan_for_live_hosts(p)
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
        print '     2. UDP Scan (-sUV -f)'
        print '     3. TCP Full Scan (-p-)'
        print '     4. TCP Scan Services, known ports (-sS -A -p [TCP Ports])'
        print '     5. UDP Scan Services, known ports (-sU -A -p [UDP Ports])'
        print '     99. Return'
        print ''
        a = Console.prompt('What\'ll it be sweetheart? ')

        if '1' == a:
            NmapScans.scan_all_ports(project)
        elif a == '2':
            NmapScans.scan_udp(project)
        elif a == '3':
            NmapScans.scan_all_tcp_ports(project)
        elif a == '4':
            NmapScans.scan_full_tcp_ports(project)
        elif a == '5':
            NmapScans.scan_full_udp_ports(project)
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



