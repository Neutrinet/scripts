import os
import sys
import json
import string
import random
import zipfile
import getpass

import argh
import pexpect
import requests

from StringIO import StringIO


cube_template = """\
client
dev tun
proto udp
remote vpn.neutrinet.be 1194
resolv-retry infinite
nobind
ns-cert-type server
comp-lzo
topology subnet

ca keys/ca-server.crt
cert keys/user.crt
key keys/user.key

auth-user-pass keys/credentials

# Logs
verb 3
mute 5
status /var/log/openvpn-client.status
log-append /var/log/openvpn-client.log
"""


def generate_random_password():
    return ''.join(random.SystemRandom().choice(string.hexdigits) for n in xrange(60))

def get_user_input(name, default, dev, validate=None):
    if dev:
        return default
    return raw_input("%s:" % name)


def main(email, api_login, api_password=None, dev=False, api_base_url="https://api.neutrinet.be/api/", name=None, last_name=None, street=None, postal_code=None, town=None, country=None, birthplace=None, birthdate=None):
    if api_password is None:
        api_password = getpass.getpass("Your vpn api password (you must be admin, see with wannes):")

    session = requests.Session()

    sys.stdout.write("Generating a vpn registration key...")
    sys.stdout.flush()
    # generate a key for the vpn
    response = session.put(api_base_url + "unlock-key/new", auth=(api_login, api_password), headers={"Content-Type": "application/json"}, data='{"email": "%s"}' % email)

    assert response.status_code == 200, "%s: %s" % (response.status_code, response.content)
    key = response.json()["key"]
    sys.stdout.write("done\n")

    sys.stdout.write("Log into the vpn account creation api...")
    sys.stdout.flush()
    # log on the vpn API
    response = session.post(api_base_url + "reg/validateKey", data=json.dumps({"email": email, "key": key}), headers={"Content-Type": "application/json"})

    assert response.status_code == 200, "%s: %s" % (response.status_code, response.content)
    sys.stdout.write("done\n")

    sys.stdout.write("Sending randomly generated password...")
    sys.stdout.flush()
    id = response.json()["id"]
    password = generate_random_password()
    response = session.post(api_base_url + "reg/enterPassword", '{"id":"%s", "password":"%s"}' % (id, password))

    assert response.status_code == 200, "%s: %s" % (response.status_code, response.content)
    sys.stdout.write("done\n")

    sys.stdout.write("User personnal informations:\n")

    if name is None:
        name = get_user_input("Name", "pouet", dev)

    if last_name is None:
        last_name = get_user_input("Last name", "pouet", dev)

    if street is None:
        street = get_user_input("Street", "rue du chateau", dev)

    if postal_code is None:
        postal_code = get_user_input("Postal code", "1000", dev)

    if town is None:
        town = get_user_input("Town", "pouet", dev)

    if country is None:
        country = get_user_input("Country", "BE", dev)[:2].upper()

    if birthplace is None:
        birthplace = get_user_input("Birthplace", "pouet", dev)

    if birthdate is None:
        birthdate = get_user_input("Birthdate (format: dd-mm-yyyy)", "11-11-1990", dev)

    user_personnal_data = u'{"name":"%s","last-name":"%s","street":"%s","postal-code":"%s","municipality":"%s","birthplace":"%s","birthdate":"%s","undefined":"","country":"%s","id":"%s"}' % (
        name.decode("Utf-8"),
        last_name.decode("Utf-8"),
        street.decode("Utf-8"),
        postal_code,
        town.decode("Utf-8"),
        birthplace.decode("Utf-8"),
        birthdate,
        country[:2].upper(),
        id
    )

    user_personnal_data = user_personnal_data.encode("Utf-8")

    sys.stdout.write("Sending user personnal informations...")
    sys.stdout.flush()
    response = session.post(api_base_url + "reg/manual", user_personnal_data)

    if response.status_code == 303:
        print "ERROR: user already exists, abort"
        sys.exit(1)

    assert response.status_code == 200, "%s: %s" % (response.status_code, response.content)
    sys.stdout.write("done\n")

    user_db_id = response.json()["user"]
    client_db_id = response.json()["client"]["id"]

    if not os.path.exists(email):
        os.makedirs(email)

    sys.stdout.write("Generating openssl certificate...\n")

    openssl = pexpect.spawn("openssl req -out CSR.csr -new -newkey rsa:4096 -nodes -keyout client.key", cwd=os.path.join(os.path.realpath("."), email), timeout=5)

    openssl.expect("Country Name \(2 letter code\) \[AU\]:")
    openssl.sendline(str(country[:2].upper()))
    openssl.expect("State or Province Name \(full name\) \[Some-State\]:")
    openssl.sendline(country)
    openssl.expect("Locality Name \(eg, city\) \[\]:")
    openssl.sendline(town)
    openssl.expect("Organization Name \(eg, company\) \[Internet Widgits Pty Ltd\]:")
    openssl.sendline(".")
    openssl.expect("Organizational Unit Name \(eg, section\) \[\]:")
    openssl.sendline(".")
    openssl.expect("Common Name \(e.g. server FQDN or YOUR name\) \[\]:")
    openssl.sendline("certificate for %s" % email)
    openssl.expect("Email Address \[\]:")
    openssl.sendline(email)
    openssl.expect("A challenge password \[\]:")
    openssl.sendline("")
    openssl.expect("An optional company name \[\]:")
    openssl.sendline("")

    openssl.interact()

    sys.stdout.write("done\n")

    sys.stdout.write("Submit openssl certificate...")
    sys.stdout.flush()
    csr = session.put(api_base_url + "client/%s/cert/new" % client_db_id, open("%s/CSR.csr" % email).read(), cookies={"Registration-ID": id})
    assert csr.status_code in (204, 200), "%s: %s" % (csr.status_code, csr.content)
    sys.stdout.write("done\n")

    sys.stdout.write("Requesting IPv4...")
    sys.stdout.flush()
    ipv4 = session.put(api_base_url + "address/lease/new", '{"user":"%s","version":4,"client":%s}' % (user_db_id, client_db_id), cookies={"Registration-ID": id})

    assert ipv4.status_code == 200, "%s: %s" % (ipv4.status_code, ipv4.content)
    sys.stdout.write("done\n")

    sys.stdout.write("Requesting IPv6 /56 subnet...")
    ipv6 = session.put(api_base_url + "subnet/lease/new", '{"prefix":56,"version":6,"client":%s}' % (client_db_id), cookies={"Registration-ID": id})

    assert ipv6.status_code == 200, "%s: %s" % (ipv6.status_code, ipv6.content)
    sys.stdout.write("done\n")

    confirmation_data = {
        "user": csr.json()["client"]["userId"],
        "client": csr.json()["client"],
        "id": id,
        "completed": None,
        "ipv4Id": ipv4.json()["id"],
        "ipv6Id": ipv6.json()["id"],
        "sendEmail": False,
        "unlockKey": {
            "key": key,
            "email": email,
            "usedAt": None,
        },
    }

    sys.stdout.write("Confirm registration...")
    sys.stdout.flush()
    confirmation = session.post(api_base_url + "reg/commit", json.dumps(confirmation_data))

    assert confirmation.status_code == 200, "%s: %s" % (confirmation.status_code, confirmation.content)
    sys.stdout.write("done\n")

    sys.stdout.write("Getting zip file...")
    sys.stdout.flush()
    neutrinet_zipfile = session.post(api_base_url + "client/%s/config" % client_db_id, '{"regId":"%s","platform":"linux"}' % id, auth=(email, password), cookies={"Registration-ID": id})

    assert neutrinet_zipfile.status_code == 200, "%s: %s" % (neutrinet_zipfile.status_code, neutrinet_zipfile.content)
    sys.stdout.write("done\n")

    zipfile.ZipFile(StringIO(neutrinet_zipfile.content)).extractall(email)

    open(os.path.join(email, "auth"), "w").write("%s\n%s\n" % (email, password))

    open(os.path.join(email, "neutrinet.ovpn"), "a").write("auth-user-pass auth\nlog-append /var/log/openvpn.log\n")

    open(os.path.join(email, "FOR_CUBE.ovpn"), "w").write(cube_template)


if __name__ == '__main__':
    argh.dispatch_command(main)
