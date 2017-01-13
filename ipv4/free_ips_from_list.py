import psycopg2
import dotenv
import csv
import sys

src = sys.argv[1]

def connect():
    return psycopg2.connect(host=dotenv.get('HOSTNAME'),
                            port=dotenv.get('PORT'),
                            user=dotenv.get('USERNAME'),
                            password=dotenv.get('PASSWORD'),
                            dbname=dotenv.get('DATABASE'))

def free_ip(ip):
    conn = connect()
    cur = conn.cursor()
    cur.execute('update address_pool set client_id = -1 where "ipVersion" = 4 and address = %s', (ip,))
    conn.commit()
    cur.close
    conn.close()

dotenv.load()
src_file = open(src, 'rb')
reader = csv.reader(src_file, delimiter=',')

for line in reader:
    ip = line[0].strip()
    free_ip(ip)
    print "%s is now available." % (ip)

src_file.close()
