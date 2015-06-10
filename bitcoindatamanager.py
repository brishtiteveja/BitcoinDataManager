import sys 
import getopt

import MySQLdb as mdb

from bitcoinrpc.authproxy import AuthServiceProxy
from pprint import pprint


#Variable initial declaration
#bitcoin rpc connection variable
rpc_connection = None

#block variables 
block_height = -1
block_hashes = []

#transaction id
tx_id = -1

#MySQL variable
height_in_db = 0
connection = None 
cursor = None

#Block class definition
class Block:
    height = None
    merkleroot = None
    hash = None
    version = None
    tx_hashes = None
    num_tx = None
    difficulty = None
    confirmations = None
    nextblockhash = None
    time = None
    bits = None
    size = None
    nonce = None
    
    def __init__(self):
        pass
    def copyBlock(self, blk):
        self.height = blk.height
        self.merkleroot = blk.merkleroot
        self.hash = blk.hash
        self.version = blk.version
        self.tx_hashes = blk.tx_hashes
        self.num_tx = blk.num_tx
        self.difficulty = blk.difficulty
        self.confirmations = blk.confirmations
        self.nextblockhash = blk.nextblockhash
        self.time = blk.time
        self.bits = blk.bits
        self.size = blk.size
        self.nonce = blk.nonce
        
class ScriptSig:
    script_asm = None 
    script_hex = None 
    
    def __init__(self, script_asm, script_hex):
        self.script_asm = script_asm
        self.script_hex = script_hex
        
class ScriptPubKey:
    addrs = []
    script_asm = None 
    script_hex = None 
    script_reqSigs = None
    script_type = None
    def __init__(self, addrs, script_asm, script_hex, script_reqSigs, script_type):
        self. addrs = [a for a in addrs]
        self.script_asm = script_asm
        self.script_hex = script_hex
        self.script_reqSigs = script_reqSigs
        self.script_type = script_type
    
# Input Transaction class definition 
class TxIn:
    id = None 
    n = None # n-th input address in the input section of the transaction
    addrs = [] 
    coinbase = None
    scriptSig = None
    sequence = None
    tx_hash_prev = None 
    vout_prev = None
    vals = [] 
    
    def __init__(self):
        pass
    def copyTxIn(self, ti):
        self.id = ti.id
        self.n = ti.n 
        self.addr = [ti.addr[i] for i in range(len(ti.addrs))]
        self.coinbase = ti.coinbase
        self.scriptSig = ti.scriptSig
        self.sequence = ti.sequence 
        self.tx_hash_prev = ti.tx_hash_prev 
        self.vout_prev = ti.vout_prev 
        self.val = [ti.vals[i] for i in range(len(ti.vals))] 

# Output Transaction class definition 
class TxOut:
    id = None 
    n = None # n-th input address in the input section of the transaction
    scriptPubKey = None
    vals = [] 
    
    def __init__(self):
        pass
    def copyTxOut(self, to):
        self.id = to.id
        self.n = to.n 
        self.scriptPubKey = to.scriptPubKey
        self.vals = [v for v in to.vals] 

# Transaction class definition
class Tx:
    id = None
    hash = None
    block_id = None
    block_time = None
    locktime = None 
    version = None
    txIn = [] 
    txOut = []  
    num_inputs = None
    num_outputs = None 
    total_in_val = None 
    total_out_val = None 
    
    def __init__(self):
        pass
    def copyTx(self, t):
        self.id = t.id
        self.hash = t.hash
        self.block_id = t.block_id
        self.block_time = t.block_time 
        self.locktime = t.locktime 
        self.version = t.version
        self.num_inputs = t.num_inputs 
        self.txIn = [t.txIn[i] for i in range(t.num_inputs)]
        self.num_outputs = t.num_outputs 
        self.txOut = [t.txOut[i] for i in range(t.num_outputs)]
        self.total_in_val = t.total_in_val 
        self.total_out_val = t.total_out_val     

