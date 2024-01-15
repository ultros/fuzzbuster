#!/usr/bin/env python3

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
from alive_progress import alive_bar

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

    with (concurrent.futures.ThreadPoolExecutor(max_workers=Core.settings.Settings.max_workers) as executor):
        futures = []
        with alive_bar(len(formatted_url_list), title=f'Scanning Target', bar='smooth', enrich_print=False) as bar:
            for url in formatted_url_list:
                futures.append(executor.submit(networking.perform_request, url))

            for future in concurrent.futures.as_completed(futures):
                response = future.result()

                if response is not None:
                    valid_response_list.append(response)
                    print(f"{response}")

                bar()

            print(f"Total connection errors: {networking.timeouts}")

            assert type(valid_response_list) is list
            logging.info(
                f"{dt.now()} ({original_fuzzer_url}) {len(valid_response_list)} "
                f"resolved URLs returned from {total_urls}"
                f" total URL entries.")

            for url in valid_response_list:
                logging.info(f" -  {url}")

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
    parser.add_argument("--title", dest="title", required=False,
                        action='store_true',
                        help='Capitalize first letter in Fuzz.')
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
        fuzzbuster Version {__version__} - 1/3/2024
        Author: {__author__}
        Contact: {__email__}
        GitHub: https://github.com/ultros/fuzzbuster
        """)
        sys.exit(0)

    if args.title:
        Core.settings.TITLE = True

    if args.page_size:
        Core.settings.PAGE_SIZE = args.page_size

    if args.proxies:
        network = Core.network.Network()
        print("[+] Elite SOCKS4 Proxies")
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

    print(f"""
    SETTINGS VERIFICATION
    {colored(f"[+] URL set to: {url}", "yellow")}
    {colored(f"[+] Wordlist set to: {Path.absolute(Path(wordlist))}", "yellow")}
    [+] Session Cookie: {Core.settings.Settings.session_cookie}
    {colored(f"[+] Custom User-Agent: {Core.settings.CUSTOM_USER_AGENT}", "yellow")}
    [+] Page size(s) to ignore: {Core.settings.PAGE_SIZE}
    [+] Title set to {colored(str(Core.settings.TITLE), "yellow")} (uppercase first letter of Fuzz if True)")
    """)
    if Core.settings.SocksProxy.enable_socks:
        print(f"""
    [!] Proxies in use: {Core.settings.SocksProxy.socks_list}
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


def install_dependencies():
    pass


if __name__ == "__main__":
    main()
