import re


class Process:
    def __init__(self, wordlist: str):
        self.wordlist = wordlist

    # @Core.settings.trace
    def format_url(self, url: str, keyword: str) -> str | None:
        """Returns a formatted URL to fuzz/directory bust."""
        try:
            if re.search("FUZZ", url):
                formatted_url = url.replace("FUZZ", keyword.strip())
            else:
                print('[!] Could not find the "FUZZ" string in your URL. E.g. https://www.google.com/search?&q=FUZZ')
                return

        except Exception as e:
            print(e)
            return

        return formatted_url

    # @Core.settings.trace
    def format_wordlist(self, url: str) -> list:
        """Returns valid URLs (list) and a total of all URLs in the wordlist."""
        valid_urls = []
        wordlist = ''

        try:
            wordlist = open(self.wordlist, 'r')
        except Exception as e:
            print(e)

        try:
            for word in wordlist:
                temp_url = self.format_url(url, word)
                if temp_url is not None:
                    valid_urls.append(temp_url)
                else:
                    exit(0)

        except Exception as e:
            print(e)

        # print(id(valid_urls))
        return valid_urls
