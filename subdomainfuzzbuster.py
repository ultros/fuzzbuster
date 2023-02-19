#!/usr/bin/env python3.11

import argparse
import concurrent.futures
import logging
import os
import re
from datetime import datetime as dt
from typing import Tuple

import requests

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
    headers = {'Host': host}
    try:
        res = requests.get(url, headers=headers, timeout=1)
        origin_response = requests.get(url, timeout=1)

        if res.status_code == 200:
            if len(origin_response.text) != len(res.text):
                return f"Discovered subdomain: {host}"

        if res.status_code == 404 and re.search('{"status": "running"}', res.text):
            # handle Amazon S3 (s3.example.com) 404
            print(f"404 - {host}")

    except Exception as e:
        return


def fuzz_subdomains(hostname: str, url: str, wordlist: str) -> None:
    valid_response_list = []
    i = 0

    if re.search("^http", hostname):
        print('Remove "http://" or "https://" from hostname.')
        exit(2)

    if not re.search("^http", url):
        print("Ensure your --URL/-u begins with http or https.")
        exit(2)

    hosts = prepare_wordlist(hostname, wordlist)

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

    args = parser.parse_args()

    if args.url is not None:
        url = args.url

    if (args.wordlist is not None) and (os.path.isfile(args.wordlist)):
        wordlist = args.wordlist
    else:
        print(f"[!] Invalid wordlist")
        exit(2)

    if args.host is not None:
        host = args.host

    fuzz_subdomains(host, url, wordlist)


if __name__ == '__main__':
    main()
