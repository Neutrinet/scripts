import psycopg2
import dotenv
import csv
import sys

src = sys.argv[1]
dest = sys.argv[2]

def connect():
    return psycopg2.connect(host=dotenv.get('HOSTNAME'),
                            port=dotenv.get('PORT'),
                            user=dotenv.get('USERNAME'),
                            password=dotenv.get('PASSWORD'),
                            dbname=dotenv.get('DATABASE'))

def ipv4_from_user_id(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute('select address from address_pool where "ipVersion"=4 and client_id in (select id from ovpn_clients where "userId"=%s)', (user_id,))
    records = cur.fetchall()
    cur.close
    conn.close()
    return records[0][0]

dotenv.load()
src_file = open(src, 'rb')
dest_file = open(dest, 'wb')
reader = csv.reader(src_file, delimiter=',')
writer = csv.writer(dest_file, delimiter=',')

for line in reader:
    user_id = line[0].strip()
    email = line[1].strip()
    ip = ipv4_from_user_id(user_id)
    writer.writerow([user_id, email, ip])
    print "%s: %s - %s" % (user_id, email, ip)

print "\n%s was created." % dest

src_file.close()
dest_file.close()
