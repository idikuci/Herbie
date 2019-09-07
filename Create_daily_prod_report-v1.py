# Work with Python 3.6
import psycopg2

from datetime import date, timedelta

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


def get_full_prod_report():
  cur = conn.cursor()
  cur.execute(f"select DISTINCT witness, count(witness), sum(payment::float) from block_production_history where date_trunc('day', timestamp) = current_date - INTERVAL '1 day' group by witness;")
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
    watcherslist.append(word)
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



def store_watchers(witness, num_block, payout, discord_id, date, type):

  try:
    cur = conn.cursor()
 # cur.execute(f"SELECT DISTINCT watchword FROM watchlist")
#    for watcher in watchers:
    cur.execute("""INSERT INTO pending_notifications (authorperm, targets, watchword, author, type, amount) VALUES (%s, %s, %s, %s, %s, %s);""", (date, discord_id, witness, num_block, type, payout) )

    cur.close()
    conn.commit()

    return True


  except Exception as e:
    print(f"Error with Storing watchers: {e}")
    return False

def mark_completed(witness, blocknum, conn):

  cur = conn.cursor()
  cur.execute(f"DELETE FROM pending_witness_blocks WHERE witness = '{witness}' AND blocknum = '{blocknum}';")
  cur.close()
  conn.commit()

  

if __name__ == '__main__':

  reports    = get_full_prod_report()
  witnesses  = []
  yesterday  = date.today() - timedelta(1)
  todaysdate = yesterday.strftime('%Y-%m-%d')

  for r in reports:
    witnesses.append(r[0])

  requested_details = get_watcherslist(type='blockproductionreport')
#  print(requested_details)
  print(reports)

  for info in requested_details:
#    commentobj = Comment(authorperm, steem_instance = w)
#    print
    try:
      targeting = witnesses.index(info[2])
      details   = reports[targeting]
      witness   = details[0]
      num_block = details[1]
      payout    = details[2]
    except:
      targeting = []
      witness   = []
      num_block = []
      payout    = []

    print(info)

    store_watchers(info[2], num_block, payout, info[1], todaysdate, 'blockproductionreport')
