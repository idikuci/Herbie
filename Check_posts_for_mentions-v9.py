# Work with Python 3.6
#import discord
#client.run(TOKEN)
import psycopg2
import regex as re

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
  cur.execute(f"SELECT * FROM pending_posts;")

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

def check_self_replies():
  cur = conn.cursor()
  cur.execute(f"SELECT * FROM watchlist where type = 'self'")
  result =  cur.fetchall()
  print(len(result))
  if len(result)> 0:
    return True
  else:
    return False

def make_URL(authorperm):
  return URL + authorperm



def store_watchers(watchers,authorperm, watchword, type, author, additional_text = []):

  try:
    cur = conn.cursor()
 # cur.execute(f"SELECT DISTINCT watchword FROM watchlist")
    for watcher in watchers:
      if type == 'word':
        cur.execute("""SELECT COUNT(*) FROM watchlist WHERE watchword = %s and discord_id = %s and type = 'ignore'""",(author, watcher))
        res = cur.fetchall()[0][0]
#        print)
        print(f"{watcher}: {watchword} : {type}")
      else:
        res = 0
      print(res)
      if res < 1:
        print("notifying")
        if not additional_text:
          cur.execute("""INSERT INTO pending_notifications (authorperm, targets, watchword, type, author) VALUES (%s, %s, %s, %s, %s);""", (authorperm, watcher, watchword, type, author) )
        else:
          cur.execute("""INSERT INTO pending_notifications (authorperm, targets, watchword, type, author, ad_text) VALUES (%s, %s, %s, %s, %s, %s);""", (authorperm, watcher, watchword, type, author, additional_text) )

    cur.close()
    conn.commit()

    return True


  except Exception as e:
    print(f"Error with Storing watchers: {e}")
    return False

def mark_completed(authorperm):
  cur = conn.cursor()
  cur.execute(f"DELETE FROM pending_posts WHERE authorperm='{authorperm}';")
  cur.close()
  conn.commit()

  

if __name__ == '__main__':

  wordslist = get_all_words('word')
  replylist = get_all_words('reply')
  authorlist = get_all_words('author')
  all_posts = get_unproceed_blocks()

  for post in all_posts:
    success = True
#    print(post)
#    sleep(10)
    body = post[3]
    parent_author = post[6]
    author = post[1]
    strtags = post[7]
    tags = [s.strip() for s in strtags[1:-1].split(',')]
#    tags = post[7]

#    print(tags)
#    print(tag[0])

#    if any(substring.casefold() in body.casefold() for substring in wordslist):
    WLS_URL = make_URL(post[0])

    for curr_word in wordslist:
      if re.search(r"\b" + re.escape(curr_word.casefold()) + r"\b", body.casefold()) or re.search(r"\b@" + re.escape(curr_word.casefold()) + r"\b", body.casefold()):
        success = False
#        WLS_URL = make_URL(post[0])
        watchers = get_watcherslist(curr_word,'word')
        if len(body) >= 200:
          success = store_watchers(watchers, WLS_URL, curr_word, 'word', author)
        else:
          success = store_watchers(watchers, WLS_URL, curr_word, 'word', author, body)

    for parent in replylist:
      if parent == parent_author:
        success = False
#        WLS_URL = make_URL(post[0])
        watchers = get_watcherslist(parent, 'reply')
        if len(body) >= 200:
          success = store_watchers(watchers,WLS_URL, parent, 'reply', author)
        else:
          success = store_watchers(watchers,WLS_URL, parent, 'reply', author, body)

#    print(f"All Authors: {authorlist}")
    for suspect_author in authorlist:
#      print(author)
      if suspect_author == author and not parent_author:
        success = False
#        WLS_URL = make_URL(post[0])
        watchers = get_watcherslist(suspect_author, 'author')
        if len(body) >= 200:
          success = store_watchers(watchers,WLS_URL, suspect_author, 'author', author)
        else:
          success = store_watchers(watchers,WLS_URL, suspect_author, 'author', author, body)

    if not parent_author: # If Post
#        print('Post')
        for tag in tags: #
#            print(f'tags : {tag}')
            watchers = get_watcherslist(tag, 'tag') # Check if anyone is interested in tags of post
#            print(f"watchers: {watchers}")
            if watchers: # If they are, notify
                success = False
                success = store_watchers(watchers, WLS_URL, tag, 'tag', author)


    if check_self_replies:
      if author == parent_author:
       watchers = get_watcherslist([], 'self')
       success = store_watchers(watchers, WLS_URL, author, 'self', author)


    if success :
      mark_completed(post[0])
        
        

#  print(all_posts)

 # client.close()
