#!/usr/bin/env python3.11
import argparse
import concurrent.futures
import logging
import os
from datetime import datetime as dt

import Core.network
import Core.process
import Core.reports
import Core.settings

logging.basicConfig(filename="log.txt", encoding='utf-8', level=logging.INFO, format='')


def print_banner():
    banner = [
        f'{Core.settings.Colors.HEADER}\u24D5\u24E4\u24E9\u24E9\u24D1\u24E4\u24E2\u24E3\u24D4\u24E1'
        f'{Core.settings.Colors.END}'
    ]
    for line in banner:
        print(line)


print_banner()


@Core.settings.fuzz_time
def fuzz(url: str, wordlist: str) -> list:
    original_fuzzer_url = url
    networking = Core.network.Network()
    processing = Core.process.Process(wordlist)
    formatted_url_list = processing.format_wordlist(url)

    # print(id(formatted_url_list))
    total_urls = 0
    i = 0
    valid_response_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=Core.settings.Settings.max_workers) as executor:
        futures = []

        for url in formatted_url_list:
            futures.append(executor.submit(networking.perform_request, url))
            total_urls += 1
            print(f"Total URLs: {total_urls}...", end="\r")

        try:
            for future in concurrent.futures.as_completed(futures):
                response = future.result()
                if response is not None:
                    valid_response_list.append(response)
                    print(f"{response}")

                i += 1
                print(end='\x1b[2K')
                print(f"{i} of {total_urls}", end="\r")  # to end of line

        except Exception as e:
            print("[!] Is the web server running?")
            print(f"[!] {e}")
            i += 1
            pass

        print(end='\x1b[2K')
        print(f"{i} of {total_urls}")

        assert type(valid_response_list) == list
        logging.info(
            f"{dt.now()} ({original_fuzzer_url}) {len(valid_response_list)} resolved URLs returned from {total_urls}"
            f" total URL entries.")
        for url in valid_response_list:
            logging.info(f" -  {url}")

        return valid_response_list


def main():
    parser = argparse.ArgumentParser(description="URL Fuzzer (E.g. www.google.com/search?q=FUZZ")
    parser.add_argument('-u', '--url', required=True, type=str,
                        default=None, dest="url",
                        help="Specify URL to fuzz (e.g. www.google.com/search?q=FUZZ")
    parser.add_argument('-w', '--wordlist', required=True, type=str,
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

    args = parser.parse_args()

    if args.url is not None:
        url = args.url

    if (args.wordlist is not None) and (os.path.isfile(args.wordlist)):
        wordlist = args.wordlist
    else:
        print(f"[!] Invalid wordlist")
        exit(1)

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
