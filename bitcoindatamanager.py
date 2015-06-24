import sys 
import getopt

import MySQLdb as mdb

from bitcoinrpc.authproxy import AuthServiceProxy
from pprint import pprint
from numpy import double


#Variable initial declaration
#bitcoin rpc connection variable
rpc_connection = None

#block variables 
block_height = 0
block_hashes = []

#transaction id
tx_id = 0 
#address id
addr_id = 0

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
    addrs = []
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
#     rpc_user and rpc_password are set in the bitcoin.conf file
    rpc_user = "bitcoinrpc"
    rpc_password = "9RGmSw5dTkMq7Hm1r2pbBVauWoqfM8RXDoCBmoYGmno"
    global rpc_connection
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%(rpc_user, rpc_password))
    return rpc_connection

def get_current_block_height():
#     batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
    commands = [["getblockcount"]]
    global rpc_connection
    counts = rpc_connection.batch_(commands)
    global block_height
    block_height = counts[0]
    return block_height

def get_current_total_transaction():
    global connection, tx_id
    cursor = connection.cursor()
    if (cursor.execute("""SELECT MAX(tx_id) from tx;""")):
        data = cursor.fetchall()
        for row in data:
            tx_id = row[0]
            break
    return tx_id

def get_current_total_address():
    global connection, addr_id
    cursor = connection.cursor()
    if (cursor.execute("""SELECT MAX(addr_id) from addresses;""")):
        data = cursor.fetchall()
        for row in data:
            addr_id = row[0]
            if addr_id == None or addr_id == -1:
                addr_id = 0
            break
    return addr_id    

def get_block_hash(block_height):
    commands = [ [ "getblockhash", block_height] ]
    global rpc_connection
    block_hash = rpc_connection.batch_(commands)[0]
    return block_hash
    
def get_all_block_hashes():
    block_height = get_current_block_height()
    commands = [ [ "getblockhash", height] for height in range(block_height) ]
    global block_hashes, rpc_connection
    block_hashes = rpc_connection.batch_(commands)
    return block_hashes

def get_all_block_hashes_from_present_to_past():
    block_height = get_current_block_height()
    commands = [ [ "getblockhash", height] for height in range(block_height + 1) ]
    global block_hashes, rpc_connection
    block_hashes = rpc_connection.batch_(commands)
    return block_hashes

def get_block_time(block_height):
    block_hash = get_block_hash(block_height)
    blk = rpc_connection.getblock(block_hash)
    block_time = int(blk["time"])
    return block_time

def connect_to_my_SQL():
    global connection
    connection = mdb.connect('127.0.0.1', 'root', 'AAAnandaaa05950233;', 'brishtit_bitcoin');
    
def get_current_block_height_in_db():
    height_in_db = -1
    cursor = connection.cursor()
    if (cursor.execute("""SELECT MAX(height) from block_info;""")):
        data = cursor.fetchall()
        for row in data:
            height_in_db = row[0]
            break
    else:
        print "No block yet."
    return height_in_db 

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
    global height_in_db
    height_in_db = get_current_block_height_in_db()   
    
    if height_in_db == None:
        height_in_db = 0
    
    global block_height
    if (height_in_db + 1 == block_height):
        print "All blocks are up to date."
                                           
    for height in xrange(height_in_db + 1, block_height + 1):
        block_hash = block_hashes[height]
        block = get_block_info(block_hash, height)
#         print_block_info(block)
        try: 
            global connection
            cursor = connection.cursor()
