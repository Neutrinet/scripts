#!/bin/bash

usage="Usage: dyndns.sh <ipv4 or ipv6> <domain name> <DNS server to be updated>
No trailing dot is needed for the domain"


#From http://www.linuxjournal.com/content/validating-ip-address-bash-script

function valid_ipv4()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

function valid_ipv6()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ (([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])) ]]
 	then return 0
    else return 1
    fi
}





function valid_domain 
{
     local  domain=$1
# From http://stackoverflow.com/a/20204811	
     match=$(echo $domain | grep -P '(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}\.?$)' -c)
     if [ $match -eq 1 ]
	then return 0
        else
            return 1 
        fi
}


function valid_dns_server
{
	local  nom=$1
	if (valid_ipv4 $nom) || (valid_domain $nom) || (valid_ipv6 $nom)
		then return 0
	else
		return 1
	fi
	
}

function valid_A_record
{
	local domain=$1
	local ip=$2

	A_record=$(dig +short $domain | tail -1)

	if [ $A_record == $ip ]
                then return 0
        else
                return 1
        fi
} 

function valid_AAAA_record
{
	local domain=$1
	local ip=$2

	AAAA_record=$(dig +short $domain AAAA | tail -1)

	if [ $AAAA_record == $ip ]
                then return 0
        else
                return 1
        fi
} 





if [ $# -ne 3 ]
        then echo "Invalid amount of arguments - 3 arguments requested"
        echo "$usage"
        exit 33
fi



if valid_ipv4 $1
	then ip_type="v4"
elif valid_ipv6 $1
	then ip_type="v6"
else
	echo "Invalid IP"
	echo "$usage"
	exit 1
fi

if ! valid_domain $2
then echo "Invalid fqdn - Maximum 253 characters - Works with IDN (internationalized domain name). Trailing dot can be added (optional)"
        echo "$usage"
        exit 2
fi

if ! valid_dns_server $3
        then echo "Invalid DNS server name. It doesn't appear to be either a hostname or an IP"
        echo "$usage"
        exit 3
fi

if [ $ip_type == "v4" ]
	then
	if ! valid_A_record $2 $1
        	then echo "The suggested PTR record for the IP address doesn't seem to point to that IP address"
        	echo "$usage"
        	exit 4
	fi

elif [ $ip_type == "v6" ]
	 then
         if ! valid_AAAA_record $2 $1
                 then echo "The suggested PTR record for the IP address doesn't seem to point to that IP address"
                 echo "$usage"
                 exit 4
         fi      


fi

reverse_ip=$(dig -x $1 +noall +question | tail -1 | cut -d";" -f2 | cut -d'	' -f1 | cut -d' ' -f1)

workingfile=$(mktemp)

echo "server $3" >> $workingfile
echo "update add $reverse_ip 8400 PTR $2" >> $workingfile
echo "send" >> $workingfile

nsupdate -d $workingfile

if [ $? -eq 0 ]
	then echo "Success!"
	exit 0

else 
	echo "nsupdate wasn't able to do the update. Please check this is a Neutrinet IP and that DNS server info is correct (currently should be 172.31.1.253)"
	exit 5
fi	

rm $workingfile
