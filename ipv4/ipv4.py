import psycopg2
import dotenv


def connect():
    return psycopg2.connect(host=dotenv.get('HOSTNAME'),
                            port=dotenv.get('PORT'),
                            user=dotenv.get('USERNAME'),
                            password=dotenv.get('PASSWORD'),
                            dbname=dotenv.get('DATABASE'))

def sorted_ipv4s(ipv4s):
    return sorted(ipv4s, key=lambda a: int(a.split('.')[-1])) 

def get_existing_ipv4s():
    conn = connect()
    cur = conn.cursor()
    cur.execute('SELECT address FROM address_pool where "ipVersion"=4 AND address like %s', ('80.67.181.%',))
    records = cur.fetchall()
    cur.close
    conn.close()
    return sorted_ipv4s(map((lambda r: r[0]), records))

def list_all_possible_ipv4s():
    prefix = "80.67.181."
    return map((lambda a: prefix + str(a)), range(256))

def list_ipv4s_to_add(all, existing, exceptions=None):
    ipv4s_to_add = set(all) - set(existing)
    if exceptions is not None:
        ipv4s_to_add -= set(exceptions)
    return sorted_ipv4s(list(ipv4s_to_add))

def insert_ipv4s(addresses):
    answer = raw_input("Are you sure you want to insert those IP addresses? (N/y) : ")
    if answer.lower() != 'y':
        print "Aborting..."
        return

    print "Inserting..."
    conn = connect()
    cur = conn.cursor()
    for address in addresses:
        sql_statement = '''insert into address_pool
                        (client_id, address, "ipVersion", enabled, "leasedAt", expiry, netmask, purpose)
                        values (-1, %s, 4, true, '2016-12-25 14:00:00', '2026-12-25 14:00:00', 32,
                        'CLIENT_ASSIGN')'''
        if cur.execute(sql_statement, (address,)) is not None:
            print "Lastrowid: %d" % cur.lastrowid
            print "Query: %s" % cur.query
            print "Status: %s" % cur.statusmessage
            break
    conn.commit()
    print "Inserted."
    cur.close
    conn.close()

dotenv.load()
all_addresses = list_all_possible_ipv4s()
existing_addresses = get_existing_ipv4s()
# exceptions= ["80.67.181.255"]
exceptions= []
addresses_to_add = list_ipv4s_to_add(all_addresses, existing_addresses, exceptions)

print "There are %d possible IPv4 addresses for our range. (%s..%s)" % (len(all_addresses), all_addresses[0], all_addresses[-1])
print "There are %d existing IPv4 addresses for our range. (%s..%s)" % (len(existing_addresses), existing_addresses[0], existing_addresses[-1])
print "There are %d IPv4 addresses to add for our range:" % len(addresses_to_add)
print ', '.join(addresses_to_add)
insert_ipv4s(addresses_to_add)
