# Herbie
Alerts/ Notifications bot for the smoke network.

## Requirements:

- Python 3.6
- Postgresql

### Python modules
- Beem
- psycopg2
- discord
- logging

### PostgreSQL Tables (Code not written to make it)

#### block_production_history
```
  Column   |            Type             | Collation | Nullable | Default
-----------+-----------------------------+-----------+----------+---------
 witness   | character varying(55)       |           |          |
 timestamp | timestamp without time zone |           |          |
 blocknum  | numeric                     |           |          |
 payment   | character varying(55)       |           |          |
```
#### pending_custom_json
```
         Column         |         Type          | Collation | Nullable | Default
------------------------+-----------------------+-----------+----------+---------
 required_posting_auths | character varying(55) |           |          |
 action                 | text                  |           |          |
 json                   | text                  |           |          |
 blocknum               | numeric               |           |          |
```
#### pending_notifications
```
   Column   |          Type           | Collation | Nullable | Default
------------+-------------------------+-----------+----------+---------
 authorperm | character varying(1050) |           |          |
 targets    | text                    |           |          |
 watchword  | character varying(255)  |           |          |
 author     | text                    |           |          |
 type       | text                    |           |          |
 amount     | character varying(55)   |           |          |
 ad_text    | text                    |           |          |
```
#### pending_posts
```
    Column     |            Type             | Collation | Nullable | Default
---------------+-----------------------------+-----------+----------+---------
 authorperm    | character varying(1050)     |           | not null |
 author        | character varying(55)       |           |          |
 title         | character varying(255)      |           |          |
 body          | text                        |           |          |
 created       | timestamp without time zone |           | not null |
 blocknum      | numeric                     |           |          |
 parent_author | text                        |           |          |
 tags          | text                        |           |          |
```
#### pending_transfers
```
  Column   |          Type          | Collation | Nullable | Default
-----------+------------------------+-----------+----------+---------
 userto    | character varying(255) |           |          |
 userfrom  | character varying(255) |           |          |
 amount    | character varying(55)  |           |          |
 message   | text                   |           |          |
 timestamp | character varying(255) |           |          |
```
#### pending_vesting_withdrawl
```
   Column    |         Type          | Collation | Nullable | Default
-------------+-----------------------+-----------+----------+---------
 fromaccount | character varying(55) |           |          |
 toaccount   | character varying(55) |           |          |
 amount      | character varying(25) |           |          |
 blocknum    | numeric               |           |          |
```
#### pending_votes
```
    Column     |            Type             | Collation | Nullable | Default
---------------+-----------------------------+-----------+----------+---------
 authorperm    | character varying(1050)     |           | not null |
 author        | character varying(55)       |           |          |
 title         | character varying(255)      |           |          |
 created       | timestamp without time zone |           | not null |
 blocknum      | numeric                     |           |          |
 parent_author | character varying(55)       |           |          |
 voter         | character varying(55)       |           |          |
 vote_percent  | numeric                     |           |          |
```
#### pending_withdrawls
```
  Column   |            Type             | Collation | Nullable | Default
-----------+-----------------------------+-----------+----------+---------
 account   | character varying(55)       |           |          |
 vests     | character varying(55)       |           |          |
 timestamp | timestamp without time zone |           |          |
 blocknum  | numeric                     |           |          |
```
#### pending_witness_blocks
```
  Column   |            Type             | Collation | Nullable | Default
-----------+-----------------------------+-----------+----------+---------
 witness   | character varying(55)       |           |          |
 timestamp | timestamp without time zone |           |          |
 blocknum  | numeric                     |           |          |
 payment   | character varying(55)       |           |          |
```
#### watchlist
```
   Column   |          Type          | Collation | Nullable |                 Default
------------+------------------------+-----------+----------+------------------------------------------
 entry      | integer                |           | not null | nextval('watchlist_entry_seq'::regclass)
 discord_id | character varying(255) |           |          |
 watchword  | character varying(255) |           |          |
 type       | text                   |           |          |
```
# To make it work
Edit the bash script files to ensure they point to the correct folders.

Open Crontab and put in the below lines at the end

`* * * * * python3.6 projects/herbie-smoke/Check_posts_for_mentions-v9.py`

`* * * * * python3.6 projects/herbie-smoke/Check_for_transfers-v2.py`

`* * * * * python3.6 projects/herbie-smoke/Check_for_voters-v1.py`

`* * * * * python3.6 projects/herbie-smoke/Check_custom_json-v1.py`

# process witness production alerts (virtual Ops)
`* * * * * python3.6 projects/herbie-smoke/Check_for_witness_blocksv2.py`

# Daily production reports
`2 1 * * * python3.6 projects/herbie-smoke/Create_daily_prod_report-v1.py`

# These will only run the code if it's not already running
`*/20 * * * * ./projects/herbie-smoke/Run_Stream_Operations.sh`

`*/20 * * * * ./projects/herbie-smoke/Run_Stream_Virtual.sh`

`*/20 * * * * ./projects/herbie-smoke/Run_interface.sh`
