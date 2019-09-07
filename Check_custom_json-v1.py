# Work with Python 3.6
#import discord
#client.run(TOKEN)
import psycopg2
from beem.steem import Steem
from beem.comment import Comment
import ast
import json


URL = "https://smoke.io/"

# Connect to Database
cur = None
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


def get_unproceed_blocks():
  cur = conn.cursor()
  cur.execute(f"SELECT * FROM pending_custom_json;")

  result =  cur.fetchall()
  pendinglist=[]
  for word in result:
    pendinglist.append(word)

  cur.close()
  return pendinglist

def get_watcherslist(word, type):
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



def store_watchers(watchers, status, follower, followee, type, blocknum):

  try:
    cur = conn.cursor()
 # cur.execute(f"SELECT DISTINCT watchword FROM watchlist")
    for watcher in watchers:
      cur.execute("""INSERT INTO pending_notifications (authorperm, targets, watchword, type, author, amount) VALUES (%s, %s, %s, %s, %s, %s);""", (status, watcher, followee, type, follower, blocknum) )


    cur.close()
    conn.commit()

    return True


  except Exception as e:
    print(f"Error with Storing watchers: {e}")
    return False

def mark_completed(jsondata, blocknum):
  cur = conn.cursor()
  cur.execute(f"DELETE FROM pending_custom_json WHERE json ='{jsondata}' AND blocknum='{blocknum}';")
  cur.close()
  conn.commit()

  

if __name__ == '__main__':

  all_posts = get_unproceed_blocks()

  for post in all_posts:

    success = True
    print(post)
#    sleep(10)
    action   = post[1]
    jsondata = post[2]
    blocknum = post[3]

#    print(action)
    if action == 'follow':
      print(jsondata)
      listofdata = ast.literal_eval(jsondata)
#      print(listofdata)
      typeit = listofdata[0]
      if typeit == 'follow':
        jsondict = listofdata[1]
        print(jsondict)
#      print(jsondict['follower'])
#      print(jsondict['what'])

        watchers = get_watcherslist(jsondict['following'], 'follow')

        follower = jsondict['follower']
        followee = jsondict['following']

#      print('watchers: ' + str(watchers))

        if watchers:
          if not jsondict['what']:
            action = 'unfollowed'
          else:
            action = 'following'

          success = store_watchers(watchers, action, follower, followee, 'follow', blocknum)

      if success :
#      mark_completed(post[0])
        mark_completed(jsondata, blocknum)
        
