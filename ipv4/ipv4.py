import psycopg2
import dotenv
from netaddr import *

def connect():
    return psycopg2.connect(host=dotenv.get('HOSTNAME'),
                            port=dotenv.get('PORT'),
                            user=dotenv.get('USERNAME'),
                            password=dotenv.get('PASSWORD'),
                            dbname=dotenv.get('DATABASE'))

def ips_in_database():
    conn = connect()
    cur = conn.cursor()
    cur.execute('SELECT address FROM address_pool where "ipVersion"=4 AND address like %s', ('80.67.181.%',))
    records = cur.fetchall()
    cur.close
    conn.close()
    return IPSet(map(lambda r: r[0], records))

def ips_summary(set):
    ips = sorted(IPSet(set).iprange())
    return "%d addresses (%s..%s)" % (len(ips), ips[0], ips[-1])

def insert_ipv4s(addresses):
    print 'Those IP addresses will be inserted into the database:'
    print ', '.join(map(lambda a: str(a), addresses))
    answer = raw_input("Are you sure? (N/y) : ")
    if answer.lower() != 'y':
        print "Aborting..."
        return

    print "Inserting..."
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT setval('address_pool_id_seq', (SELECT MAX(id) FROM address_pool));")
    for address in addresses:
        sql_statement = '''insert into address_pool
                        (client_id, address, "ipVersion", enabled, "leasedAt", expiry, netmask, purpose)
                        values (-1, %s, 4, true, '2016-12-25 14:00:00', '2026-12-25 14:00:00', 32,
                        'CLIENT_ASSIGN')'''
        if cur.execute(sql_statement, (str(address),)) is not None:
            print "Lastrowid: %d" % cur.lastrowid
            print "Query: %s" % cur.query
            print "Status: %s" % cur.statusmessage
            break
    conn.commit()
    print "Inserted."
    cur.close
    conn.close()

dotenv.load()
neutrinet_ip_range = IPSet(IPNetwork('80.67.181.0/24'))
reserved_ip_range = IPSet(IPNetwork('80.67.181.0/28'))
existing_ip_range = IPSet(IPNetwork('80.67.181.128/25')).union(ips_in_database())
range_to_add = neutrinet_ip_range - reserved_ip_range - existing_ip_range

print "Neutrinet IP Range: %s" % ips_summary(neutrinet_ip_range)
print "Reserved IP Range: %s" % ips_summary(reserved_ip_range)
print "Existing IP Range: %s" % ips_summary(existing_ip_range)
print "IP Range to add: %s" % ips_summary(range_to_add)

insert_ipv4s(range_to_add)
