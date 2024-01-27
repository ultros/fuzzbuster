#!/usr/bin/env python3.11
from termcolor import colored
import argparse
import concurrent.futures
import logging
import os
import random
import re
from datetime import datetime as dt
from typing import Tuple
import requests
import Core.settings
from pathlib import Path

logging.basicConfig(filename="log.txt", encoding='utf-8', level=logging.INFO, format='')


def format_url(url: str, keyword: str) -> None | str:
    """Returns a formatted URL to fuzz/directory bust."""
    try:
        if re.search("FUZZ", url):
            url = url.replace("FUZZ", keyword.strip())
        else:
            print('[!] Could not find the "FUZZ" string. E.g. "http://preprod-FUZZ.trick.htb"')
            return

    except Exception as e:
        print(e)

    return url


def prepare_wordlist(url: str, wordlist: str) -> Tuple[list, list, int]:
    """Returns valid URLs, a total of all words, and a list of invalid words discovered in the wordlist."""
    urls = []
    badwords = []

    assert os.path.exists(wordlist)
    file = open(wordlist, 'r')

    try:
        for word in file:
            temp_url = format_url(url, word)
            if temp_url is None:
                exit(1)
            urls.append(temp_url)

    except Exception as e:
        badwords.append(word)

    total_urls = len(urls)
    print(f"Total URLs to fuzz: {total_urls}")
    print(f"Total invalid words in wordlist: {len(badwords)}")

    return urls, badwords, total_urls


def process_host(host: str, url: str) -> str | None:
    if Core.settings.CUSTOM_USER_AGENT:
        headers = {'Host': host, 'User-Agent': Core.settings.CUSTOM_USER_AGENT}
    else:
        headers = {'Host': host, 'User-Agent': random.choice(Core.settings.UserAgents.user_agents)}

    try:
        res = requests.get(url, headers=headers, timeout=1, verify=False, allow_redirects=True)

        if re.search("File not found", res.text):
            return
        if re.search("Error 404", res.text):
            return
        if re.search("status=404", res.text) and re.search("Whitelabel Error Page", res.text):
            # Spring boot 404 with default content
            return
        if res.status_code == 200:
            if str(len(res.content)) in Core.settings.PAGE_SIZE:
                return
            else:
                print(f"[200]: {host} [Size: {len(res.content)}]")
        elif res.status_code == 404 and re.search('{"status": "running"}', res.text):
            # handle Amazon S3 (s3.example.com) 404
            print(f"404 - {host}")

    except Exception as e:
        # print(e)
        return




def fuzz_subdomains(hostname: str, url: str, wordlist: str) -> None:
    valid_response_list = []
    i = 0

    if re.search("^http", hostname):
        print('Remove "http://" or "https://" from hostname.')
        exit(1)

    if not re.search("^http", url):
        print("Ensure your --URL/-u begins with http or https.")
        exit(1)

    hosts = prepare_wordlist(hostname, wordlist)
    requests.packages.urllib3.disable_warnings()
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = []

        for host in hosts[0]:
            futures.append(executor.submit(process_host, host=host, url=url))

        try:
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res is not None:
                    valid_response_list.append(res)
                    print(f"{res}")

                i += 1
                print(f"{i} of {len(hosts[0])}", end="\r")

        except Exception as e:
            i += 1

        assert type(valid_response_list) == list
        logging.info(
            f"({dt.now()} {hostname}) {len(valid_response_list)} resolved subdomains/vhosts returned from {len(hosts[0])}"
            f" total entries.")

        for url in valid_response_list:
            logging.info(f" -  {url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Subdomain Finder (E.g. FUZZ.google.com)")

    parser.add_argument('--host', required=True, type=str,
                        default=None, dest="host",
                        help="Specify hostname (E.g. preprod-FUZZ.trick.htb)")

    parser.add_argument('-u', '--url', required=True, type=str,
                        default=None, dest="url",
                        help="Specify URL or IP Address of Server")

    parser.add_argument('-w', '--wordlist', required=True, type=str,
                        default=None,
                        help='Specify wordlist to use (e.g. /usr/share/wordlists/dirb/big.txt)')

    parser.add_argument('--custom_user_agent', required=False, dest='custom_user_agent',
                        help='Add a custom user agent to your queries.')

    parser.add_argument("--size", required=False, nargs='+',
                        default=[None], dest="page_size",
                        help='Page sizes to ignore (--size 15 2010 8)')

    args = parser.parse_args()

    if args.page_size:
        Core.settings.PAGE_SIZE = args.page_size

    if args.custom_user_agent:
        Core.settings.CUSTOM_USER_AGENT = args.custom_user_agent

    if args.url is not None:
        url = args.url

    if (args.wordlist is not None) and (os.path.isfile(args.wordlist)):
        wordlist = args.wordlist
    else:
        print(f"[!] Invalid wordlist")
        exit(1)

    if args.host is not None:
        host = args.host

    print(f"""
    SETTINGS VERIFICATION
    {colored(f"[+] Host set to: {host}", "red")}
    {colored(f"[+] URL set to: {url}", "yellow")}
    {colored(f"[+] Wordlist set to: {Path.absolute(Path(wordlist))}", "yellow")}
    {colored(f"[+] Custom User-Agent: {Core.settings.CUSTOM_USER_AGENT}", "red")}
    """)

    answer = input("[?] Does this look correct (Y/n) > ") or "y"
    if not answer.lower() == "y":
        exit(0)

    fuzz_subdomains(host, url, wordlist)


if __name__ == '__main__':
    main()
