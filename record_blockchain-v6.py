from beem.comment import Comment
from beem.steem import Steem
from beem.blockchain import Blockchain

import logging
import os
import psycopg2
import json

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
nodes = ['https://rpc.smoke.io/']

def connect_db(logger):
 # Connect to Database
  cursor = None
  conn = None
  try:
    connect_str = "dbname='smoke' user='XXXXXX' host='localhost' " + \
                  "password='XXXXXXXXX'"
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    return conn
  except Exception as e:
    return False
    print(f"Invalid dbname, user or password? - {e}")
    logger.error(f"Invalid dbname, user or password? - {e}")

def set_logger(loggername, DIR_PATH=""):
  # Set up logger for catching and recording errors
  if DIR_PATH == "":
    DIR_PATH = os.path.dirname(os.path.realpath(__file__))

  logger = logging.getLogger(f"{loggername}")
  logger.setLevel(logging.INFO)
  fh = logging.FileHandler(f"{DIR_PATH}/record_blocks.log")
  fh.setLevel(logging.DEBUG)
  formatter = logging.Formatter(
      "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  fh.setFormatter(formatter)
  logger.addHandler(fh)

  return logger


def create_tables(conn, logger):
    """ create tables in the PostgreSQL database"""
    command = """
            CREATE TABLE IF NOT EXISTS pending_posts(
            authorperm VARCHAR(255) PRIMARY KEY,
            author VARCHAR(55),
            title VARCHAR(255),
            body text,
            created TIMESTAMP NOT NULL,
            blocknum NUMERIC,
            parent_author VARCHAR(55),
            userto VARCHAR(55),
            userfrom VARCHAR(55),
            amount VARCHAR(55),
            message TEXT,
            voter VARCHAR(55),
            vote_percent NUMERIC
        )
        """
    cur = None
#    print(commands)
    try:
      cur = conn.cursor()
      print("# create tables one by one")
      cur.execute(command)
      # close communication with the PostgreSQL database server
      cur.close()
      # commit the changes
      conn.commit()
      return True
    except (Exception, psycopg2.DatabaseError) as error:
      # Print the error
      print(error)
      # Log the error
      logger.error(f"couldn't make tables: {error}")
      if cur is not None:
        cur.close()
      return False

def addpost_to_db(transaction, conn, logger):
  cur = conn.cursor()
#  print('Got Cursor')

#  print(transaction['author'])
#  print( transaction['permlink'])


  authorperm = "@" + transaction['author'] + "/" + transaction['permlink']
#  print(f"this one : {authorperm}")
  parent_authorperm = "@" + transaction['parent_author'] + "/" + transaction['parent_permlink']
#  print(f" Parent: {parent_authorperm}")

#  print(transaction['json_metadata'])

  try: 
    tags = json.loads(transaction['json_metadata'])['tags']
  except Exception as e:
    logger.error(f"Issue Loading Tags: {e}")
    tags = ""

  try:
    cur.execute("""
               INSERT INTO pending_posts (authorperm, author, title, body, created, parent_author, tags)
               SELECT %s, %s, %s, %s, %s, %s, %s
               WHERE NOT EXISTS (SELECT authorperm FROM pending_posts WHERE authorperm = %s) ;
               """,
               (
               str(authorperm), str(transaction['author']), str(transaction['title']), str(transaction['body']), str(transaction['timestamp']), transaction['parent_author'], tags,
               str(authorperm)
               )
               )
#    print('Execute command Add to DB success')
    conn.commit()
    cur.close()
    return True

  except (Exception, psycopg2.DatabaseError) as error:
    # Print the error
    print(f'Error in Add post To DB: {error}')
    # Log the error
    logger.error(f"Can't add post to DB: {error}")
    if cur is not None:
      cur.close()
    return False

def addtransfer_to_db(transaction, conn, logger):

  try:
#    print("get cursor")
    cur = conn.cursor()
#  print('Got Cursor')
#  try:

 #   print("adding")
    cur.execute("""
               INSERT INTO pending_transfers (userto, userfrom, amount, message, timestamp)
               SELECT %s, %s, %s, %s, %s
               """,
               (
               str(transaction['to']), str(transaction['from']), str(transaction['amount']), str(transaction['memo']), transaction['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
               )
               )
#    print('Execute command Add Transfer to DB - success')
    conn.commit()
    cur.close()
    return True

  except (Exception, psycopg2.DatabaseError) as error:
    # Print the error
    print(f'Error in Addtransfer To DB: {error}')
    # Log the error
    logger.error(f"Can't add transfer to DB: {error}")
    if cur is not None:
      cur.close()
    return False

def addwitness_vote_to_db(transaction, conn, logger):
  cur = conn.cursor()
  try:
    cur.execute("""
               INSERT INTO pending_witness_votes (account, witness, approve, created, blocknum)
               SELECT %s, %s, %s, %s, %s
               """,
               (
               str(transaction['account']), str(transaction['witness']), transaction['approve'], transaction['timestamp'], transaction['block_num']
               )
               )
#    print('Execute command Add to DB success')
    conn.commit()
    cur.close()
    return True

  except (Exception, psycopg2.DatabaseError) as error:
    # Print the error
    print(f'Error in Add post To DB: {error}')
    # Log the error
    logger.error(f"Can't add post to DB: {error}")
    if cur is not None:
      cur.close()
    return False

#  return True

def addwithdraw_to_db(transaction, conn, logger):
  cur = conn.cursor()

  try:
    cur.execute("""
               INSERT INTO pending_withdrawls (account, vests, timestamp, blocknum)
               SELECT %s, %s, %s, %s
               """,
               (
               str(transaction['account']), str(transaction['vesting_shares']), transaction['timestamp'], transaction['block_num']
               )
               )


    conn.commit()
    cur.close()
    return True
  except (Exception, psycopg2.DatabaseError) as error:
    # Print the error
    print(f'Error in Add withdraw To DB: {error}')
    # Log the error
    logger.error(f"Can't add withdrawl to DB: {error}")
    if cur is not None:
      cur.close()
    return False

def addcustomjson_to_db(transaction, conn, logger):
  cur = conn.cursor()
# required_posting_auths | character varying(55) |
# action                 | text                  |
# json                   | text                  |
# blocknum               | numeric               |
  req_auth  = transaction['required_posting_auths']
  action    = transaction['id']
  json_data = transaction['json']
  blocknum  = transaction['block_num']

  try:
    cur.execute("""
               INSERT INTO pending_custom_json ( required_posting_auths, action, json, blocknum)
               SELECT %s, %s, %s, %s
               WHERE NOT EXISTS (SELECT required_posting_auths FROM pending_custom_json WHERE blocknum=%s AND required_posting_auths = %s);
               """,
               (
               str(req_auth), action, json_data, blocknum,
               blocknum, str(req_auth)
               )
               )
    conn.commit()

    cur.close()
    return True

  except (Exception, psycopg2.DatabaseError) as error:
    # Print the error
    print(f'Error in Add Cust Json To DB: {error}')
    # Log the error
    logger.error(f"Can't add Custom Json to DB: {error}")
    if cur is not None:
      cur.close()
    return False




def addvote_to_db(transaction, conn, logger):

  cur = conn.cursor()
  authorperm = "@" + transaction['author'] + "/" + transaction['permlink']

  try:
    cur.execute("""
               INSERT INTO pending_votes (authorperm, author, created, blocknum, voter, vote_percent)
               SELECT %s, %s, %s, %s, %s, %s;
               """,
               (
               str(authorperm), str(transaction['author']), str(transaction['timestamp']), transaction['block_num'], transaction['voter'], transaction['weight']
               )
               )
#                WHERE NOT EXISTS (SELECT authorperm FROM pending_votes WHERE authorperm = %s and voter = %s) ;
#    print('Execute command Add to DB success')
    conn.commit()
    cur.close()
    return True

  except (Exception, psycopg2.DatabaseError) as error:
    # Print the error
    print(f'Error in Add post To DB: {error}')
    # Log the error
    logger.error(f"Can't add post to DB: {error}")
    if cur is not None:
      cur.close()
    return False

def write_to_file(data, filename):
  try:
    with open(filename, 'w+') as f:
      f.write(str(data))
      f.close()
  except Exception as e:
    print("Error writing to file: {e}")

#  print("Written to file")

def read_blocknum_fromfile(filename):
  try:
    with open(filename, 'r') as f:
      line = f.read()
      print(int(line))
      return int(line)
  except Exception as e:
    print(f"Error Reading File: {e}")
    return []



def addblock_to_db(transaction, conn, logger):
  # Add transaction to database for processing

  success = False

#  print(" success:")
#  print(transaction['type'])
  if transaction['type'] == 'comment':
    success = addpost_to_db(transaction,conn, logger)

  elif transaction['type'] == 'transfer':
    success = addtransfer_to_db(transaction, conn, logger)

  elif transaction['type'] == 'vote':
    success = addvote_to_db(transaction, conn, logger)

  elif transaction['type'] == 'account_witness_vote':
    success = addwitness_vote_to_db(transaction, conn, logger)

  elif transaction['type'] == 'withdraw_vesting':
    success = addwithdraw_to_db(transaction, conn, logger)

  elif transaction['type'] == 'claim_reward_balance':
    success = True

  elif transaction['type'] == 'custom_json':
    print(transaction)
    success = addcustomjson_to_db(transaction, conn, logger)

  if success:
    print(f"Execute command Add Transaction to DB - success : {transaction['type']} | {transaction['block_num']}")
    write_to_file(f"{transaction['block_num']}", "ops_block.txt")
  else:
    print(f"didn\'t work : {transaction['type']}")
    logger.info(transaction)


  return success

def main(conn, logger, debug = False):
  s = Steem(node=nodes)

  theChain = Blockchain(steem_instance = s, mode = "head")
#  print('Start For loop')

  Start_block_num = read_blocknum_fromfile("ops_block.txt")
  if not Start_block_num:
    Start_block_num = theChain.get_current_block_num()


  try:
    for block in theChain.stream(start = Start_block_num):
#      print("Run Again")
#      print(f"{block['block_num']}")
      yay = addblock_to_db(block, conn, logger)
#      print("Got out ok")

  except Exception as e:
    logger.error(f"Error in Stream: {e}")
    return



if __name__ == '__main__':

  print("trying logger")
  logging = set_logger('Notify')
  print("connecting")
  connection = connect_db(logging)
#  print("connected")
#  connection.cursor()
  while True:
    try:
      print('Stream Blockchain and store comments')
      main(connection, logging)

    except (KeyboardInterrupt, SystemExit):
      print("Quitting Program Please wait...")
      break

    except Exception as error:
      print(f"Error in Main Loop: {error}")
      logging.error(f"Error in Main Loop: {error}")
#      break
