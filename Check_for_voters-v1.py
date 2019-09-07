# Work with Python 3.6
#import discord
#client.run(TOKEN)
import psycopg2
from beem.steem import Steem
from beem.comment import Comment

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


def get_unproceed_blocks():
  cur = conn.cursor()
  cur.execute(f"SELECT * FROM pending_votes;")

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



def store_watchers(watchers, authorperm, voter, type, author, vote_weight):

  try:
    cur = conn.cursor()
 # cur.execute(f"SELECT DISTINCT watchword FROM watchlist")
    for watcher in watchers:
      cur.execute("""INSERT INTO pending_notifications (authorperm, targets, watchword, type, author, amount) VALUES (%s, %s, %s, %s, %s, %s);""", (authorperm, watcher, voter, type, author, vote_weight) )


    cur.close()
    conn.commit()

    return True


  except Exception as e:
    print(f"Error with Storing watchers: {e}")
    return False

def mark_completed(authorperm):
  cur = conn.cursor()
  cur.execute(f"DELETE FROM pending_votes WHERE authorperm='{authorperm}';")
  cur.close()
  conn.commit()

  

if __name__ == '__main__':

  nodes = ['https://rpc.smoke.io/']
  w = Steem(node=nodes)

  votesin  = get_all_words('votein')
  votesout = get_all_words('voteout')
#  authorlist = get_all_words('author')
  all_posts = get_unproceed_blocks()

  for post in all_posts:
#    commentobj = Comment(authorperm, steem_instance = w)

    success = True
#    print(post)
#    sleep(10)
    authorperm = post[0]
    author     = post[1]
    voter      = post[6]
    vote_weight= post[7]

#    print(post)

    try: 
      commentobj = Comment(authorperm, steem_instance = w)
    except: 
      commentobj = []
    

#p    print(commentobj)
    if commentobj:
      if commentobj.is_main_post():
        print(" Is Main Post")
        WLS_URL = make_URL(authorperm)
        for poster in votesin:
          if poster == author:
            print("  Watching Author")
            success = False
            watchers = get_watcherslist(poster,'votein')
            success = store_watchers(watchers, WLS_URL, voter, 'votein', author, vote_weight)
            break

        for Pvoter in votesout:
          if Pvoter == voter:
            print("   Watching voter")
            success = False
            watchers = get_watcherslist(Pvoter, 'voteout')
            success = store_watchers(watchers, WLS_URL, voter, 'voteout', author, vote_weight)
            break

    if success :
      mark_completed(post[0])
        
        

#  print(all_posts)

 # client.close()
