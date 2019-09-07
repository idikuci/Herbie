#!/bin/sh
if ps -ef | grep -v grep | grep record_blockchain-v6.py ; then
        exit 0
else
        python3.6 /root/projects/discord-bot/record_blockchain-v6.py
        # >> /home/user/bin/spooler.log &
        #mailing program
        #/home/user/bin/simplemail.php "Print spooler was not running...  Restarted." 
        exit 0
fi