def connect_to_bitcoin_RPC():
    # rpc_user and rpc_password are set in the bitcoin.conf file
    rpc_user = "bitcoinrpc"
    rpc_password = "9RGmSw5dTkMq7Hm1r2pbBVauWoqfM8RXDoCBmoYGmno"
    global rpc_connection
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%(rpc_user, rpc_password))
    return rpc_connection

def get_current_block_height():
    # batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
    commands = [["getblockcount"]]
    counts = rpc_connection.batch_(commands)
    global block_height
    block_height = counts[0]
    return block_height

def get_block_hash(block_height):
    commands = [ [ "getblockhash", block_height] ]
    block_hash = rpc_connection.batch_(commands)[0]
    return block_hash
    
def get_all_block_hashes():
    block_height = get_current_block_height()
    commands = [ [ "getblockhash", height] for height in range(block_height) ]
    global block_hashes
    block_hashes = rpc_connection.batch_(commands)
    return block_hashes

def get_all_block_hashes_from_present_to_past():
    block_height = get_current_block_height()
    commands = [ [ "getblockhash", height] for height in range(block_height) ]
    global block_hashes
    block_hashes = rpc_connection.batch_(commands)
    block_hashes = reversed(block_hashes)
    return block_hashes

def get_block_time(block_height):
    block_hash = get_block_hash(block_height)
    blk = rpc_connection.getblock(block_hash)
    block_time = int(blk["time"])
    return block_time

def connect_to_my_SQL():
    global connection, cursor, height_in_db
    connection = mdb.connect('127.0.0.1', 'root', 'AAAnandaaa05950233;', 'brishtit_bitcoin');
    cursor = connection.cursor()
    if (cursor.execute("""SELECT MAX(height) from block_info;""")):
        data = cursor.fetchall()
        for row in data:
            height_in_db = row[0]
            break
    else:
        print "Maximum block height can not be retrieved."
        sys.exit(1)

def get_block_info(block_hash, height = 0):
    blk = rpc_connection.getblock(block_hash)
    
    block = Block();
    
    block.height = int(height)
    block.merkleroot = blk["merkleroot"]
    block.hash = block_hash 
    block.version = blk["version"]
    block.tx_hashes = [txh for txh in blk["tx"]]
    block.num_tx = len(blk["tx"])
    block.height = blk["height"]
    block.difficulty = int(blk["difficulty"])
    block.confirmations = int(blk["confirmations"])
    block.nextblockhash = blk["nextblockhash"]
    block.time = int(blk["time"])
    block.bits = int(blk["bits"],16)
    block.size = int(blk["size"])
    block.nonce = int(blk["nonce"])
    
    return block
    
def print_block_info(block):
    print "Printing Block Information:"
    print "Height = ", block.height
    print "Hash = ", block.hash
    print "Merkle Root = ", block.merkleroot
    print "Version = ", block.version
    print "Difficulty = ", block.difficulty
    print "Number of Transactions: ", block.num_tx
    print "Block Transaction Hashes."
    for i,tx_hash in enumerate(block.block_tx_hashes):
        print "Tx ",i, " Hash: ", tx_hash
    print "Confirmations = ", block.confirmations
    print "Next Block Hash = ", block.nextblockhash
    print "Time = ", block.time
    print "Size = ", block.size
    print "Nonce = ", block.nonce
    print("Bits = ", block.bits)
        
def update_block_info():    
    for n, block_hash in enumerate(block_hashes):
        height = block_height - n
        block = get_block_info(block_hash, height)
#         print_block_info(block)
        try: 
            cursor = connection.cursor()
            if height > height_in_db:
