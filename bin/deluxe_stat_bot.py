#!/usr/bin/env python
import requests
import pandas as pd
import getopt
import base64
import os
import traceback
import json
import sys
import logging
import datetime

sys.path.insert(1,'../lib/')
import lib

def main(argv):
    try:
        (opts,args)=getopt.getopt(argv,"hc:a:i:t:",["help"])  
        file_name=""
        contract_address=""
        input=-1
        total_flg=0

        for (opt,arg) in opts:   
            if (opt in ("-h","--help")):
                Usage()
                sys.exit()
            elif (opt in ("-c")):
                file_name=str(arg)
            elif (opt in ("-a")):
                contract_address=str(arg)
            elif (opt in ("-i")):
                input=int(arg)
            elif (opt in ("-t")):
                total_flg=int(arg)
            else:
                Usage()
                sys.exit()

        config=lib.get_config(file_name)

        logging.basicConfig(filename=config.get("LOG_DIR")+"/"+str(datetime.datetime.now())+"_deluxe_stat_bot.log",filemode="w")
        log=logging.getLogger()
        log.setLevel(logging.INFO)
        log.info(str(datetime.datetime.now())+"|main|starting")

        if (contract_address=="0x5df89cC648a6bd179bB4Db68C7CBf8533e8d796e"): 
            if (input==0):
                es_key=str(config.get("ES_KEY"))
                df=lib.get_erc721_transfers(log,es_key,contract_address)
                lib.hive_mint_act(log,df,config,total_flg)
            elif (input==1):
                lib.hive_status(log, config, contract_address) 
        elif (input==0 and contract_address=="0x1c2CD50f9Efb463bDd2ec9E36772c14A8D1658B3"):
            es_key=str(config.get("ES_KEY"))
            df=lib.get_erc721_transfers(log,es_key,contract_address)
            lib.bee_mint_act(log,df,config,contract_address,total_flg)
        elif (input==0 and contract_address=="0x4BB33f6E69fd62cf3abbcC6F1F43b94A5D572C2B"):
            es_key=str(config.get("ES_KEY"))
            df=lib.get_erc721_transfers(log,es_key,contract_address)
            lib.bear_mint_act(log,df,config)
        else: 
            log.info(str(datetime.datetime.now())+"|main|contract_address not supported. exiting...")
            sys.exit()
 
    except Exception as e:
        traceback.print_exc()

if __name__=="__main__":
    main(sys.argv[1:])
