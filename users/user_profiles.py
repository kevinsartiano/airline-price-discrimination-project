"""User list."""
import os

WINDOWS_CHROME_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
ANDROID_CHROME_UA = 'Mozilla/5.0 (Linux; Android 10; M2007J3SG) ' \
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36'
MACOS_SAFARI_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) ' \
                  'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15'
IOS_SAFARI_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) ' \
                'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1'

WINDOWS_CHROME = {
    'user': 'Windows-Chrome',
    'os': 'Windows 10',
    'browser': 'Chrome 87',
    'user_agent': WINDOWS_CHROME_UA,
    'vpn_server': 'it170',
    'ip_address': '185.183.105.28',
    'cookie_jar': os.path.join('cookie_jars', 'windows_chrome')
}

ANDROID_CHROME = {
    'user': 'Android-Chrome',
    'os': 'Android 10',
    'browser': 'Chrome 87',
    'user_agent': ANDROID_CHROME_UA,
    'vpn_server': 'it175',
    'ip_address': '82.102.21.68',
    'cookie_jar': os.path.join('cookie_jars', 'android_chrome')
}

MACOS_SAFARI = {
    'user': 'MacOS-Safari',
    'os': 'Mac OS 10.15',
    'browser': 'Safari 14.0',
    'user_agent': MACOS_SAFARI_UA,
    'vpn_server': 'it180',
    'ip_address': '192.145.127.236',
    'cookie_jar': os.path.join('cookie_jars', 'macos_safari')
}

IOS_SAFARI = {
    'user': 'iOS-Safari',
    'os': 'iOS 14.3',
    'browser': 'Safari 14.0',
    'user_agent': IOS_SAFARI_UA,
    'vpn_server': 'it185',
    'ip_address': '84.17.59.143',
    'cookie_jar': os.path.join('cookie_jars', 'ios_safari')
}

USER_LIST = [WINDOWS_CHROME, ANDROID_CHROME, MACOS_SAFARI, IOS_SAFARI]
