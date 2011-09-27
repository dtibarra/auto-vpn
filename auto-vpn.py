#!/bin/env python
"""
auto-vpn, written by @dtibarra 2011-09-24
"""
import ConfigParser
import mechanize
import re
import sys

config_file = 'auto-vpn.conf'

#Configuration stuff
config = ConfigParser.ConfigParser()
config.read(config_file)
url = config.get('auth', 'url')
email = config.get('auth', 'email')
password = config.get('auth', 'password')
regex_string = config.get('etc', 'result_regex')

#Populate and submit form
br = mechanize.Browser()
br.set_handle_robots(False) #VPN login doesn't allow crawlers
br.open(url)
br.select_form(nr=0) #Form is nameless
br['email'] = email
br['password'] = password
response = br.submit()

#Regex out the password and print (or exit on error)
response = response.read()
match = re.search(regex_string, response)
if match:
    vpn_password = match.group('vpn_password')
else:
    print("Error fetching VPN password! Bailing out.")
    sys.exit(1)
print vpn_password
