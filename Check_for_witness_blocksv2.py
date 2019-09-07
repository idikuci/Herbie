# Work with Python 3.6
#import discord
#client.run(TOKEN)
import psycopg2
from beem.steem import Steem
from beem.comment import Comment

#TOKEN = 'NTM2ODQyNzkyMjQ1Mzk1NDY2.DycqeA.w2hX73vXRTXvmS9iOJR_SwgV38Y'

#client = discord.Client()

URL = "https://smoke.io/"

# Connect to Database
cur = None
conn = None
try:
    connect_str = "dbname='smoke' user='root' host='localhost' " + \
                  "password='DJisaBeast'"
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    # create a psycopg2 cursor that can execute queries
#    cursor = conn.cursor()
except Exception as e:
    print(f"Invalid dbname, user or password? - {e}")
    logger.error(f"Invalid dbname, user or password? - {e}")

if False:
  cur = conn.cursor()
  sql_command= """CREATE TABLE IF NOT EXISTS pending_notifications(
                  authorperm varchar(1050),
                  targets TEXT
                  )
               """
  cur.execute(sql_command)
  cur.close()
  conn.commit()


def get_unproceed_blocks(table):
  cur = conn.cursor()
  cur.execute(f"SELECT * FROM {table};") #pending_witness_blocks;")

  result =  cur.fetchall()
  pendinglist=[]
  for word in result:
    pendinglist.append(word)

  cur.close()
  return pendinglist

def get_watcherslist(word=[], type=[]):
  cur = conn.cursor()
  if word:
    cur.execute(f"SELECT * FROM watchlist where watchword='{word}' AND type = '{type}';")
  else:
    cur.execute(f"SELECT * FROM watchlist where type = '{type}';")

  result =  cur.fetchall()

  watcherslist=[]

  for word in result:
    watcherslist.append(word[1])
  cur.close()
  return watcherslist

def get_all_words(type):
  cur = conn.cursor()
  cur.execute(f"SELECT DISTINCT watchword FROM watchlist where type = '{type}'")
#  cur.execute(f"SELECT discord_id FROM watchlist where watchword = '{word}' and type = '{type}'")
  result =  cur.fetchall()

  wordlist    = []
#  print(result)
  for record in result:
#    print(record)
    word = record[0]
#    print(word)
#    if word not in wordlist:
    wordlist.append(word)
  cur.close()

  return wordlist

def make_URL(authorperm):
  return URL + authorperm



def store_watchers(watchers, block_num, witnessname, type, payout):

  try:
    cur = conn.cursor()
 # cur.execute(f"SELECT DISTINCT watchword FROM watchlist")
    for watcher in watchers:
      cur.execute("""INSERT INTO pending_notifications (authorperm, targets, watchword, type, amount) VALUES (%s, %s, %s, %s, %s);""", (block_num, watcher, witnessname, type, payout) )


    cur.close()
    conn.commit()

    return True


  except Exception as e:
    print(f"Error with Storing watchers: {e}")
    return False

def store_vest_watchers(watchers, fromaccount, amount, blocknum, type):

  try:
    cur = conn.cursor()
 # cur.execute(f"SELECT DISTINCT watchword FROM watchlist")
    for watcher in watchers:
      cur.execute("""INSERT INTO pending_notifications (targets, watchword, type, amount) VALUES (%s, %s, %s, %s);""", (watcher, fromaccount, type, amount) )
    cur.close()
    conn.commit()

    return True


  except Exception as e:
    print(f"Error with Storing watchers: {e}")
    return False



def copy_to_history(blocknum, witness, timing, payout, conn):
#  block_production_history
# witness   | character varying(55)       |
# timestamp | timestamp without time zone |
# blocknum  | numeric                     |
# payment   | character varying(55)       |

  cur = conn.cursor()
  cur.execute("""INSERT INTO block_production_history (witness, timestamp, blocknum, payment)
               SELECT %s, %s, %s, %s
               WHERE NOT EXISTS (SELECT blocknum FROM pending_posts WHERE blocknum = %s) ;
               """,
               (
               str(witness), str(timing), blocknum, payout,
               blocknum
               )
               )


  cur.close()
  conn.commit()
  pass

def mark_completed(witness, blocknum, conn):

  cur = conn.cursor()
  cur.execute(f"DELETE FROM pending_witness_blocks WHERE witness = '{witness}' AND blocknum = '{blocknum}';")
  cur.close()
  conn.commit()

def mark_vests_completed(fromaccount, blocknum, conn):

  cur = conn.cursor()
  cur.execute(f"DELETE FROM pending_vesting_withdrawl WHERE fromaccount = '{fromaccount}' AND blocknum = '{blocknum}';")
  cur.close()
  conn.commit()

  

if __name__ == '__main__':

#  nodes = ["ws://51.158.67.29:80/", "https://wls.kennybll.com"]
#  w = Steem(node=nodes)

#  witness  = get_all_words('witnessvote')
#  votesout = get_all_words('voteout')
#  authorlist = get_all_words('author')
  all_posts = get_unproceed_blocks('pending_witness_blocks')
  for post in all_posts:
    print(post)
    success = True

    witness  = post[0]
    timing   = post[1]
    blocknum = post[2]
    payout   = post[3]

    watchers = get_watcherslist(witness, 'witnessblock')

    if watchers:
      success = store_watchers(watchers, blocknum, witness, 'witnessblock', payout)
#def store_watchers(watchers, block_num, witnessname, type, payout):

#    if success :
    copy_to_history(blocknum, witness, timing, payout, conn)
    mark_completed( witness, blocknum, conn)
#      pass


  all_posts = get_unproceed_blocks('pending_vesting_withdrawl')
  for post in all_posts:
    print(post)
    success = True

    fromaccount = post[0]
    toaccount   = post[1]
    amount      = post[2]
    blocknum    = post[3]

    watchers = get_watcherslist(fromaccount,'vestswithdrawl')
#    if fromaccount !=  to account:

    if watchers:
      success = store_vest_watchers(watchers, fromaccount, amount, blocknum, 'vestswithdrawl')

#    if success:
    mark_vests_completed(fromaccount, blocknum, conn)

#  print(all_posts)

 # client.close()