#               Inserting Block info into block_info table
                warning = cursor.execute("""INSERT IGNORE INTO `block_info`(`height`, `hash`, `next_block_hash`, `time`,
                    `difficulty`, `bits`, `num_tx`, `size`, `merkle_root`, `nonce`, `version`, `confirmations`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
                    (block.height, block.hash, block.nextblockhash, block.time, 
                     block.difficulty, block.bits, block.num_tx, block.size, 
                     block.merkleroot, block.nonce, block.version, block.confirmations))
                if warning:
                    print "Success inserting block at height ", height
                else:
                    print str(warning) + " -  Row already exists!! "
                    print "Failed inserting block at height ", height
            else:
                print "Block less than height ", height, "already exists. Stopping Insertion. Exiting."
                break
#
            connection.commit()
        except mdb.Error,e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)
                sys.exit(1)
#

def get_transaction_info(tx_hash):
    commands = [ [ "getrawtransaction", tx_hash ] ]
    raw_tx = rpc_connection.batch_(commands)[0]
    commands = commands = [ [ "decoderawtransaction", raw_tx ] ]
    tx = rpc_connection.batch_(commands)[0]
    return tx

def update_block_transaction_info(block_height):
    block_hash = get_block_hash(block_height)
    block = get_block_info(block_hash, block_height)
    num_tx = block.num_tx
    tx_hashes = block.tx_hashes
    
    for i in range(num_tx):
        tx_info = get_transaction_info(tx_hashes[i])
        
        tx = Tx()
        
        global tx_id
        tx_id += 1
        tx.id = tx_id
        tx.hash = tx_info["txid"]
        tx.block_id = block_height
        tx.block_time = get_block_time(block_height)
        tx.locktime = tx_info["locktime"]
        tx.version = tx_info["version"]
        
        #to be deleted, don't delete now
#         if tx.hash != "b9a5890b4821450eae5b0e3e2b7f2acaf296085d74e7267e837c2598a977c49a":
#             continue
        
        vin = tx_info["vin"]
        tx.num_inputs = len(vin)
        vout = tx_info["vout"]
        tx.num_outputs = len(vout)
        tx.total_in_val = 0
        tx.total_out_val = 0
        
#         process vin
        for in_i in range(tx.num_inputs):
            txIn = TxIn()
            
            txIn.id = tx.id
            txIn.n = in_i;
            txIn.sequence = vin[in_i]["sequence"]
 
            if "coinbase" in vin[in_i].keys():
                txIn.coinbase = vin[in_i]["coinbase"]
            else:
                txIn.coinbase = "None"
                
            if "scriptSig" in vin[in_i].keys():
                scriptSig = vin[in_i]["scriptSig"]
                script_asm = scriptSig["asm"]
                script_hex = scriptSig["hex"]
                txIn.scriptSig = ScriptSig(script_asm, script_hex)
            else:
                coinbase_msg = "coinbase@block-height:" + str(block_height) + "@tx:" + str(txIn.id) + "@input:" + str(txIn.n)
                txIn.scriptSig = ScriptSig(coinbase_msg, coinbase_msg)
                
            in_addrs = []
            if "txid" in vin[in_i].keys():           
                txIn.tx_hash_prev = vin[in_i]["txid"]
                prev_tx = get_transaction_info(txIn.tx_hash_prev)
            
                if "vout" in vin[in_i].keys():
                    txIn.vout_prev = vin[in_i]["vout"]
                    prev_tx_vout = prev_tx["vout"][txIn.vout_prev]
         
                    #Getting input addresses
                    prev_tx_vout_scriptPubKey = prev_tx_vout["scriptPubKey"]
                    in_addrs = prev_tx_vout_scriptPubKey["addresses"]
                    vals = prev_tx_vout["value"]
                    for val in vals:
                        txIn.vals.append(val)
            else:
                txIn.tx_hash_prev = "None"
                txIn.vout_prev = -1
            
            if "coinbase" in vin[in_i].keys(): #adding coingen as an address in case of coinbase transaction
                in_addrs.append("coingen")
                txIn.vals.append(0) 
            for i,a in enumerate(in_addrs):
                txIn.addrs.append(a)
            
                try: 
                    cursor = connection.cursor()
                    warning = cursor.execute("""INSERT IGNORE INTO `tx_in`(`tx_id`, `n`, `addr`, `coinbase`, `scriptSig_asm`,
                        `scriptSig_hex`, `sequence`, `tx_hash_prev`, `vout_prev`, `val`) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
                        (txIn.id, txIn.n, str(a), txIn.coinbase, txIn.scriptSig.script_asm, 
                         txIn.scriptSig.script_hex, txIn.sequence, txIn.tx_hash_prev, 
                         txIn.vout_prev, txIn.vals[i]))
                    if warning:
                        print "Success inserting input transaction."
                    else:
                        print str(warning) + " -  Row already exists!! "
                        print "Failed to insert input transaction."
                        break
                    connection.commit()
                except mdb.Error,e:
                    try:
                        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                    except IndexError:
                        print "MySQL Error: %s" % str(e)
                        sys.exit(1)

        for out_i in range(tx.num_outputs):
            txOut = TxOut()
            
            txOut.id = tx.id
            txOut.n = out_i;            
            
            scriptPubKey = vout[out_i]["scriptPubKey"]
            out_asm = scriptPubKey["asm"]
            out_hex = scriptPubKey["hex"]
            out_addrs = scriptPubKey["addresses"]
            out_reqSigs = scriptPubKey["reqSigs"]
            out_type = scriptPubKey["type"]
            txOut.scriptPubKey = ScriptPubKey(out_addrs, out_asm, out_hex, out_reqSigs, out_type)
            
            for a in txOut.scriptPubKey.addrs:
                val = vout[out_i]["value"]
                txOut.vals.append(val)
            
                try: 
                    cursor = connection.cursor()
                    warning = cursor.execute("""INSERT IGNORE INTO `tx_out`(`tx_id`, `n`, `addr`, `scriptPubKey_asm`,
                        `scriptPubKey_hex`, `reqSigs`, `type`, `val`) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""", 
                        (txOut.id, txOut.n, str(a), txOut.scriptPubKey.script_asm, 
                         txOut.scriptPubKey.script_hex, txOut.scriptPubKey.script_reqSigs, 
                         txOut.scriptPubKey.script_type, str(val)))
                    if warning:
                        print "Success inserting output transaction."
                    else:
                        print str(warning) + " -  Row already exists!! "
                        print "Failed to insert output transaction."
                        break
                    connection.commit()
                except mdb.Error,e:
                    try:
                        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                    except IndexError:
                        print "MySQL Error: %s" % str(e)
                        sys.exit(1)
            
        break
