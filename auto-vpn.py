#!/usr/bin/env python
"""
auto-vpn, written by @dtibarra 2011-09-24
"""
import ConfigParser
import mechanize
import re
import sys
import subprocess
import libvpn_configurator
import time

config_file = 'auto-vpn.conf'
if libvpn_configurator.determine_os() != "Debian":
    print "[*] Non-debian OS detected, proceeding with undefined behavior."

#Configuration stuff
config = ConfigParser.ConfigParser()
config.read(config_file)
url = config.get('auth', 'url')
email = config.get('auth', 'email')
password = config.get('auth', 'password')
regex_string = config.get('etc', 'result_regex')
ips = config.get('etc', 'ips_to_access').split(',')
vpn_server = config.get('auth', 'vpn_server')
vpn_user = config.get('auth', 'vpn_user')
vpn_name = config.get('auth', 'vpn_name')

if libvpn_configurator.chap_is_stale():
    print "[+] Fetching password..."
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
    try:
        libvpn_configurator.write_chap_secret(vpn_user, vpn_name, vpn_password)
        libvpn_configurator.write_peer_file(vpn_user, vpn_name, vpn_server)
    except IOError:
        print "[ERRORED] Password is %s - please connect manually." % (vpn_password)
        sys.exit(1)
    print "[+] Got a password!"

print "[+] Setting up VPN..."
#Do VPN stuff!
libvpn_configurator.start_vpn(vpn_name)
gateway = False
tries = 0
while not gateway:
    gateway = libvpn_configurator.get_gateway()
    time.sleep(2)
    tries += 1
    if tries > 15:
        print "[!] Could not get the gateway to create the tunnel. Please make sure pptp is running properly and create the route manually"
        sys.exit(1)
for ip in ips:
   libvpn_configurator.create_route(ip, gateway)
print "[+] VPN set up? Check to see if the routes were properly created."
