import datetime


class Settings:
    max_workers = 30
    timeout = 10  # page load timeout


class SocksProxy:
    enable_socks = False
    socks_list = ''


class TorProxy:
    enable_socks = False
    tor_proxy = 'socks5://127.0.0.1:9050'


class UserAgents:
    user_agents = (
        ('Mozilla/5.0 (Linux; Android 11; Samsung SM-A025G) '
         'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19'),
        ('Mozilla/5.0 (Linux; Android 11; SM-A426U) '
         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36'),
        ('Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 '
         '(KHTML, like Gecko) FxiOS/36.0  Mobile/15E148 Safari/605.1.15'),
        ('Mozilla/5.0 (Linux; Android 11; SM-T227U Build/RP1A.200720.012; wv) '
         'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Safari/537.36'),
        ('Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0'),
        ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46'),
        ('Mozilla/5.0 (X11; CrOS x86_64 13982.82.0) AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/92.0.4515.157 Safari/537.36'),
        ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) '
         'Version/14.1.1 Safari/605.1.15'),
    )


class Colors:
    HEADER = '\033[95m'
    NOTE = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def trace(func):
    def wrapper(*args, **kwargs):
        print(f'TRACE: calling {func.__name__}() with {args}, {kwargs}')
        original_result = func(*args, **kwargs)
        print(f'TRACE: {func.__name__}() returned {original_result}')
        return original_result

    return wrapper


def fuzz_time(func):
    def wrapper(*args, **kwargs):
        print(f'{Colors.NOTE}[+] Fuzzer started at {datetime.datetime.today()}{Colors.END}')
        responses = func(*args, **kwargs)
        print(f'{Colors.NOTE}[+] Fuzzer completed at {datetime.datetime.today()}{Colors.END}')
        print(f'[+] Closing...')
        return responses
    return wrapper
