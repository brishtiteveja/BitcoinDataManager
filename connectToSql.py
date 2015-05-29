import MySQLdb as mdb
import sys 
import subprocess
import bitcoinrpc
import logging

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# rpc_user and rpc_password are set in the bitcoin.conf file
rpc_user = "bitcoinrpc"
rpc_password = "9RGmSw5dTkMq7Hm1r2pbBVauWoqfM8RXDoCBmoYGmno"
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%(rpc_user, rpc_password))
# best_block_hash = rpc_connection.getbestblockhash()
# print(rpc_connection.getblock(best_block_hash))

# batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
commands = [["getblockcount"]]
counts = rpc_connection.batch_(commands)
block_height = counts[0]

#block_height = 20;
commands = [ [ "getblockhash", height] for height in range(block_height) ]
block_hashes = rpc_connection.batch_(commands)
block_hashes = reversed(block_hashes)

con = mdb.connect('127.0.0.1', 'root', 'AAAnandaaa05950233;', 'brishtit_bitcoin');
cur = con.cursor()
if (cur.execute("""SELECT MAX(block_height) from block_info;""")):
    data = cur.fetchall()
    for row in data:
        height_in_db = row[0]
        break
else:
    print "Maximum block height can not be retrieved."
    sys.exit(1)
for n,h in enumerate(block_hashes):
    i = block_height - n
    block = rpc_connection.getblock(h)
    block_height = int(i)
    block_merkleroot = block["merkleroot"]
    block_hash = h 
    block_version = block["version"]
    block_tx_hashes = [txh for txh in block["tx"]]
    block_num_tx = len(block["tx"])
    block_height = block["height"]
    block_difficulty = int(block["difficulty"])
    block_confirmations = int(block["confirmations"])
    block_nextblockhash = block["nextblockhash"]
    block_time = int(block["time"])
    block_bits = int(block["bits"],16)
    block_size = int(block["size"])
    block_nonce = int(block["nonce"])
#
#     print(block_merkleroot)
#     print(block_hash)
#     print(block_version)
#     print(block_tx_hashes)
#     print(block_num_tx)
#     print(block_height)
#     print(block_difficulty)
#     print(block_confirmations)
#     print(block_nextblockhash)
#     print(block_time)
#     print(block_size)
#     print(block_nonce)
#     print(block_bits)
#
    try:
 #       
        cur = con.cursor()
        if block_height > height_in_db:
            warning = cur.execute("""INSERT IGNORE INTO `block_info`(`block_height`, `block_hash`, `next_block_hash`, `time`,
                `difficulty`, `bits`, `num_tx`, `size`, `merkle_root`, `nonce`, `version`, `confirmations`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
                (block_height, block_hash, block_nextblockhash, block_time, 
                 block_difficulty, block_bits, block_num_tx, block_size, 
                 block_merkleroot, block_nonce, block_version, block_confirmations))
            print "Success inserting block at height ", block_height
        else:
            print "Block less than height ", block_height, "already exists. Stopping Insertion. Exiting."
            break
#
        con.commit()
    except mdb.Error,e:
        try:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: %s" % str(e)
        sys.exit(1)
#
            