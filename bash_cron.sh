#!/bin/bash
BITCOIN_MANAGER_HOME="/Users/jogg/Desktop/Andy/workspace/BitcoinDataManager"
OUTPUT=`ps -ef | grep "bash_bitcoindatamanager_daemon\.sh"`
if [[ ! -z "${OUTPUT// }" ]] #Checking whether the daemon is running or not 
then
	echo "Bitcoin Data Manager Daemon is running."
else
	#starting a new daemon
	sh  $BITCOIN_MANAGER_HOME/bash_bitcoindatamanager_daemon.sh & > /dev/null 2>&1 < /dev/null
fi