#               Inserting Block info into block_info table
            warning = cursor.execute("""INSERT IGNORE INTO `block_info`(`height`, `hash`, `next_block_hash`, `time`,
                    `difficulty`, `bits`, `num_tx`, `size`, `merkle_root`, `nonce`, `version`, `confirmations`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
                    (block.height, block.hash, block.nextblockhash, block.time, 
                     block.difficulty, block.bits, block.num_tx, block.size, 
                     block.merkleroot, block.nonce, block.version, block.confirmations))
            if warning:
                print "Success inserting block at height ", height
#                 updating all other tables: tx, txin, txout, addresses, degree, balance, address_graph
                update_block_transaction_info(height)
                print "All transaction for block at ", height, " is completed."
#              
            else:
                print str(warning) + " -  Row already exists!! "
                print "Failed inserting block at height ", height
            connection.commit()
        except mdb.Error,e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)
                sys.exit(1)


def get_transaction_info(tx_hash):
    commands = [ [ "getrawtransaction", tx_hash ] ]
    raw_tx = rpc_connection.batch_(commands)[0]
    commands = commands = [ [ "decoderawtransaction", raw_tx ] ]
    tx = rpc_connection.batch_(commands)[0]
    return tx

def get_address_id(addr):
    global connection 
    cursor = connection.cursor()
    addr_id = None 
    if (cursor.execute("""SELECT `addr_id` FROM addresses WHERE `address` = %s;""", addr)):
        data = cursor.fetchall()
        for row in data:
            addr_id = row[0]
            break
    return addr_id


def get_address_degree(addr):
    global connection
    cursor = connection.cursor()
    addr_id = None 
    in_degree = 0
    out_degree = 0
    if (cursor.execute("""SELECT `addr_id` FROM addresses WHERE `address` = %s;""", addr)):
        data = cursor.fetchall()
        for row in data:
            addr_id = row[0]
            if (cursor.execute("""SELECT `in_degree`, `out_degree` FROM degree WHERE `addr_id` = %s;""", addr_id)):
                degree_data = cursor.fetchall()
                for row in degree_data:
                    in_degree = row[0]
                    out_degree = row[1]
            break
    return (addr_id, in_degree, out_degree)

def get_address_balance(addr):
    global connection
    cursor = connection.cursor()
    addr_id = None 
    balance = 0
    num_changes = 0
    last_change_tx_id = None
    if (cursor.execute("""SELECT `addr_id` FROM addresses WHERE `address` = %s;""", addr)):
        data = cursor.fetchall()
        for row in data:
            addr_id = row[0]
            if (cursor.execute("""SELECT `balance`, `num_changes`, `last_change_tx_id` FROM balance WHERE `addr_id` = %s;""", addr_id)):
                balance_data = cursor.fetchall()
                for row in balance_data:
                    balance = row[0]
                    num_changes = row[1]
                    last_change_tx_id = row[2]
            break
    return (addr_id, balance, num_changes, last_change_tx_id)

def update_address_balance(addr, val, tx_id, time):
#    trying to update in and out degrees of each address
    (addr_id, old_balance, old_num_changes, last_change_tx_id) = get_address_balance(addr)
    new_balance = old_balance + val
    new_num_changes = old_num_changes + 1
    if tx_id != last_change_tx_id:
        new_num_changes_unique_tx = old_num_changes + 1
    else:
        new_num_changes_unique_tx = old_num_changes
    
    try: 
        global connection
        cursor = connection.cursor()
        warning = cursor.execute("""INSERT INTO `balance`(`addr_id`, `balance`, `num_changes`, `num_changes_unique_tx`, `last_change_tx_id`, `last_change_time`) 
            VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE `balance` = VALUES(`balance`), `num_changes` = VALUES(`num_changes`), `num_changes_unique_tx` = VALUES(`num_changes_unique_tx`),
            `last_change_tx_id` = VALUES(`last_change_tx_id`), `last_change_time` = VALUES(`last_change_time`);""", 
            (str(addr_id), str(new_balance), str(new_num_changes), str(new_num_changes_unique_tx), str(tx_id), str(time)))
        if warning:
            if val < 0:
                print "Successfully increased the address balance."
            elif val > 0:
                print "Successfully decreased the address balance."
            else:
                print "Balance kept the same."
        else:
            print "Failed to change the address balance."
        connection.commit()
    except mdb.Error,e:
        try:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: %s" % str(e)
            sys.exit(1)    


def update_address_degree(addr, in_degree, out_degree):
#    trying to update in and out degrees of each address
    (addr_id, old_in_degree, old_out_degree) = get_address_degree(addr)
    new_in_degree = old_in_degree + in_degree
    new_out_degree = old_out_degree + out_degree
    try: 
        global connection
        cursor = connection.cursor()
        warning = cursor.execute("""INSERT INTO `degree`(`addr_id`, `in_degree`, `out_degree`) 
            VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE `in_degree` = VALUES(`in_degree`), 
            `out_degree` = VALUES(`out_degree`);""", 
            (str(addr_id), str(new_in_degree), str(new_out_degree)))
        if warning:
            if in_degree != 0 and out_degree == 0:
                print "Success updating in degree for the output address."
            elif in_degree == 0 and out_degree != 0:
                print "Success updating out degree for the input address."
        else:
            print "Failed to update degree for the address."
        connection.commit()
    except mdb.Error,e:
        try:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: %s" % str(e)
            sys.exit(1)    

def update_addresses(addr):
#    trying to insert new address into address table
    new_addr_id = int(get_current_total_address()) + 1;
    try: 
        global connection
        cursor = connection.cursor()
        warning = cursor.execute("""INSERT IGNORE INTO `addresses`(`addr_id`, `address`) 
            VALUES (%s, %s);""", 
            (str(new_addr_id), str(addr)))
        if warning:
            print "Success inserting new address."
        else:
            print str(warning) + " -  Address already exists!! "
            print "Failed to insert address."
        connection.commit()
    except mdb.Error,e:
        try:
            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        except IndexError:
            print "MySQL Error: %s" % str(e)
            sys.exit(1)

def update_address_graph(txInList, txOutList, time):
        for j in xrange(0, len(txInList)): #txInList and txOutList size = number of tx in a block
            txIns = txInList[j]
            txOuts = txOutList[j]
            
            tx_time = time # block time
            
            for txIn in txIns: # Though only one address
                in_addrs = txIn.addrs
                in_vals = txIn.vals
                for txOut in txOuts: # Though only one address
                    out_addrs = txOut.addrs
                    out_vals = txOut.vals
                    
                    tx_id = txOut.id # transaction index in the block
                    for m, in_addr in enumerate(in_addrs):
                        in_val = in_vals[m]
                        for n, out_addr in enumerate(out_addrs):
                            out_val = out_vals[n]
                            try: 
                                global connection
                                cursor = connection.cursor()
                                warning = cursor.execute("""INSERT INTO `address_graph`(`tx_id`, `in_addr_id`, `in_val`, `out_addr_id`, `out_val`, `tx_time`) 
                                    VALUES (%s, %s, %s, %s, %s, %s);""", 
                                    (str(tx_id), str(in_addr), str(in_val), str(out_addr), str(out_val), str(tx_time)))
                                if warning:
                                    print "Success inserting edge into address graph."
                                    pass
                                else:
                                    print "Failed to insert edge into address graph."
                                connection.commit()
                            except mdb.Error,e:
                                try:
                                    print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                                except IndexError:
                                    print "MySQL Error: %s" % str(e)
                                sys.exit(1) 
            

def update_block_transaction_info(block_height):
    block_hash = get_block_hash(block_height)
    block = get_block_info(block_hash, block_height)
    num_tx = block.num_tx
    tx_hashes = block.tx_hashes
    
    txIns = []
    txInList = [txIns] * num_tx
    txOuts = []
    txOutList = [txOuts] * num_tx
    
    for i in range(num_tx):
        tx_info = get_transaction_info(tx_hashes[i])
        pprint(tx_info)
        tx = Tx()
        
        global tx_id
        tmp_id = get_current_total_transaction()
        
        if tmp_id != None:
            tx_id = int(tmp_id) + 1
        else:
            tx_id = 0
        
            
        tx.id = str(tx_id)
        tx.hash = tx_info["txid"]
        tx.block_id = block_height
        tx.block_time = get_block_time(block_height)
        tx.locktime = tx_info["locktime"]
        tx.version = tx_info["version"]
        
#         to be deleted, don't delete now
#         if tx.hash != "b9a5890b4821450eae5b0e3e2b7f2acaf296085d74e7267e837c2598a977c49a":
#             continue
        
        vin = tx_info["vin"]
        tx.num_inputs = len(vin)
        vout = tx_info["vout"]
        tx.num_outputs = len(vout)
        tx.total_in_val = 0
        tx.total_out_val = 0
        
#         process vin
        txIns = []
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
                coinbase_msg = "coinbase@block-height:" + str(block_height) + "@" + str(in_i) + "-th tx input."
                txIn.scriptSig = ScriptSig(coinbase_msg, coinbase_msg)
                
            in_addrs = []
            txIn.vals = []
            if "txid" in vin[in_i].keys():           
                txIn.tx_hash_prev = vin[in_i]["txid"]
                prev_tx = get_transaction_info(txIn.tx_hash_prev)
            
                if "vout" in vin[in_i].keys():
                    txIn.vout_prev = vin[in_i]["vout"]
                    prev_tx_vout = prev_tx["vout"][txIn.vout_prev]
         
#                     Getting input addresses
                    prev_tx_vout_scriptPubKey = prev_tx_vout["scriptPubKey"]
                    if "addresses" in prev_tx_vout_scriptPubKey.keys():
                        in_addrs = prev_tx_vout_scriptPubKey["addresses"]
                    else:
                        in_addrs =["Undecoded Input Address"]
                    
                    val = float(prev_tx_vout["value"])
                    tx.total_in_val += val
                    txIn.vals.append(val)
                        
            else:
                txIn.tx_hash_prev = "None"
                txIn.vout_prev = -1
            
            if "coinbase" in vin[in_i].keys(): #adding coingen as an address in case of coinbase transaction
                in_addrs.append("coingen")
                txIn.vals.append(0) 
            
            txIn.addrs = [] 
            for i,a in enumerate(in_addrs):
                if "coinbase" not in vin[in_i].keys():
                    update_addresses(a)
                    a = get_address_id(a)
                else:
                    a = 0
                    
                txIn.addrs.append(a)
                    
#                 trying to insert into tx_in table
                try: 
                    cursor = connection.cursor()
                    warning = cursor.execute("""INSERT INTO `tx_in`(`tx_id`, `n`, `addr`, `coinbase`, `scriptSig_asm`,
                        `scriptSig_hex`, `sequence`, `tx_hash_prev`, `vout_prev`, `val`) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
                        (txIn.id, txIn.n, str(a), txIn.coinbase, txIn.scriptSig.script_asm, 
                         txIn.scriptSig.script_hex, txIn.sequence, txIn.tx_hash_prev, 
                         txIn.vout_prev, txIn.vals[i]))
                    if warning:
                        print "Success inserting input transaction."
                        
