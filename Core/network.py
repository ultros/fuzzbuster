import random
import re
import requests
import Core.settings


class Network:
    def __init__(self):
        pass

    # @Core.settings.trace
    def perform_request(self, url: str) -> str | None:
        """Receives a URL to request. Performs the request with or without proxies.

        Keyword arguments:
            url -- The URL to request.
        Returns the HTTP status code of that request.
        """
        if Core.settings.SocksProxy.enable_socks and Core.settings.TorProxy.enable_socks:
            print("[!] WARNING: Both SOCKS5 and Tor are enabled in settings. Utilize only one proxy type.")
            exit(0)

        headers = {'user-agent': random.choice(Core.settings.UserAgents.user_agents)}
        response = None

        if Core.settings.SocksProxy.enable_socks:
            proxy = random.choice(Core.settings.SocksProxy.socks_list)
            proxies = {'http': proxy, 'https': proxy}
            try:
                response = requests.get(url=url, proxies=proxies, headers=headers,
                                        timeout=Core.settings.Settings.timeout)
            except Exception as e:
                # print(e)
                pass

        if Core.settings.TorProxy.enable_socks:
            proxy = Core.settings.TorProxy.tor_proxy
            proxies = {'http': proxy, 'https': proxy}
            try:
                response = requests.get(url=url, proxies=proxies, headers=headers,
                                        timeout=Core.settings.Settings.timeout)
            except Exception as e:
                # print(e)
                pass

        if not Core.settings.TorProxy.enable_socks and not Core.settings.SocksProxy.enable_socks:
            try:
                response = requests.get(url=url, headers=headers, timeout=Core.settings.Settings.timeout)
            except Exception as e:
                # print(e)
                pass

        try:
            match response.status_code:
                case 200:
                    if re.search == "":
                        # Handle 200 empty page
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
                    else:
                        return f"[200] Discovered: {url}"
                case 302:
                    return f"[302] Temporary redirect: {url}"
                case 301:
                    return f"[301] Permanent redirect: {url}"
                case 403:
                    if re.search("You are authenticated as: anonymous", response.text):
                        # Skip Jenkins redirect
                        return
                    return f"[403] Forbidden: {url}"
                case 500:
                    return
                case _:
                    pass
        except Exception as e:
            # print(e)
            return
