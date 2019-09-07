# Work with Python 3.6
#import discord
#client.run(TOKEN)
import psycopg2

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

def get_unproceed_blocks(table):
  cur = conn.cursor()
  cur.execute(f"SELECT * FROM {table};")

  result =  cur.fetchall()
  pendinglist=[]
  for word in result:
    pendinglist.append(word)

  cur.close()
  return pendinglist

def get_watcherslist(type, word=[]):

  cur = conn.cursor()
  if word:
    cur.execute(f"SELECT * FROM watchlist where watchword='{word}' AND type = '{type}';")
  else:
    cur.execute(f"SELECT * FROM watchlist where type = '{type}';")

  result =  cur.fetchall()
  watcherslist=[]

  print(f"raw: {result}")

  for word in result:
    watcherslist.append(word[1])
  cur.close()
  return watcherslist

def get_all_words(type):
  cur = conn.cursor()
  cur.execute(f"SELECT DISTINCT watchword FROM watchlist where type = '{type}'")
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


def store_watchers(watchers, fromaccount, toaccount, time, type, amount):
#    store_watchers(watchers, rank, witnessname, voter, type, status):

  try:
    cur = conn.cursor()
#    print(f"watchers: {watchers}")
    print(f"|{type}|")
    if type == 'witnessvote':
      rank = fromaccount
      witnessname = toaccount
      type = type
      voter = time
      status = amount
      print(status)

      for watcher in watchers:
        cur.execute("""INSERT INTO pending_notifications (authorperm, targets, watchword, type, author, amount) VALUES (%s, %s, %s, %s, %s, %s);""", (rank, watcher, witnessname, type, voter, status) )

    elif type == 'transferto' or type == 'transferfrom':
      for watcher in watchers:
        cur.execute("""INSERT INTO pending_notifications (targets, watchword, type, author, authorperm, amount) VALUES (%s, %s, %s, %s, %s, %s);""", (watcher, fromaccount, type, toaccount, time, amount) )

    cur.close()
    conn.commit()

    return True


  except Exception as e:
    print(f"Error with Storing watchers: {e}")
    return False

def mark_completed(toaccount, fromaccount, amount=[], time=[], table=[], blocknum = []):

  cur = conn.cursor()

  if table == 'pending_transfers':
    cur.execute(f"DELETE FROM {table} WHERE userto='{toaccount}' AND userfrom = '{fromaccount}' AND amount='{amount}' AND timestamp = '{time}';")
  elif table == 'pending_witness_votes':
    cur.execute(f"DELETE FROM {table} WHERE account='{toaccount}' AND witness = '{fromaccount}' AND blocknum = '{blocknum}';")

  cur.close()
  conn.commit()



if __name__ == '__main__':

  table = 'pending_transfers'
  transfertolist = get_all_words('transferto')
  transferfromlist = get_all_words('transferfrom')
  all_transfers = get_unproceed_blocks(table)

  for transfer in all_transfers:
    success = True
#    print(post)
    sendingto = transfer[0]
    sendingfrom = transfer[1]
    amount = transfer[2]
    memo = transfer[3]
    timestamp = transfer[4]
#    print('got transfer')

#    watchers = get_watcherslist('transferto', sendingto)

    if sendingto in transfertolist:
#      print('User in To List')
      success = False
      watchers = get_watcherslist('transferto', sendingto)
      success = store_watchers(watchers, sendingfrom, sendingto, timestamp, 'transferto', amount)

    if sendingfrom in transferfromlist:
#      print('User in From List')
      success = False
      watchers = get_watcherslist('transferfrom', sendingfrom)
      success = store_watchers(watchers, sendingfrom, sendingto, timestamp, 'transferfrom', amount)

    if success :
      mark_completed(sendingto, sendingfrom, amount, timestamp, table)




  table = 'pending_witness_votes'

  all_posts = get_unproceed_blocks(table)
  for post in all_posts:
    print(post)
    success = True
    voter    = post[0]
    witness  = post[1]
    approve  = post[2]
    blocknum = post[4]

    watchers = get_watcherslist('witnessvote', witness)
    print(witness)
    print(watchers)
    if watchers:
      print(approve)
      if approve:
        print('True')
        status = 'approved'
      elif not approve:
        print('False')
        status = 'disapproved'
      success = store_watchers(watchers, [], witness, voter, 'witnessvote', status)

    if success:
      mark_completed(voter, witness, blocknum= blocknum, table = table)