#                         update input address and its degree
                        if "coinbase" not in vin[in_i].keys():
                            update_address_degree(a, 0, tx.num_outputs)
                            update_address_balance(a, -val, tx.id, tx.block_time)
                
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
            txIns.append(txIn)            
        txInList.append(txIns)
            
        txOuts = []    
#         process vout
        for out_i in range(tx.num_outputs):
            txOut = TxOut()
            
            txOut.id = tx.id
            txOut.n = out_i;            
            
            scriptPubKey = vout[out_i]["scriptPubKey"]
            out_asm = scriptPubKey["asm"]
            out_hex = scriptPubKey["hex"]
            if "addresses" in scriptPubKey.keys():
                out_addrs = scriptPubKey["addresses"]
            else:
                out_addrs = ["Undecoded Output Address"]
            
            if "reqSigs" in scriptPubKey.keys():
                out_reqSigs = scriptPubKey["reqSigs"]
            else:
                out_reqSigs = "No reqSigs"
            
            if "type" in scriptPubKey.keys():
                out_type = scriptPubKey["type"]
            else:
                out_type = "No type"
            txOut.scriptPubKey = ScriptPubKey(out_addrs, out_asm, out_hex, out_reqSigs, out_type)
           
            txOut.addrs = []
            txOut.vals = []
            for a in txOut.scriptPubKey.addrs:
                #update address table
                update_addresses(a)
                #get address_id from the address table
                a = int(get_address_id(a))
                
                txOut.addrs.append(a)
                val = float(vout[out_i]["value"])
                txOut.vals.append(val)
                tx.total_out_val += val
                
