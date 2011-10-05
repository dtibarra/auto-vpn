from subprocess import Popen, PIPE
import re
import os
import time

# This function determines what flavor Linux we're running on.
def determine_os():
    command = ["lsb_release", "-a"]
    try:
        p = Popen(command, stdout=PIPE, stderr=PIPE)
    except OSError:
        return "Unknown"
    output = p.communicate()[0]
    match = re.search('Distributor\sID:\s(.+)', output)
    if match:
        return match.group(1)
    else:
        return "Unknown"

#Checks to see if our VPN password is stale or not
def chap_is_stale():
    #if the file was written before the hour, and it's now after the hour, it's
    #stale. There's a case where if I sign in, reboot, and sign in again it
    #technically could possibly not work (FIXME)
    try:
        file_time = time.localtime(os.stat('/tmp/_chap_secret').st_mtime)
    except OSError:
        return True
    current_time = time.localtime()
    if file_time[3] < current_time[3]:
        return True
    else:
        return False

#Writes our chap secret file with the given credentials
def write_chap_secret(user_name, vpn_name, password):
    try:
        f = open('/etc/ppp/chap-secrets','r')
    except IOError:
        print "[!] Cannot open chap-secrets file!"
        raise
    lines = []
    chap_regex = re.compile('''%s\s+%s\s+['"]?[a-zA-Z0-9]+['"]?\s+\*''' % (user_name,
                                                                           vpn_name))
    secret_added = False
    for line in f.readlines():
        if re.search(chap_regex, line):
            lines.append('%s %s "%s" *\n' % (user_name, vpn_name, password))
            secret_added = True
        else:
            lines.append(line)
    if not secret_added:
        lines.append('%s %s "%s" *\n' % (user_name, vpn_name, password))
    f.close()
    f = open('/etc/ppp/chap-secrets','w')
    for line in lines:
        f.write("%s" % (line))
    f.close()
    open('/tmp/_chap_secret','w').close()

#Writes our peer file with the given information
def write_peer_file(user_name, vpn_name, vpn_host):
    try:
        f = open('/etc/ppp/peers/%s' % (vpn_name),'w')
    except IOError:
        print "[!] Cannot open chap-secrets file!"
        raise
    f.write('pty "pptp %s --nolaunchpppd"\n' % (vpn_host))
    f.write('lock\n')
    f.write('noauth\n')
    f.write('nobsdcomp\n')
    f.write('nodeflate\n')
    f.write('name %s\n' % (user_name))
    f.write('remotename %s\n' % (vpn_name))
    f.write('ipparam %s\n' % (vpn_name))
    f.write('require-mppe-128\n')
    f.close()

#Use pon to enable vpn for us.
def start_vpn(vpn_name):
    command = ["pon", vpn_name]
    try:
        p = Popen(command)
    except OSError:
        print "[!] Cannot start the VPN, likely you do not have pon installed \
or it's not in your PATH."

#grabs the gateway ip for pptp
def get_gateway():
    p1 = Popen(["ip","addr"], stdout=PIPE)
    p2 = Popen(['grep','ppp0'], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(['grep', 'inet'],stdin=p2.stdout, stdout=PIPE)
    line = p3.communicate()[0]
    match = re.search('\s+inet\s([0-9\.]+)\speer\s([0-9\.]+)/32.*', line)
    if match:
        return match.group(2)
    else:
        return False

def create_route(ip, gateway):
    Popen(["ip", "route", "add", ip, "via", gateway])
