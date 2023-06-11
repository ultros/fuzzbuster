#!/usr/bin/env python3.11

__version__ = "1.0.0"
__author__ = "Jesse Shelley"
__email__ = "realjesseshelley@gmail.com"

import argparse
import concurrent.futures
import logging
import os
import sys
from pathlib import Path
from datetime import datetime as dt
from termcolor import colored
import Core.network
import Core.process
import Core.reports
import Core.settings

logging.basicConfig(filename="log.txt", encoding='utf-8', level=logging.INFO, format='')


def print_banner():
    banner = [
        """
    ██████                                   █████                         █████                      
   ███░░███                                 ░░███                         ░░███                       
  ░███ ░░░  █████ ████  █████████  █████████ ░███████  █████ ████  █████  ███████    ██████  ████████ 
 ███████   ░░███ ░███  ░█░░░░███  ░█░░░░███  ░███░░███░░███ ░███  ███░░  ░░░███░    ███░░███░░███░░███
░░░███░     ░███ ░███  ░   ███░   ░   ███░   ░███ ░███ ░███ ░███ ░░█████   ░███    ░███████  ░███ ░░░ 
  ░███      ░███ ░███    ███░   █   ███░   █ ░███ ░███ ░███ ░███  ░░░░███  ░███ ███░███░░░   ░███     
  █████     ░░████████  █████████  █████████ ████████  ░░████████ ██████   ░░█████ ░░██████  █████    
 ░░░░░       ░░░░░░░░  ░░░░░░░░░  ░░░░░░░░░ ░░░░░░░░    ░░░░░░░░ ░░░░░░     ░░░░░   ░░░░░░  ░░░░░     
"""
    ]
    for line in banner:
        print(colored(line, 'cyan', attrs=['bold']))


print_banner()

@Core.settings.fuzz_time
def fuzz(url: str, wordlist: str) -> list:
    original_fuzzer_url = url
    networking = Core.network.Network()
    processing = Core.process.Process(wordlist)
    formatted_url_list = processing.format_wordlist(url)

    total_urls = 0
    i = 0
    valid_response_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=Core.settings.Settings.max_workers) as executor:
        futures = []

        for url in formatted_url_list:
            futures.append(executor.submit(networking.perform_request, url))
            total_urls += 1
            print(f"Total URLs: {total_urls}...", end="\r")

        for future in concurrent.futures.as_completed(futures):
            response = future.result()

            if response is not None:
                valid_response_list.append(response)
                print(f"{response}")

            i += 1
            print(end='\x1b[2K')
            print(f"{i} of {total_urls}", end="\r")  # to end of line

        assert type(valid_response_list) == list
        logging.info(
            f"{dt.now()} ({original_fuzzer_url}) {len(valid_response_list)} resolved URLs returned from {total_urls}"
            f" total URL entries.")

        for url in valid_response_list:
            logging.info(f" -  {url}")

        for url in networking.retry_addresses:
            logging.info(f"[!] Failed to connect: {url}")
            print(f"[!] Failed to connect: {url}")

    return valid_response_list


def main():
    parser = argparse.ArgumentParser(description="Concurrent directory, parameter, and query fuzzer.")
    parser.add_argument('-u', '--url', required=False, type=str,
                        default=None, dest="url",
                        help="Specify URL to fuzz (e.g. www.google.com/search?q=FUZZ")
    parser.add_argument('-w', '--wordlist', required=False, type=str,
                        default=None, dest="wordlist",
                        help='Specify wordlist to use (e.g. /usr/share/wordlists/dirb/commmon.txt)')
    parser.add_argument("--pdf", required=False, type=str,
                        default=None, dest="pdf",
                        help='Specify PDF report name')
    parser.add_argument("--html", required=False, type=str,
                        default=None, dest="html",
                        help='Specify HTML report name')
    parser.add_argument("--json", required=False, type=str,
                        default=None, dest="json",
                        help='Specify report name')
    parser.add_argument("--size", required=False, nargs='+',
                        default=[None], dest="page_size",
                        help='Page sizes to ignore (--size 15 2010 8)')
    parser.add_argument("--get_proxies", dest="proxies", required=False,
                        action='store_true',
                        help='Gather socks4/socks5 elite proxies.')
    parser.add_argument("-sc", dest="session_cookie", required=False,
                        help='Specify a session cookie.')
    parser.add_argument("-cua", dest="custom_user_agent", required=False,
                        help='Set a custom user agent.')
    parser.add_argument("-v", "--version", required=False, action="store_true",
                        help="Display software version.")

    args = parser.parse_args()

    try:
        if sys.argv[1]:
            pass
    except IndexError:
        parser.print_help()
        sys.exit(1)

    if args.version:
        print(f"""
        fuzzbuster Version {__version__}
        Author: {__author__}
        Contact: {__email__}
        """)
        sys.exit(0)

    if args.proxies:
        network = Core.network.Network()
        print("[+] Elite SOCKS4/SOCK5 Proxies")
        print("---")
        print(network.get_proxies().strip())
        print("---")
        sys.exit(0)

    if args.session_cookie:
        Core.settings.Settings.session_cookie = args.session_cookie

    if args.custom_user_agent:
        Core.settings.CUSTOM_USER_AGENT = args.custom_user_agent

    if args.url is not None:
        url = args.url

    if (args.wordlist is not None) and (os.path.isfile(args.wordlist)):
        wordlist = args.wordlist
    else:
        print(f"[!] Invalid wordlist")
        sys.exit(1)

    Core.settings.Settings.PAGE_SIZE = args.page_size

    print(f"""
    SETTINGS VERIFICATION
    {colored(f"[+] URL set to: {url}", "yellow")}
    {colored(f"[+] Wordlist set to: {Path.absolute(Path(wordlist))}", "yellow")}
    [+] Session Cookie: {Core.settings.Settings.session_cookie}
    {colored(f"[+] Custom User-Agent: {Core.settings.CUSTOM_USER_AGENT}", "yellow")}
    [+] Page size(s) to ignore (comma-separated): {Core.settings.Settings.PAGE_SIZE[0]}
    """)

    answer = input(f"[?] Does this look correct ({colored('Y', attrs=['blink'])}/n) > ") or "y"
    if not answer.lower() == "y":
        sys.exit(0)

    responses = fuzz(url, wordlist)

    if args.pdf is not None:
        pdfreport = Core.reports.PdfReport(args.pdf, url, responses)
        pdfreport.generate_pdf_report()

    if args.html is not None:
        htmlreport = Core.reports.HtmlReport(args.html, url, responses)
        htmlreport.generate_html_report()

    if args.json is not None:
        jsonreport = Core.reports.JsonReport(args.json, url, responses)
        jsonreport.generate_json()


if __name__ == "__main__":
    main()
