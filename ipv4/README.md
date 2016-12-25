# ipv4.py

This script inserts the IPv4 addresses Neutrinet has in its possession and that are not yet in the `address_pool` table of the `ispng` database.
This script is supposed to be run once, from your local machine, with a SSH tunnel created to connect to the Postgres server running on `left-panda`.

## Getting started

Install dependencies:

```bash 
sudo apt install libpq-dev python-dev
```

In a separate terminal, create the SSH tunel:

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

Run the script:

```bash
python ipv4.py
```
