#!/bin/sh
if ps -ef | grep -v grep | grep discord_interface-v15.py ; then
        exit 0
else
        python3.6 /root/projects/discord-bot/discord_interface-v15.py
        # >> /home/user/bin/spooler.log &
        #mailing program
        #/home/user/bin/simplemail.php "Print spooler was not running...  Restarted." 
        exit 0
fi
