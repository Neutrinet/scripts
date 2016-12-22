Commands:

    virtualenv ve
    source ve/bin/activate
    pip install -r requirements.txt

Run it:

    source ve/bin/activate
    python script.py <user email> <api login>  # a prompt will ask for your password

    # you can also specify the password as a cli arg
    python script.py <user email> <api login> --api-password foobar
