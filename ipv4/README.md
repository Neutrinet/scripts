# Scripts to add/free IPv4s

## Getting started

Install dependencies on your local machine:

```bash 
sudo apt install libpq-dev python-dev
```

In a separate terminal, create the SSH tunel to be able to connect to the Postgres database from your local machine:

```bash
ssh -p 2222 USERNAME@left-panda.neutrinet.be -L 9000:localhost:5432
```

Clone the repository and setup the python env on your local machine:

```bash 
git clone https://github.com/Neutrinet/scripts.git
cd scripts/ipv4
virtualenv ve
source ve/bin/activate
pip install -r requirements.txt
```

Set the Postgres connection info:

```bash
cp .env.sample .env
vim .env # port should be set to 9000
```

## Scripts

### add_ipv4.py

This script inserts the IPv4 addresses Neutrinet has in its possession and that are not yet in the `address_pool` table of the `ispng` database.
This script is supposed to be run once, from your local machine, with a SSH tunnel created to connect to the Postgres server running on `left-panda`.

Run the script:

```bash
python add_ipv4.py
```
**Remarks**

- The script resets the `address_pool_id_seq` value to fix this error:

```
duplicate key value violates unique constraint "address_pool_pkey"
DETAIL:  Key (id)=(774838) already exists.
```

### get_ips_from_user_ids.py

This script gets the IP associated with a userId.
It takes a CSV file as an input, connects to the `ispng` database, and the output is a CSV containing the IP addresses.

```bash
python get_ips_from_user_ids.py input_sample.csv outpout.csv
```

### free_ips_from_list.py

This script frees IPv4 addresses.
It takes a CSV file as an input, connects to the `ispng` database, and free the IPs listed in the CSV file.

```bash
python free_ips_from_list.py ip_to_free_sample.csv
```

## How to use those scripts together

- get a list of userId/email for expired certificates (with Tharyrok's script), save it to input.csv
- get the IP addresses associated with those certificates: `python get_ips_from_user_ids.py input.csv output.csv`
- manually create a file called `ip_to_free.csv` with the IPs you're sure you can free
- free those IPs: `python free_ips_from_list.py ip_to_free.csv`

Look at the sample CSV files in the `csv_samples` directory to check the expected format.
