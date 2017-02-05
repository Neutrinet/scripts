# Sendmail

A simple Ruby script that:
- reads a body from a file
- send a personalized email to each recipient in a given CSV file

## Getting Started

```bash
$ cd sendmail
$ script/setup
```

Set ENV variables in `.env`.
Make sure `source.csv` looks like this:

```
user1@example.com,80.67.181.229
user2@example.com,80.67.181.230
```

Edit `body.txt` and make sure to have `IP_ADDRESS` show up somewhere in the file.

Then run:

```bash
$ ruby sendmail.rb
```
