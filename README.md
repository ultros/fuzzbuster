# fuzzbuster
Concurrent URL fuzzer and directory buster (i.e. parameters, queries, and directories).

### Query:

#### $ python3 fuzzbuster.py -u https://www.google.com/search?q=FUZZ -w /usr/share/wordlists/dirb/small.txt

    Total URLs to fuzz: 961  
    Total invalid words in wordlist: 0  
    [200] Discovered: https://www.google.com/search?q=00  
    [200] Discovered: https://www.google.com/search?q=0  
    [200] Discovered: https://www.google.com/search?q=20  
    [200] Discovered: https://www.google.com/search?q=1  
 
...

### Subdomain/VirtualHost:

#### $ python3 subdomainfuzzbuster.py --host "preprod-FUZZ.trick.htb" -u http://trick.htb -w /usr/share/wordlists/dirb/small.txt

    Total URLs to fuzz: 961  
    Total invalid words in wordlist: 0  
    Found preprod-marketing.trick.htb - 200  
    Found preprod-payroll.trick.htb - 200  

...

![vhost-emuneration-subdomain-fuzzbuster](https://user-images.githubusercontent.com/2483361/205157196-994fff4e-6925-414c-820c-1102657a0c39.gif)

---

### Log Generation

    $ cat log.txt  
    (2022-12-01 14:38:52.461914 http://###.com/FUZZ) 5 resolved URLs returned from 961 total URL entries.
     -  [200] Discovered: http://###.com/marketing
     -  [200] Discovered: http://###.com/archive
     -  [403] Forbidden: http://###.com/javascript
    ...

    $ cat log.txt
    (2022-12-01 14:47:56.278808 FUZZ.google.com) 9 resolved subdomains/vhosts returned from 961 total entries.
     -  Discovered subdomain: code.google.com
     -  Discovered subdomain: developers.google.com 
     -  Discovered subdomain: files.google.com
     -  Discovered subdomain: images.google.com 
    ...

---  

### Report Export  

![image](https://user-images.githubusercontent.com/2483361/193124127-3c259e17-1479-4cb2-b847-23355aff31ff.png)