# #         for in_i in prev_tx_vout[
# 
# #         process vout
#         out_addrs = []
#         num_outputs = len(vout)
#         n = 0
#         for out_i in range(num_outputs):
#                     
#             #Getting input addresses
#             pprint(prev_tx_vout)
#             prev_tx_vout_scriptPubKey = prev_tx_vout["scriptPubKey"]
#             in_addr = prev_tx_vout_scriptPubKey["addresses"]
#             script_asm = prev_tx_vout_scriptPubKey["asm"]
#             script_hex = prev_tx_vout_scriptPubKey["hex"]
#             in_reqSigs = prev_tx_vout_scriptPubKey["reqSigs"]
#             in_type = prev_tx_vout_scriptPubKey["type"] 
#             
#             for a in in_addr:
#                 in_addrs.append(a)
#             
#             print in_addrs
#             break
#         
#         break
#         try: 
#             cursor = connection.cursor()
#             warning = cursor.execute("""INSERT IGNORE INTO `block_info`(`height`, `hash`, `next_block_hash`, `time`,
#                     `difficulty`, `bits`, `num_tx`, `size`, `merkle_root`, `nonce`, `version`, `confirmations`) 
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
#                     (block.height, block.hash, block.nextblockhash, block.time, 
#                      block.difficulty, block.bits, block.num_tx, block.size, 
#                      block.merkleroot, block.nonce, block.version, block.confirmations))
#             if warning:
#                 print "Success inserting block at height ", block_height
#             else:
#                 print "Block less than height ", block_height, "already exists. Stopping Insertion. Exiting."
#                 break
# #
#             connection.commit()
#         except mdb.Error,e:
#             try:
#                 print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
#             except IndexError:
#                 print "MySQL Error: %s" % str(e)
#                 sys.exit(1)
#           
def main():
    # parse command line options
    try:
        connect_to_bitcoin_RPC()
        #get_all_block_hashes_from_present_to_past()
        connect_to_my_SQL()
        #update_block_info()
        update_block_transaction_info(3)
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)

if __name__ == "__main__":
    main()  
    