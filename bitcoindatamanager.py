import sys 
import getopt

import MySQLdb as mdb

from bitcoinrpc.authproxy import AuthServiceProxy
from pprint import pprint


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