import sys 
import getopt

import MySQLdb as mdb

from bitcoinrpc.authproxy import AuthServiceProxy



#Variable initial declaration
#bitcoin rpc connection variable
rpc_connection = None

#block variables 
block_height = 0
block_hashes = []

#MySQL variable
height_in_db = 0
connection = None 
cursor = None

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
    def copyBlock(self, Block):
        self.height = Block.height
        self.merkleroot = Block.merkleroot
        self.hash = Block.hash
        self.version = Block.version
        self.tx_hashes = Block.tx_hashes
        self.num_tx = Block.num_tx
        self.difficulty = Block.difficulty
        self.confirmations = Block.confirmations
        self.nextblockhash = Block.nextblockhash
        self.time = Block.time
        self.bits = Block.bits
        self.size = Block.size
        self.nonce = Block.nonce


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
    block.block_tx_hashes = [txh for txh in blk["tx"]]
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
        print_block_info(block)
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
          
def main():
    # parse command line options
    try:
        connect_to_bitcoin_RPC()
        get_all_block_hashes_from_present_to_past()
        connect_to_my_SQL()
        update_block_info()
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)

if __name__ == "__main__":
    main()  