#                trying to insert into tx_out table
                try: 
                    cursor = connection.cursor()
                    warning = cursor.execute("""INSERT INTO `tx_out`(`tx_id`, `n`, `addr`, `scriptPubKey_asm`,
                        `scriptPubKey_hex`, `reqSigs`, `type`, `val`) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""", 
                        (txOut.id, txOut.n, str(a), txOut.scriptPubKey.script_asm, 
                         txOut.scriptPubKey.script_hex, txOut.scriptPubKey.script_reqSigs, 
                         txOut.scriptPubKey.script_type, str(val)))
                    if warning:
                        print "Success inserting output transaction."
                        
#                         update output address degree and balance
                        update_address_degree(a, tx.num_inputs, 0)
                        update_address_balance(a, val, tx.id, tx.block_time)
                
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
            txOuts.append(txOut)
        txOutList.append(txOuts)
            
        update_address_graph(txInList, txOutList, tx.block_time)
                    
#        trying to insert into tx table
        try: 
            cursor = connection.cursor()
            warning = cursor.execute("""INSERT IGNORE INTO `tx`(`tx_id`, `hash`, `block_id`, `block_time`,
                `locktime`, `version`, `num_inputs`, `num_outputs`, `total_in_val`, `total_out_val`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
                (tx.id, tx.hash, tx.block_id, tx.block_time, tx.locktime, tx.version, 
                 tx.num_inputs, tx.num_outputs, tx.total_in_val, tx.total_out_val))
            if warning:
                print "Success inserting transaction."
            else:
                print str(warning) + " -  Row already exists!! "
                print "Failed to insert transaction."
                break
            connection.commit()
        except mdb.Error,e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)
                sys.exit(1)

def get_all_txids_for_block(block_id):
    global connection 
    cursor = connection.cursor()
    info_tx_ids = []
    if (cursor.execute("""SELECT `tx_id`,`num_inputs`,`num_outputs` FROM tx WHERE `block_id` = %s;""", block_id)):
        data = cursor.fetchall()
        for row in data:
            tpl = (row[0],row[1],row[2])
            info_tx_ids.append(tpl)
    return info_tx_ids

def update_balance_table_for_addr(addr, val, increase):    
    global connection 
    cursor = connection.cursor()
    
    addr_id = get_address_id()    
    if (cursor.execute("""SELECT `balance` FROM balance WHERE `addr_id` = %s;""", str(addr))):
        data = cursor.fetchall()
        for row in data:
            print row[0]
#             old_balance = double(row[0])
#             print old_balance
#             if increase:
#                 new_balance = old_balance + val
#             else:
#                 new_balance = old_balance - val
#             print new_balance
#             print ""
#             warning = cursor.execute("""UPDATE balance SET `balance` = %s WHERE `addr_id` = %s;""", tx_id, new_balance)
#             if warning:
#                 print "Successfully updated the address balance."
#             else:
#                 print "Failed to update the address balance."

def update_degree_table_for_addr(addr, num_outputs, out_degree):
    global connection 
    cursor = connection.cursor()
    
    if out_degree:    
        if (cursor.execute("""SELECT out_degree FROM degree WHERE `addr_id` = %s;""", addr)):
            data = cursor.fetchall()
            for row in data:
                old_degree = row[0]
                new_degree = old_degree - num_outputs
            
                warning = cursor.execute("""UPDATE degree SET `degree` = %s WHERE `addr_id` = %s;""", new_degree, addr)
                if warning:
                    print "Successfully decreased the out degree for the input address."
                else:
                    print "Failed to update the out degree for the input address."

def update_tables_using_txin_table(info_tx_id):
    (tx_id, num_inputs, num_outputs) = info_tx_id
    
    global connection 
    cursor = connection.cursor()
    tx_ids = []
    if (cursor.execute("""SELECT tx_id, addr, val FROM tx_in WHERE `tx_id` = %s;""", tx_id)):
        data = cursor.fetchall()
        for row in data:
            (tx_id, in_addr, in_val) = (row[0], row[1], row[2])
            if "coingen" in in_addr:
                print "Nothing to do for coingen address."
            else:
                print "Update"
            update_balance_table_for_addr(in_addr, in_val, True)
#             update_degree_table_for_addr(in_addr, num_inputs, True)

def delete_block_data_and_update_tables(block_id):
    global height_in_db
    #Get the last block id in the database
    height_in_db = get_current_block_height_in_db()
    #Get all the tx_ids for the last block
    info_tx_ids = get_all_txids_for_block(height_in_db)
    #print info_tx_ids
    # Get input addresses from tx_in
    for info_tx_id in info_tx_ids:
        update_tables_using_txin_table(info_tx_id)
     
    
def delete_all_data():
    global connection
    cursor = connection.cursor()
    
    table_delete_count = 0
    if (cursor.execute("""delete from block_info;""")):
        table_delete_count += 1
        
    if (cursor.execute("""delete from tx;""")):
        table_delete_count += 1
    
    if (cursor.execute("""delete from tx_in;""")):
        table_delete_count += 1
    
    if (cursor.execute("""delete from tx_out;""")):
        table_delete_count += 1
        
    if (cursor.execute("""delete from balance;""")):
        table_delete_count += 1
    
    if (cursor.execute("""delete from degree;""")):
        table_delete_count += 1
    
    if (cursor.execute("""delete from addresses;""")):
        table_delete_count += 1
    if (cursor.execute("""delete from address_graph;""")):
        table_delete_count += 1
    
    if (cursor.execute("""delete from user_graph_heuristic1;""")):
        table_delete_count += 1
    
    if (cursor.execute("""delete from user_graph_heuristic2;""")):
        table_delete_count += 1
    
    if (cursor.execute("""delete from user_id_heuristic1;""")):
        table_delete_count += 1
    if (cursor.execute("""delete from user_id_heuristic2;""")):
        table_delete_count += 1
        
    if table_delete_count == 12:
        print "All data deleted."
    
def main():
#     parse command line options
    try:
        connect_to_my_SQL()
        connect_to_bitcoin_RPC()
        #get_all_block_hashes_from_present_to_past()
        #update_block_info()
        #update_block_transaction_info(71036)
        delete_block_data_and_update_tables(133074)
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)

if __name__ == "__main__":
    main()  
    