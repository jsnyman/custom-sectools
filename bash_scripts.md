To cat a hostname file and do a DNS lookup on the resultant hostname:

```
for host in $(cat [FILENAME]); do echo $host: $(dig +short -t ANY $host.[DOMAIN_NAME] @[NAMESERVER_OF_KNOWN]); done
```
