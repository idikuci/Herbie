from beem.comment import Comment
from beem.steem import Steem
from beem.blockchain import Blockchain
from beem.amount import Amount

import logging
import os
import psycopg2

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
nodes = ['https://rpc.smoke.io/']

def connect_db(logger):
 # Connect to Database
  cursor = None
  conn = None
  try:
    connect_str = "dbname='smoke' user='XXXXXX' host='localhost' " + \
                  "password='XXXXXX'"
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
  fh = logging.FileHandler(f"{DIR_PATH}/Virtual_Ops.log")
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

def addwithdraw_to_db(transaction, conn, logger):
  cur = conn.cursor()

  try:
    fromaccount = transaction['from_account']
    toaccount = transaction['to_account']
    amount = transaction['deposited']
    blocknum = transaction['block_num']

    cur.execute("""
               INSERT INTO pending_vesting_withdrawl (fromaccount, toaccount,  amount, blocknum)
               SELECT %s, %s, %s, %s
               WHERE NOT EXISTS (SELECT fromaccount FROM pending_vesting_withdrawl WHERE fromaccount = %s AND blocknum = %s);
               """,
               (
               fromaccount, toaccount, amount, blocknum,
               fromaccount, blocknum
               )
               )
    print('Execute command Add to DB success')
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

def addcuration_reward_to_db(transaction, conn, logger):

  try:
#    print("get cursor")
#    cur = conn.cursor()
#  print('Got Cursor')
#  try:

 #   print("adding")
#    cur.execute("""
#               INSERT INTO pending_transfers (userto, userfrom, amount, message, timestamp)
#               SELECT %s, %s, %s, %s, %s
#               """,
#               (
#               str(transaction['to']), str(transaction['from']), str(transaction['amount']), str(transaction['memo']), transaction['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
#               )
#               )
#    print('Execute command Add Transfer to DB - success')
#    conn.commit()
#    cur.close()
    return False

  except (Exception, psycopg2.DatabaseError) as error:
    # Print the error
    print(f'Error in Addtransfer To DB: {error}')
    # Log the error
    logger.error(f"Can't add transfer to DB: {error}")
    if cur is not None:
      cur.close()
    return False

def addauthorreward_to_db(transaction, conn, logger):
#  cur = conn.cursor()
  try:
#    cur.execute("""
#               INSERT INTO pending_witness_votes (account, witness, approve, created, blocknum)
#               SELECT %s, %s, %s, %s, %s
#               """,
#               (
#               str(transaction['account']), str(transaction['witness']), transaction['approve'], transaction['timestamp'], transaction['block_num']
#               )
#               )
#    print('Execute command Add to DB success')
#    conn.commit()
#    cur.close()
    return False

  except (Exception, psycopg2.DatabaseError) as error:
    # Print the error
    print(f'Error in Add post To DB: {error}')
    # Log the error
    logger.error(f"Can't add post to DB: {error}")
    if cur is not None:
      cur.close()
    return False

#  return True

def adddevfund_to_db(transaction, conn, logger):
#  cur = conn.cursor()

  try:
#    cur.execute("""
#               INSERT INTO pending_withdrawls (account, vests, timestamp, blocknum)
#               SELECT %s, %s, %s, %s
#               """,
#               (
#               str(transaction['account']), str(transaction['vesting_shares']), transaction['timestamp'], transaction['block_num']
#               )
#               )#


#    conn.commit()
#    cur.close()
    return False
  except (Exception, psycopg2.DatabaseError) as error:
    # Print the error
    print(f'Error in Add withdraw To DB: {error}')
    # Log the error
    logger.error(f"Can't add withdrawl to DB: {error}")
    if cur is not None:
      cur.close()
    return False



def addwitness_to_db(transaction, conn, logger):
  cur = conn.cursor()

  witness     = transaction['producer']
  reward, meh = transaction['vesting_shares'].split(' ')
  timing      = transaction['timestamp']
  blocknum    = transaction['block_num']

#  print(reward)

  try:
    cur.execute("""
               INSERT INTO pending_witness_blocks (witness, timestamp, blocknum, payment)
               SELECT %s, %s, %s, %s
               WHERE NOT EXISTS (SELECT blocknum FROM pending_witness_blocks WHERE blocknum = %s) ;
               """,
               (
               str(witness), str(timing), blocknum, reward,
               blocknum
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

def write_to_file(data, filename):
  try:
    with open(filename, 'w+') as f:
      f.write(str(data))
      f.close()
  except Exception as e:
    print("Error writing to file: {e}")

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
  if transaction['type'] == 'producer_reward':
#    print("right type")
    success = addwitness_to_db(transaction,conn, logger)
#  print("  Not Comment")
  elif transaction['type'] == 'devfund':
#    print("   Transfer")
    success = adddevfund_to_db(transaction, conn, logger)
  elif transaction['type'] == 'author_reward':
    success = addauthorreward_to_db(transaction, conn, logger)
  elif transaction['type'] == 'curation_reward':
    success = addcuration_reward_to_db(transaction, conn, logger)
  elif transaction['type'] == 'fill_vesting_withdraw':
    success = addwithdraw_to_db(transaction, conn, logger)
#  elif transaction['type'] == 'claim_reward_balance':
#    success = True

#  header = block.json()

#  success = addwitness_to_db(header, conn, logger)

  if success:
    print(f"Add Block to DB - success : {transaction['type']} | {transaction['block_num']}")
    write_to_file(f"{transaction['block_num']}", "virtual_ops_block.txt")
  else:
    print(f"didn\'t work : {transaction['type']}")
#    logger.info(transaction)


  return success

def main(conn, logger, debug = False):
  # Main Loop
  s = Steem(node=nodes)
  theChain = Blockchain(steem_instance = s, mode = "head")

  Start_block_num = read_blocknum_fromfile("virtual_ops_block.txt")
  if not Start_block_num:
    Start_block_num = theChain.get_current_block_num()


#  print('Start For loop')
  try:
    for block in theChain.stream(only_virtual_ops=True, start = Start_block_num):
      print("Try add to DB")
      addblock_to_db(block, conn, logger)

  except Exception as e:
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
