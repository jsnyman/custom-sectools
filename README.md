# This is a test



### General

* Add user - [https://www.windows-commandline.com/add-user-from-command-line/](https://www.windows-commandline.com/add-user-from-command-line/) `net user [username] [password] /ADD`
* Add user to Admin group `net localgroup Administrators [username] /add`
* List all services `> sc queryex type= service state= all` OR `> net start` OR `$ wmic service list brief --> lists all services`
* Command to stop a service: `net stop servicename`

