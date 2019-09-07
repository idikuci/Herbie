# Work with Python 3.6
import discord
import psycopg2
import asyncio
import os
import logging

from beem.steem import Steem
from beem.account import Account
#from time import sleep

TOKEN = 'NTg1NzI4NDk3MzI3Mjc2MDMy.XPd6iw.X3rW_9QGWtTwZJDI4cNuo8Knt2Q'

client = discord.Client()

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Logging
logger = logging.getLogger("Herbie")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(f"{DIR_PATH}/Discord.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


 # Connect to Database
cursor = None
conn = None
try:
    connect_str = "dbname='smoke' user='XXXXXX' host='localhost' " + \
                  "password='XXXXXX'"
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    # create a psycopg2 cursor that can execute queries
#    cursor = conn.cursor()
except Exception as e:
    print(f"Invalid dbname, user or password? - {e}")
    logger.error(f"Invalid dbname, user or password? - {e}")

nodes = ['https://rpc.smoke.io/']

s = Steem(node = nodes)

def account_exists(accountname):

  try:
    acc = Account(accountname, steem_instance = s)
    return True
  except:
    return False

def add_watchword(discord_id, watchword=[], type='self'):

  cur = conn.cursor()
  if watchword: # If no watchword, assume self being added
    if type == 'transfer': # if a transfer, add both in and out options
      cur.execute("""INSERT INTO watchlist (discord_id, watchword, type) SELECT %s, %s, %s
                  WHERE NOT EXISTS (SELECT discord_id FROM watchlist WHERE discord_id = %s AND watchword = %s and type = 'transferto') ;""", (discord_id, watchword, 'transferto', discord_id, watchword) )
      cur.execute("""INSERT INTO watchlist (discord_id, watchword, type) SELECT %s, %s, %s
                  WHERE NOT EXISTS (SELECT discord_id FROM watchlist WHERE discord_id = %s AND watchword = %s and type = 'transferfrom') ;""", (discord_id, watchword, 'transferfrom', discord_id, watchword) )
    elif type == 'vote':  # if a vote, add both in and out options
      cur.execute("""INSERT INTO watchlist (discord_id, watchword, type) SELECT %s, %s, %s
                  WHERE NOT EXISTS (SELECT discord_id FROM watchlist WHERE discord_id = %s AND watchword = %s and type = 'votein') ;""", (discord_id, watchword, 'votein', discord_id, watchword) )
      cur.execute("""INSERT INTO watchlist (discord_id, watchword, type) SELECT %s, %s, %s
                  WHERE NOT EXISTS (SELECT discord_id FROM watchlist WHERE discord_id = %s AND watchword = %s and type = 'voteout') ;""", (discord_id, watchword, 'voteout', discord_id, watchword) )

    else: # otherwise just add it direct to db as is
      cur.execute("""INSERT INTO watchlist (discord_id, watchword, type) VALUES (%s, %s, %s);""", (discord_id, watchword, type) )
  else: # no watchword to be added with self.
    cur.execute("""INSERT INTO watchlist (discord_id, type) VALUES ( %s, %s);""", (discord_id, type) )

  cur.close()
  conn.commit()

def already_exists(discord_id, watchword=[], type=[]):
  cur = conn.cursor()
  if watchword:
    if type == 'transfer':
       cur.execute(f"SELECT COUNT(*) FROM watchlist where discord_id='{discord_id}' and watchword='{watchword}' and type='transferto';")
       result = cur.fetchone()
       if result[0] > 0:
         cur.execute(f"SELECT COUNT(*) FROM watchlist where discord_id='{discord_id}' and watchword='{watchword}' and type='transferfrom';")
       else:
         return False
    elif type == 'vote':
       cur.execute(f"SELECT COUNT(*) FROM watchlist where discord_id='{discord_id}' and watchword='{watchword}' and type='votein';")
       result = cur.fetchone()
       if result[0] > 0:
         cur.execute(f"SELECT COUNT(*) FROM watchlist where discord_id='{discord_id}' and watchword='{watchword}' and type='voteout';")
       else:
         return False

    else:
       cur.execute(f"SELECT COUNT(*) FROM watchlist where discord_id='{discord_id}' and watchword='{watchword}' and type='{type}';")
#  if type:
#      cur.execute(f"SELECT COUNT(*) FROM watchlist where discord_id='{discord_id}' AND type = '{type}';")

  else:
    if type:
#      print(f"Person: {discord_id}, Type: {type}")
      cur.execute(f"SELECT COUNT(*) FROM watchlist where discord_id='{discord_id}' AND type = '{type}';")
    else:
      cur.execute(f"SELECT COUNT(*) FROM watchlist where discord_id='{discord_id}' ;")


  result = cur.fetchone()
#  print(result[0])
  if result[0] > 0:
    return True
  else:
    return False

def remove_watchword(discord_id, watchword=[], type='self'):

  cur = conn.cursor()
  if watchword:
    if type == 'transfer':
      cur.execute(f"DELETE FROM watchlist WHERE discord_id='{discord_id}' and watchword='{watchword}' AND type = 'transferto';")
      cur.execute(f"DELETE FROM watchlist WHERE discord_id='{discord_id}' and watchword='{watchword}' AND type = 'transferfrom';")
    elif type == 'vote':
      cur.execute(f"DELETE FROM watchlist WHERE discord_id='{discord_id}' and watchword='{watchword}' AND type = 'votein';")
      cur.execute(f"DELETE FROM watchlist WHERE discord_id='{discord_id}' and watchword='{watchword}' AND type = 'voteout';")
    else:
      cur.execute(f"DELETE FROM watchlist WHERE discord_id='{discord_id}' and watchword='{watchword}' AND type = '{type}';")
  else:
    cur.execute(f"DELETE FROM watchlist WHERE discord_id='{discord_id}' and type = '{type}';")

  cur.close()
  conn.commit()

#pause_notify(discord_id, type='pause')


def purge_user(discord_id):

  cur = conn.cursor()
  cur.execute(f"DELETE FROM watchlist WHERE discord_id='{discord_id}';")
  cur.close()
  conn.commit()


def get_settings(discord_id, type='word'):
  cur = conn.cursor()
  cur.execute(f"SELECT * FROM watchlist where discord_id='{discord_id}' AND type = '{type}';")

  result =  cur.fetchall()

  watchlist = []
#  replylist = []

  for word in result:
#    if word[3] = 'word'
      watchlist.append(word[2])
#    if word[3] = 'reply'
#      replylist.append(word[2])
  cur.close()
  return watchlist

def get_pending_notifications():
  cur = conn.cursor()
  cur.execute(f"SELECT * FROM pending_notifications")
  result =  cur.fetchall()

  notifications=[]

  for notify in result:
    notifications.append(notify)

  cur.close()

  return notifications


def remove_pending_notifications(authorperm, discord_id, type, watchword):

  cur = conn.cursor()
  if authorperm:
    cur.execute(f"DELETE FROM pending_notifications WHERE targets='{discord_id}' AND authorperm='{authorperm}' AND watchword = '{watchword}' AND type = '{type}';")
  else:
    cur.execute(f"DELETE FROM pending_notifications WHERE targets='{discord_id}' AND watchword = '{watchword}' AND type = '{type}';")

  cur.close()
  conn.commit()


def get_command(message):
    usr = []
    msg = []
    cmd = []
    cmds = []
    cmdlist = []
    usrs = []

    try:
        cmds, usrs = message.content.split(":")
    except Exception as e:
        msg = "Sorry, I'm only a simple bot, I can't work out what " + f'"{message.content}" is asking for. If you\'re unsure of what to do type "$help" for examples.'

    if usrs:
      usr = usrs.split(",")
      for idx,u in enumerate(usr):
        if u[0] == " ":
          usr[idx] = usr[idx][1:]
        if u[-1] == " ":
          usr[idx] = usr[idx][:-1]
    else:
       msg = "Sorry I'm not able to work out who/what you want to track. Please check your syntax ```$notify command: user/word/phrase```"
    
    if cmds:
      cmdlist = cmds.split(" ")
      if cmdlist[0] == "$notify":
        cmdlist = cmdlist[1:]
    else:
      msg = "Sorry I'm not able to work out who/what you want to track. Please check your syntax ```$notify command: user/word/phrase```"

    return usr, cmdlist, msg

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if not message.content.startswith('$'):
        return

    msg = []
    usr = []
    cmdlist = []
#    try:
#        cmd, usr = message.content.split(" ")
#    except Exception as e:
#        msg = "Sorry, I'm only a simple bot, I can't work out what " + f'"{message.content}" is asking for. Please only put 1 word after the command.'


    if message.content.startswith('$hello'):
        msg = 'Hello {0.author.mention}'.format(message)
#        await client.send_message(message.channel, msg)

## ================= Display Watch WOrds / Users ================= ##

    msg_start = ['Your Current Mention Watch List:',
                 'Your Current Replies Watch List:',
                 'Your Current Authors Watch List:',
                 'Your Current Transfer To Watch List:',
                 'Your Current Transfer From Watch List:',
                 'Your Current Transfer Watch List:',
                 'Your Current Powerdown Watch List:',
                 'Your Current Vesting Withdrawl Watch List:',
                 'Your Current Incoming Upshares Watch List:',
                 'Your Current Outgoing Upshares Watch List:',
                 'Your Current Upshares Watch List:',
                 'Your Current Tags Watch List:',
                 'Your Current Witness Vote Alert List:',
                 'Your Current Witness Block Production Alert List:',
                 'Daily Witness Block Production Reports:',
                 'Your Witness Missed Block Watch List:',
                 'New Followers Watch List:',
]

    notify_options = ['word', 'reply', 'author', 'transferto', 'transferfrom', 'transfer', 'powerdown', 'vestswithdrawl', 'votein', 'voteout', 'vote', 'tag', 'witnessvote', 'witnessblock', 'blockproductionreport', 'missedblock', 'follow']

    if message.content.startswith('$settings'): 
        have_response = False

        for idx, type in enumerate(notify_options):
          watchlist = get_settings(f"{message.author.id}", type)
          if watchlist:
            if not have_response:
              msg = ''
            else:
              msg += '\n'
            msg += msg_start[idx]
            msg += f" ['{watchlist[0]}'"
            for word in watchlist:
              if word != watchlist[0]:
                msg += f", '{word}'"
            msg += ']'
            have_response = True

        if not have_response:
          msg = 'Nothing Found!. Please type "$help" to see what I can do.'

## ================= Update DB with Watch Words / Users ================= ##
    possible_commands = ['mention', 'reply', 'author', 'transferto', 'transferfrom', 'transfer', 'powerdown', 'vestswithdrawl', 'votein', 'voteout', 'vote', 'tag', 'witnessvote', 'witnessblock', 'blockproductionreport', 'missedblock', 'follow']
    needs_account = ['reply', 'author', 'transferto', 'transferfrom', 'transfer', 'powerdown', 'vestswithdrawl', 'votein', 'voteout', 'vote', 'witnessvote', 'witnessblock', 'blockproductionreport', 'missedblock', 'follow']

    basic_add_messages = ['"{0}" has been added to your watchlist, you will be notified if {0} is mentioned in a post and/or comment',
                          '"{0}" has been added to your watchlist, you will be notified of replies to "{0}"',
                          '"{0}" has been added to your watchlist, you will be notified if "{0}" posts on whaleshares',
                          '"{0}" has been added to your watchlist, you will now be notified of transfers to "{0}\'s" account',
                          '"{0}" has been added to your watchlist, you will now be notified of transfers from "{0}\'s" account',
                          '"{0}" has been added to your watchlist, you will now be notified of all transfers involving "{0}"',
                          '"{0}" has been added to your watchlist, you will now be notified when "{0}" changes a powerdown',
                          '"{0}" has been added to your watchlist, you will now be notified when "{0}" gets a vesting withdrawl',
                          '"{0}" has been added to your watchlist, you will now be notified of incoming upshares to "{0}"',
                          '"{0}" has been added to your watchlist, you will now be notified of outgoing upshares from "{0}"',
                          '"{0}" has been added to your watchlist, you will now be notified of all upshares involving "{0}"',
                          '"{0}" has been added to your watchlist, you will now be notified when someone posts using the "{0}" tag',
                          '"{0}" has been added to your watchlist, you will now be notified when someone votes for  "{0}" as witness',
                          '"{0}" has been added to your watchlist, you will now be notified when "{0}" produces a block',
                          '"{0}" has been added to your watchlist, you will recieve a daily notification of "{0}\'s" block production stats',
                          '"{0}" has been added to your watchlist, you will now be notified when "{0}" misses a block',
                          '"{0}" has been added to your watchlist, you will now be notified when someone follows or unfollows "{0}"',
                         ]

    basic_remove_messages = ['You will no longer be notified if "{}" is mentioned',
                             'You will no longer be notified of replies to "{}"',
                             'You will no longer be notified of "{}\'s" posts',
                             'You will no longer be notified of transfers to "{}\'s" account',
                             'You will no longer be notified of transfers from "{}\'s" account',
                             'You will no longer be notified of transfers involving "{}"',
                             'You will no longer be notified when "{}" changes a powerdown',
                             'You will no longer be notified when "{}" gets a vesting withdrawl',
                             'You will no longer be notified of incoming upshares to "{0}"',
                             'You will no longer be notified of outgoing upshares from "{0}"',
                             'You will no longer be notified of upshares involving "{0}"',
                             'You will no longer be notified when someone posts using the "{0}" tag',
                             'You will no longer be notified when someone votes for  "{0}" as witness',
                             'You will no longer be notified when "{0}" produces a block',
                             'You will no longer recieve a daily notification of "{0}\'s" block production stats',
                             'You will no longer be notified when "{0}" misses a block',
                             'You will no longer be notified when someone follows or unfollows "{0}"',
                            ]

    if message.content.startswith('$notify-self'):
      if not already_exists(f"{message.author.id}", type='self'):
         add_watchword(f"{message.author.id}",type='self')
         msg = 'You will now be notified if someone replies to themselves'
      else:
         remove_watchword(f"{message.author.id}", type='self')
         msg = 'You will no longer be notified if someone replies to themselves'

    elif message.content.startswith('$ignore'):
      try:
        usr = message.content.split(" ")[1]
        viable = True
      except Exception as e:
        viable = False
        msg = f"Sorry I can't understand what you're trying to say. To ignore users please use the command like this ```$ignore comedyopenmic```"
      if viable:
        if not already_exists(f"{message.author.id}", usr, type='ignore'):
           add_watchword(f"{message.author.id}",usr, type='ignore')
           msg = 'You are now ignoring when "{0}" mentions one of your watchwords'.format(usr)
        else:
           remove_watchword(f"{message.author.id}", usr, type='ignore')
           msg = 'You are no longer ignoring when "{0}" mentions one of your watchwords'.format(usr)

    elif message.content.startswith('$mute'):
      if not already_exists(f"{message.author.id}", type='mute'):
         add_watchword(f"{message.author.id}", type='mute')
         msg = 'You will stop receiving notifications. Please note when you turn me back on, I will catch you up on all missed notifications'
      else:
         remove_watchword(f"{message.author.id}", type='mute')
         msg = 'Services have returned to normal, you will now get all your pending notifications.'

    elif message.content.startswith('$purge'):
        if already_exists(f"{message.author.id}"):
            purge_user(f"{message.author.id}")
            msg = "{0.author.mention}, you have been removed from my database. Hope it wasn't anything personal.".format(message)
        else:
            msg = "{0.author.mention}, I can't find any record of you.\n\n Type !help for a list of my commands.".format(message)

    elif message.content.startswith('$help'):
       msg = """Hi, I'd like to introduce myself, I'm Herbie. I heard you might need some help on what commands you can use\n
Here's a current list of all of my commands:\n
To get my attention type ```!notify``` Then you can use any of the below key words to describe what you want to do.
"mention" - Get notifications if someone mentions your word.
"reply" - Get notifications if someone replies to user.
"author" - Get notifications if a user posts.
"transferto" - Get notifications if someone sends wls to a user.
"transferfrom" - Get notifications if someone sends wls to another user.
"transfer" - Get notifications for all transactions into and out of someone's wallet.
"vestswithdrawl" - Get a notification when an a vesting withdrawl is paid out
"votein" - Get notifications if a **post** by username gets rewarded.
"voteout" - Get notifications if username rewards a post.
"vote" - Get notifications of both, incoming and outgoing rewards involving username.
"tag" - Get notifications of posts in a particular tag.
"witnessvote" - Get notified when someone gets a vote for witness.
"witnessblock" - Get notifications when a witness produces a block.
"blockproductionreport" - Get daily reports on block production for a witness.
"follow" - Alerts on new follow/unfollow.

Examples of use:
```$notify mention reply author: comedyopenmic```
```$notify reply: comedyopenmic```
```$notify mention reply author transfer witnessvote: comedyopenmic```
```$notify mention reply author transfer witnessvote: comedyopenmic, profanereviews```
**Additional commands:**
$help - See this message again
$settings - Display all of your current alert triggers.
$mute - Temporarily stop receiving notificaitons.
$ignore username - ignore when username mentions one of your watchwords.
$purge - Remove all traces of your account from database.
**To remove a trigger from one of your watch lists, just send the message again**\n
If you notice any issues with me please talk to @idikuci, it's all his fault.
"""

    elif message.content.startswith('$notify'):
      usrlist, cmdlist, msg = get_command(message) # See what they want to do
      if usrlist: # Check what they're asking for is valid
        for usr in usrlist:
          if usr:
            for cmd in cmdlist :
              if cmd:
                try:
#              print(f"|{cmd}|")
                  idx = possible_commands.index(cmd)
#              print(f"IDX: {idx}")
                  notify_tag = notify_options[idx]
#              print(len(basic_add_messages))
                except:
                  notify_tag = []
                  msg = f'Unable to find "{cmd}" in my command list, see $help for details'
                  await client.send_message(message.author, msg)
                  idx = []
#              await client.wait_until_ready()
                  msg = []
                if notify_tag:
                  if cmd in needs_account:
                    if not account_exists(usr): # Check it's actually an account on wls chain
                      msg = f'"{usr}" isn\'t a valid account, please check your spelling. Unable to perform change to "{cmd}" watchlist'
                      await client.send_message(message.author, msg)
                      msg = []
                      continue
 #                break
 #             print(f"account Exists {usr}")
                  if not already_exists(f"{message.author.id}", usr, notify_tag): # Check if command already processed
 #             print('Add Watch Word')
                    add_watchword(f"{message.author.id}", usr, notify_tag) # Add notification to db
                    msg = basic_add_messages[idx].format(usr)
                    await client.send_message(message.author, msg)
                    msg = []
                  else :
                    remove_watchword(f"{message.author.id}", usr, notify_tag)
                    msg = basic_remove_messages[idx].format(usr)
                    await client.send_message(message.author, msg)
                    msg = []


    if msg:
       try:
         print(f"Talking to: {message.author}")
         await client.send_message(message.author, msg)
         logger.info(f"Spoke to: {message.author}")
       except Exception as e:
         logger.error(f"Unable to respond to {message.author} - {e}")
         if message.content.startswith('$help'):
           await client.send_message(message.channel,msg)
         await client.send_message(message.channel, f"{message.author}, I tried sending you a DM but failed I got this error ```{e}```")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

async def my_background_task():

  embed = []

  await client.wait_until_ready()
  msg_word    = '"{0[2]}" has just been mentioned:\n\n{0[0]}'
  msg_reply   = '"{0[3]}" has just replied to "{0[2]}":\n\n{0[0]}'
  msg_author  = '"{0[2]}" has just posted:\n\n{0[0]}'
  msg_self    = '"{0[2]}" has just replied to themselves:\n\n{0[0]}'
  msg_trans   = '"{0[2]}" has just sent {0[5]} to "{0[3]}" at {0[0]}:\n\n From:```https://smoke.io/@{0[2]}/transfers```\n To:```https://smoke.io/@{0[3]}/transfers```'
  msg_vote    = '"{0[2]}" has just rewarded a post by "{0[3]}"\n\n{0[0]}'
  msg_witvote = '"{0[3]}" has just {0[5]} "{0[2]}" as witness'
  msg_bp      = '"{0[2]}" has just produced a block.\n\nProduction Reward: {0[5]}\nBlock Number Produced: {0[0]}'
  msg_bpr     = 'Daily Production Report for "{0[2]}" Dated {0[0]}:\nNumber Of Blocks Produced: {0[3]}\nProduction Rewards: {0[5]}'
  msg_tag     = '"{0[3]}" has just tagged "{0[2]}" in a post:\n\n{0[0]}'
  msg_mb      = '"{0[2]}" has just missed a block. It would be a good time to check on your witness'


  while not client.is_closed:

    pend_notify = get_pending_notifications()
#    print(f"going to cycle through {len(pend_notify)} Entries")

    for notify in pend_notify:
      usrID = notify[1]
      if already_exists(usrID, type='mute'):
        continue

#      print(usrID)
#      print(f"notify {notify}")
      try:
        Discord_id_watcher = await client.get_user_info(int(usrID))
        print(Discord_id_watcher)
      except Exception as e:
        print(f'Error trying to get user id: {e}')
        logger.error(f'Error trying to get user id: {usrID} - {e}')
        Discord_id_watcher = []
#      if notify[6]:
#        print(notify[6])
      #  Change output message based on what just happened
      if notify[4] == 'word':
        snd_msg = msg_word.format(notify)
        embed = discord.Embed(title="Mention Alert", description=f'"{notify[2]}" has been mentioned.', color=0x4ed35d)
        embed.add_field(name="Link To Mention", value=notify[0], inline=False)
        if notify[6]:
#          print(notify[6])
          embed.set_footer(text=f"Message: {notify[6]}")
#        embed.add_field(name="Field2", value="hi2", inline=False)

      elif notify[4] == 'reply':
        snd_msg = msg_reply.format(notify)
        embed = discord.Embed(title="Reply Alert", description=f'"{notify[3]}" has replied to "{notify[2]}".', color=0xff0000)
        embed.add_field(name="Link To Reply", value=notify[0], inline=False)
        if notify[6]:
          embed.set_footer(text=f"Message: {notify[6]}")

      elif notify[4] == 'author':
        snd_msg = msg_author.format(notify)
        embed = discord.Embed(title="New Post Alert", description=f'"{notify[2]}" has posted.', color=0x0000ff)
        embed.add_field(name="Link To Post", value=notify[0], inline=False)
        if notify[6]:
          embed.set_footer(text=f"Message: {notify[6]}")

      elif notify[4] == 'self':
        snd_msg = msg_self.format(notify)

      elif 'transfer' in notify[4]:
        snd_msg = msg_trans.format(notify)
        embed = discord.Embed(title="Transfer Alert", description=f'"{notify[2]}" has sent "{notify[5]}" to "{notify[3]}".', color=0xedf47a)
        embed.add_field(name="Link To Sender", value=f"https://smoke.io/@{notify[2]}/transfers", inline=False)
        embed.add_field(name="Link To Recipient", value=f"https://smoke.io/@{notify[3]}/transfers", inline=False)
        if notify[6]:
          embed.set_footer(text=notify[6])

      elif notify[4] == 'votein': # or notify[4] == 'voteout':
        snd_msg = msg_vote.format(notify)
        embed = discord.Embed(title="Incoming Reward Alert", description=f'"{notify[2]}" has rewarded a post authored by "{notify[3]}".', color=0xfed029)
        embed.add_field(name="Link To Post", value=notify[0], inline=False)
#        embed.add_field(name="Link To Recipient", value="https://whaleshares.io/@{notify[3]}/transfers", inline=False)
      elif notify[4] == 'voteout':
        snd_msg = msg_vote.format(notify)
        embed = discord.Embed(title="Outgoing Reward Alert", description=f'"{notify[2]}" has rewarded a post authored by "{notify[3]}".', color=0xfed029)
        embed.add_field(name="Link To Post", value=notify[0], inline=False)

      elif notify[4] == 'witnessvote':
        snd_msg = msg_witvote.format(notify)
        embed = discord.Embed(title="Witness Vote Alert", description=f'"{notify[3]}" has {notify[5]} "{notify[2]}" as witness.', color=0xecaf02)
#        embed.add_field(name="Link To Post", value=notify[0], inline=False)

      elif notify[4] == 'witnessblock':
        snd_msg = msg_bp.format(notify)
#  msg_bp      = '"{0[2]}" has just produced a block.\n\nProduction Reward: {0[5]}\nBlock Number Produced:
        embed = discord.Embed(title="Block Production Alert", description=f'"{notify[2]}"  has produced a block.', color=0xe8790a)
        embed.add_field(name="Block Number", value=notify[0], inline=True)
        embed.add_field(name="Producer Reward", value=notify[5], inline=True)

      elif notify[4] == 'blockproductionreport':
        snd_msg = msg_bpr.format(notify)
        if notify[0]:
          embed = discord.Embed(title="Daily Block Production Report", description=f'Summary of blocks produced by "{notify[2]}".', color=0xff5f0b)
          embed.add_field(name="Date", value=notify[0], inline=False)
          embed.add_field(name="Number of Blocks Produced", value=notify[3], inline=True)
          embed.add_field(name="Producer Reward", value=notify[5], inline=True)
        else :
          snd_msg = "The account you have requested a block production report for \"{notify[2]}\" did not produce a block yesterday: {notify[0]}, Please double check that they are a witness"
          embed = []

      elif notify[4] == 'tag':
        snd_msg = msg_tag.format(notify)
        embed = discord.Embed(title="New Post in Tag Alert", description=f'"{notify[3]}" has tagged "{notify[2]}" in a post.', color=0xffffff)
        embed.add_field(name="Link To Post", value=notify[0], inline=False)

      elif notify[4] == 'missedblock':
        snd_msg = msg_mb.format(notify)
        embed = discord.Embed(title="Missed Block", description=f'"{notify[2]}" has missed a block. It might be a good idea to check on it', color=0xffd909)

      elif notify[4] == 'vestswithdrawl':
        snd_msg = msg_mb.format(notify)
        embed = discord.Embed(title="Vests have paid out", description=f'"{notify[2]}" has just had "{notify[5]}" become liquid.', color=0x80e7e5)

      elif notify[4] == 'powerdown':
        snd_msg = msg_mb.format(notify)
        if notify[5] > 0:
          embed = discord.Embed(title="Powerdown Started", description=f'"{notify[2]}" has started a powerdown of "{notify[5]}" WLS.', color=0xfdbfbf)
        else:
          embed = discord.Embed(title="Powerdown Stopped", description=f'"{notify[2]}" has stoped powerdown.', color=0xfdbfbf)

      elif notify[4] == 'follow':
          if notify[0] == 'following':
            embed = discord.Embed(title="New Follower", description=f'"{notify[3]}" is now {notify[0]} "{notify[2]}"', color=0x0054d6)
          else:
            embed = discord.Embed(title="Lost Follower", description=f'"{notify[3]}" has {notify[0]} "{notify[2]}"', color=0x0054d6)

#      await client.send_message(this, snd_msg)
      if Discord_id_watcher:
        if embed:
          try:
            await client.send_message(Discord_id_watcher, embed = embed)
            print(Discord_id_watcher)
#            print(len(pend_notify))
            embed = []
          except Exception as e:
            print(e)
            logger.error(f"Trying to message User: {Discord_id_watcher} - {e}")
            embed = []
#            remove_pending_notifications(notify[0], notify[1], notify[4], notify[2])
#            continue
        elif snd_msg:
          await client.send_message(Discord_id_watcher, snd_msg)
#      print(f"First spot: {notify[0]} | {notify[1]} |  {notify[4]} | {notify[2]}")
        remove_pending_notifications(notify[0], notify[1], notify[4], notify[2])

    await asyncio.sleep(10)
#    sleep(60)

try:
  client.loop.create_task(my_background_task())
  client.run(TOKEN)
except (KeyboardInterrupt, SystemExit):
     conn.close()
     Print("leaving safetly")
     raise
