import random
import re
import sys
import urllib3
import requests
import Core.settings


class Network:
    def __init__(self):
        self.retry_addresses = []

    # @Core.settings.trace
    def perform_request(self, url: str, host: str = None) -> str | None:
        """Receives a URL to request. Performs the request with or without proxies.

        Keyword arguments:
            url -- The URL to request.
        Returns the HTTP status code of that request.
        """
        if Core.settings.SocksProxy.enable_socks and Core.settings.TorProxy.enable_socks:
            sys.exit("[!] WARNING: Both SOCKS5 and Tor are enabled in settings. Utilize only one proxy type.")

        if Core.settings.CUSTOM_USER_AGENT:
            headers = {
                'user-agent': Core.settings.CUSTOM_USER_AGENT
            }
        else:
            headers = {
                'user-agent': random.choice(Core.settings.UserAgents.user_agents),
            }

        cookies = ''

        if Core.settings.Settings.session_cookie:
            cookie = Core.settings.Settings.session_cookie.split(':')
            try:
                cookie[1] = cookie[1].strip()  # strip spacing from cookie
                cookies = {cookie[0]: cookie[1]}
            except IndexError:
                sys.exit("[!] Verify that the session cookie (-sc) is in the correct format: 'sess: c00k1edata'")

        proxies = ''

        if Core.settings.SocksProxy.enable_socks:
            proxy = random.choice(Core.settings.SocksProxy.socks_list)
            proxies = {'http': proxy, 'https': proxy}

        if Core.settings.TorProxy.enable_socks:
            proxy = Core.settings.TorProxy.tor_proxy
            proxies = {'http': proxy, 'https': proxy}

        try:
            urllib3.disable_warnings()  # Disable InsecureRequestWarning when attempting HTTPS
            response = requests.get(url=url, headers=headers, cookies=cookies, proxies=proxies,
                                    timeout=Core.settings.Settings.timeout, verify=False, allow_redirects=True)
        except requests.exceptions.SSLError:
            print("SSLERROR")
        except Exception as e:
            return
        else:
            match response.status_code:
                case 200:
                    if re.search('File not found', response.text):
                        return
                    if re.search("Error 404", response.text):
                        return
                    if re.search("status=404", response.text) and re.search("Whitelabel Error Page",
                                                                            response.text):
                        # Spring boot 404 with default content
                        return
                    if re.search("go_gc_cycles", response.text):
                        # golang
                        return

                    if Core.settings.PAGE_SIZE != [None]:
                        if str(len(response.content)) in Core.settings.PAGE_SIZE:
                            return
                        else:
                            return f"[200] Discovered: {url} [Size: {len(response.content)}]"

                    else:
                        return f"[200] Discovered: {url} [Size: {len(response.content)}]"

                case 302:
                    return f"[302] Temporary redirect: {url}"
                case 301:
                    return f"[301] Permanent redirect: {url}"
                case 401:
                    if str(len(response.content)) in Core.settings.Settings.PAGE_SIZE:
                        return
                    else:
                        return f"[401] Unauthorized: {url} [Size: {len(response.content)}]"
                case 403:
                    if re.search("You are authenticated as: anonymous", response.text):
                        # Skip Jenkins redirect
                        return
                    return f"[403] Forbidden: {url}"
                case 500:
                    return
                case _:
                    pass
            return

    def get_proxies(self) -> str:
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4,socks5&" \
              "timeout=100&country=all&ssl=all&anonymity=elite"
        try:
            response = requests.get(url)
        except Exception as e:
            sys.exit(e)

        return response.text
