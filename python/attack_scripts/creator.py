#!/usr/bin/env python

import sys
import os

from console import Console


class FolderCreator(object):

    @staticmethod
    def create_project_structure(path):
        Console.inform('Creating the project structure')
        # Create the main folder if not already present
        if not os.path.exists(path):
            Console.add('Creating %s' % path)
            os.makedirs(path)
        else:
            Console.inform('%s already exists' % path)
        # Create the subfolders
        evpath = path + '/evidence'
        if not os.path.exists(evpath):
            Console.add('Creating %s' % evpath)
            os.makedirs(evpath)
        else:
            Console.inform('%s already exists' % evpath)
        # repath = path + '/received'
        # if not os.path.exists(repath):
        #     Console.add('Creating %s' % repath)
        #     os.makedirs(repath)
        # else:
        #     Console.inform('%s already exists' % repath)
        # Create the main notes.md & write first lines
        notespath = path + '/notes.md'
        if not os.path.exists(notespath):
            with open(notespath, 'w') as f:
                f.write("# %s\n" % path)
                f.write("\n")
                f.write("## Hosts:\n")
            Console.add('Creating %s' % notespath)
        else:
            Console.inform('%s already exists' % notespath)
        userlist_path = path + '/users.txt'
        if not os.path.exists(userlist_path):
            with open(userlist_path, 'w') as f:
                f.write("\n")
                f.write("admin\n")
                f.write("root\n")
            Console.add('Creating %s' % userlist_path)
        else:
            Console.inform('%s already exists' % userlist_path)
        Console.inform('Project structure created: %s/' % path)

    @staticmethod
    def create_host_folder(host):
        Console.inform('Creating the host folder structure')
        path = host.get_folder_name()
        if not os.path.exists(path):
            Console.add('Creating %s' % path)
            os.makedirs(path)
        else:
            Console.inform('%s already exists' % path)
        # Create the main notes.md & write first lines
        notespath = path + '/notes.md'
        if not os.path.exists(notespath):
            Console.add('Creating %s' % notespath)
            with open(notespath, 'w') as f:
                f.write("# %s\n" % host.ip)
                f.write("\n")
                f.write("\n")
                f.write("## Ports\n")
        else:
            Console.inform('%s already exists' % notespath)
        # Create ports.txt file
        portspath = path + '/ports.txt'
        if not os.path.exists(portspath):
            Console.add('Creating %s' % portspath)
            with open(portspath, 'w') as f:
                f.write("")

        Console.inform('Host folder structure created: %s/' % path)

    @staticmethod
    def create_port_folder(port):
        print '##################################'
        print 'Creating the folder for the port'
        path = port.get_folder_name()
        if not os.path.exists(path):
            Console.add('Creating %s' % path)
            os.makedirs(path)
        else:
            Console.inform('%s already exists' % path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s [test_name]" % sys.argv[0]
        print "The default path is ."
        exit(1)

    # Get the test name
    name = sys.argv[1]
    #
    # # Create the main folder structure and initial files
    # FolderCreator.create_project_structure(name)
