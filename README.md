# fuzzbuster
Concurrent URL fuzzer and directory buster (i.e. parameters, queries, directories, and files).

$ python3 fuzzbuster.py

        ██████                                   █████                         █████                      
       ███░░███                                 ░░███                         ░░███                       
      ░███ ░░░  █████ ████  █████████  █████████ ░███████  █████ ████  █████  ███████    ██████  ████████ 
     ███████   ░░███ ░███  ░█░░░░███  ░█░░░░███  ░███░░███░░███ ░███  ███░░  ░░░███░    ███░░███░░███░░███
    ░░░███░     ░███ ░███  ░   ███░   ░   ███░   ░███ ░███ ░███ ░███ ░░█████   ░███    ░███████  ░███ ░░░ 
      ░███      ░███ ░███    ███░   █   ███░   █ ░███ ░███ ░███ ░███  ░░░░███  ░███ ███░███░░░   ░███     
      █████     ░░████████  █████████  █████████ ████████  ░░████████ ██████   ░░█████ ░░██████  █████    
     ░░░░░       ░░░░░░░░  ░░░░░░░░░  ░░░░░░░░░ ░░░░░░░░    ░░░░░░░░ ░░░░░░     ░░░░░   ░░░░░░  ░░░░░     

    usage: fuzzbuster.py [-h] [-u URL] [-w WORDLIST] [--pdf PDF] [--html HTML] [--json JSON] [--size PAGE_SIZE [PAGE_SIZE ...]] [--get_proxies] [-sc SESSION_COOKIE] [-cua CUSTOM_USER_AGENT] [-v]

    Concurrent directory buster, parameter, and query fuzzer.

    options:
      -h, --help            show this help message and exit
      -u URL, --url URL     Specify URL to fuzz (e.g. www.google.com/search?q=FUZZ
      -w WORDLIST, --wordlist WORDLIST
                            Specify wordlist to use (e.g. /usr/share/wordlists/dirb/commmon.txt)
      --pdf PDF             Specify PDF report name
      --html HTML           Specify HTML report name
      --json JSON           Specify report name
      --size PAGE_SIZE [PAGE_SIZE ...]
                            Page sizes to ignore (--size 15 2010 8)
      --get_proxies         Gather socks4/socks5 elite proxies.
      -sc SESSION_COOKIE    Specify a session cookie.
      -cua CUSTOM_USER_AGENT
                            Set a custom user agent.
      -v, --version         Display software version.

...

## Basic Usage

### Directory/File Query:
    $ fuzzbuster.py -u http://soccer.htb/FUZZ -w /usr/share/wordlists/dirb/small.txt --size 1,23 -cua "test" 

    SETTINGS VERIFICATION
    [+] URL set to: https://soccer.htb/FUZZ
    [+] Wordlist set to: /usr/share/wordlists/dirb/small.txt
    [+] Session Cookie: {}
    [+] Custom User-Agent: test
    [+] Page size(s) to ignore: 1,23
  
    [?] Does this look correct (Y/n) > 

...

### Subdomain/VirtualHost:
    $ subdomainfuzzbuster.py --host FUZZ.soccer.htb -u http://soccer.htb -w /usr/share/wordlists/dirb/big.txt

    SETTINGS VERIFICATION
    [+] Host set to: FUZZ.soccer.htb
    [+] URL set to: http://soccer.htb
    [+] Wordlist set to: /usr/share/wordlists/dirb/big.txt
    [+] Custom User-Agent: None
    
    [?] Does this look correct (Y/n) > y

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