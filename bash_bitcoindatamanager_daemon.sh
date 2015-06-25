#!/bin/bash
BITCOIN_MANAGER_HOME="/Users/jogg/Desktop/Andy/workspace/BitcoinDataManager"
while [ 1 -eq 1 ]; do
    OUTPUT=`ps -ef | grep "bitcoindatamanager\.py"`
    if [[ ! -z "${OUTPUT// }" ]] #Checking whether bitcoin manager  is running or not 
    then
	echo "Bitcoin Data Manager is running." >> $BITCOIN_MANAGER_HOME/run_log.txt
    else
	#run the python script again
	python $BITCOIN_MANAGER_HOME/bitcoindatamanager.py &
    fi
    sleep 5
done
