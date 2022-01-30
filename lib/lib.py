#!/usr/bin/env python
import requests
import pandas as pd
import base64
import os
import traceback
import json
import sys
import logging
import datetime
import getopt

import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
import plotly
import plotly.express as px

from eth_account import Account
from web3 import Web3, HTTPProvider
from requests_oauthlib import OAuth1Session, OAuth1
from multiprocessing import Process, Queue

pio.templates["custom_dark"] = pio.templates["plotly_dark"]
pio.templates["custom_dark"]['layout']['paper_bgcolor'] = '#30404D'
pio.templates["custom_dark"]['layout']['plot_bgcolor'] = '#30404D'

pio.templates['custom_dark']['layout']['yaxis']['gridcolor'] = '#4f687d'
pio.templates['custom_dark']['layout']['xaxis']['gridcolor'] = '#4f687d'


def parse_owners(log, df):
    log.info(str(datetime.datetime.now())+"|parse_owners|starting")

    mint_df=df[df["FROM_ADDR"]=="0x0000000000000000000000000000000000000000"]
    gain_df=df[df["FROM_ADDR"]!="0x0000000000000000000000000000000000000000"]
    lose_df=df[df["FROM_ADDR"]!="0x0000000000000000000000000000000000000000"]

    mint_df=mint_df[["TO_ADDR","TOKEN_ID"]]
    mint_df.rename(columns={"TO_ADDR":"WALLET"}, inplace=True)
    mint_df["ACTION"]="MINT"
    mint_df["VALUE"]=1

    gain_df=gain_df[["TO_ADDR","TOKEN_ID"]]
    gain_df.rename(columns={"TO_ADDR":"WALLET"}, inplace=True)
    gain_df["ACTION"]="GAIN"
    gain_df["VALUE"]=1

    lose_df=lose_df[["FROM_ADDR","TOKEN_ID"]]
    lose_df.rename(columns={"FROM_ADDR":"WALLET"}, inplace=True)
    lose_df["ACTION"]="LOSE"
    lose_df["VALUE"]=-1

    total_df=pd.concat([mint_df,gain_df,lose_df])
    total_df=total_df.astype({"TOKEN_ID":int})

    owners=total_df.groupby(["WALLET"]).sum()
    owners=owners[owners["VALUE"]>0]

    log.info(str(datetime.datetime.now())+"|parse_owners|completed")
    return owners


def get_erc721_transfers(log,es_key,contract_addr):
    log.info(str(datetime.datetime.now())+"|get_erc721_transfers|starting")

    url=('''https://api.etherscan.io/api?module=account&action=tokennfttx&contractaddress='''+contract_addr
+'''&startblock=0'''
+'''&endblock=99999999'''
+'''&sort=asc'''
+'''&apikey='''+es_key)

    response=requests.request("GET", url)

    if (response==None):
        raise Exception("response object is invalid")

    data=json.loads(response.text).get("result")
    cols=["BLOCK_NUM",
          "TIME_STAMP",
          "HASH",
          "NONCE",
          "BLOCK_HASH",
          "CONTRACT_ADDR",
          "TO_ADDR",
          "FROM_ADDR",
          "TOKEN_ID",
          "TOKEN_NAME",
          "TOKEN_SYMBOL",
          "TXN_INDEX",
          "GAS",
          "GAS_PRICE",
          "GAS_USED",
          "CUM_GAS_USED",
          "INPUT",
          "CONFIRMS"]

    log.info(str(datetime.datetime.now())+"|get_erc721_transfers|parsing response...")

    df=pd.DataFrame(columns=cols)
    for i in range(len(data)):
        block_num=str(data[i].get("blockNumber"))
        time_stamp=str(data[i].get("timeStamp"))
        hash=str(data[i].get("hash"))
        nonce=str(data[i].get("nonce"))
        block_hash=str(data[i].get("blockHash"))
        contract_address=str(data[i].get("contractAddress"))
        to_address=str(data[i].get("to"))
        from_address=str(data[i].get("from"))
        token_id=int(data[i].get("tokenID"))
        token_name=str(data[i].get("tokenName"))
        token_symbol=str(data[i].get("tokenSymbol"))
        token_decimal=str(data[i].get("tokenDecimal"))
        txn_index=str(data[i].get("transactionIndex"))
        gas=str(data[i].get("gas"))
        gas_price=str(data[i].get("gasPrice"))
        gas_used=str(data[i].get("gasUsed"))
        cum_gas_used=str(data[i].get("cumulativeGasUsed"))
        input=str(data[i].get("input"))
        confirms=str(data[i].get("confirmations"))

        new_row={"BLOCK_NUM":block_num,
                 "TIME_STAMP":time_stamp,
                 "HASH":hash,
                 "NONCE":nonce,
                 "BLOCK_HASH":block_hash,
                 "CONTRACT_ADDR":contract_address,
                 "TO_ADDR":to_address,
                 "FROM_ADDR":from_address,
                 "TOKEN_ID":token_id,
                 "TOKEN_NAME":token_name,
                 "TOKEN_SYMBOL":token_symbol,
                 "TXN_INDEX":txn_index,
                 "GAS":gas,
                 "GAS_PRICE":gas_price,
                 "GAS_USED":gas_used,
                 "CUM_GAS_USED":cum_gas_used,
                 "INPUT":input,
                 "CONFIRMS":confirms}
        df=df.append(new_row,ignore_index=True)

    log.info(str(datetime.datetime.now())+"|get_erc721_transfers|completed")
    return df


def mint_act(log, df, file_name, flg):
    log.info(str(datetime.datetime.now())+"|mint_act|starting")

    mint_df=df[df["FROM_ADDR"]=="0x0000000000000000000000000000000000000000"].copy()

    mint_df["MINT"]=0
    mint_df.loc[mint_df.FROM_ADDR=="0x0000000000000000000000000000000000000000","MINT"]=1

    mint_df["DT"]=[datetime.datetime.fromtimestamp(int(x)) for x in mint_df["TIME_STAMP"]]
    mint_df["DATE"]=mint_df["DT"].dt.date
    mint_df.drop(columns=["TIME_STAMP","FROM_ADDR","TOKEN_ID","DT"],inplace=True)

    mint_df=mint_df.groupby(["DATE"]).sum()

    if flg:
        fig=px.bar(mint_df,
               x=mint_df.index.values,
               y=mint_df.MINT.values,
               text=mint_df.MINT.values,
               labels={"x":"Date","y":"Mint Activity"})
        fig.layout.template='plotly_dark'
        fig.update_layout(showlegend=False)
        pio.write_image(fig,file_name,width=1000,height=750)
        #fig.show()

    log.info(str(datetime.datetime.now())+"|mint_act|completed")
    return mint_df


def get_bee_supply(log, alchemy_url, contract_addr, abi_file):
    log.info(str(datetime.datetime.now())+"|get_bee_supply|starting")

    w3=Web3(HTTPProvider(alchemy_url))
    contract=w3.eth.contract(address=contract_addr,abi=abi_file)

    current_supply=contract.functions.totalSupply().call()
    max_supply=contract.functions.MAX_SUPPLY().call()
    cent=round((current_supply/max_supply)*100,2)

    log.info(str(datetime.datetime.now())+"|get_bee_supply|completed")
    return (current_supply, max_supply, cent)


def bee_mint_act(log, df, config, contract_addr):
    log.info(str(datetime.datetime.now())+"|bee_mint_act|starting")

    file_path=config.get("WORK_DIR")+"/"+(str(datetime.datetime.now())[:-7]).replace(" ","_")+"_BD_mint_act.png"
    mint_df=mint_act(log,df,file_path,1)
    today_mint_cnt=mint_df.iloc[-1,0]

    abi_file=open(config.get("ETC_DIR")+"/BeesDeluxeAbi.json","r")
    abi=json.load(abi_file)

    (current_supply,max_supply,cent)=get_bee_supply(log,config.get("ALCHEMY_API_URL"),contract_addr,abi)

    if (current_supply=="" or current_supply==None):
        raise exception("current_supply is invalid, value="+str(current_supply))
    if (max_supply=="" or max_supply==None):
        raise exception("max_supply is invalid, value="+str(max_supply))
    if (cent=="" or cent==None):
        raise exception("cent is invalid, value="+str(cent))

    output=('''- '''+str(df.iloc[0]["TOKEN_NAME"])+''' Mint Activity -
Progress : '''+str(cent)+'''%
Minted Today : '''+str(today_mint_cnt)+'''
Supply : '''+str(current_supply)+'''/'''+str(max_supply))

    oauth=OAuth1Session(config.get("CONSUMER_KEY"),
                     client_secret=config.get("CONSUMER_SECRET"),
                     resource_owner_key=config.get("ACCESS_TOKEN"),
                     resource_owner_secret=config.get("ACCESS_SECRET"))

    url="https://upload.twitter.com/1.1/media/upload.json"

    file_size=os.path.getsize(file_path)
    file_data=open(file_path,"rb")
    files={"media":file_data}

    response=oauth.post(url,files=files)
    if (response.ok):
        dta=json.loads(response.text)
        ids=[dta["media_id"]]

        post_url="https://api.twitter.com/1.1/statuses/update.json"
        payload={"status":output,"media_ids":ids}

        post_tweet=oauth.post(post_url,params=payload)
        if (post_tweet.status_code!=200):
            log.info(str(datetime.datetime.now())+"|bee_mint_act|post_tweet response code: "+str(post_tweet.status_code))
            raise exception(post_tweet.text)
    else:
        log.info(str(datetime.datetime.now())+"|bee_mint_act|response code: "+str(response.status_code))
        raise exception(post_tweet.text)

    log.info(str(datetime.datetime.now())+"|bee_mint_act|completed")


def hive_mint_act(log, df, config):
    log.info(str(datetime.datetime.now())+"|hive_mint_act|starting")

    # assume no dups
    file_path=config.get("WORK_DIR")+"/"+(str(datetime.datetime.now())[:-7]).replace(" ","_")+"_HHD_mint_act.png"

    MAX_SUPPLY=6900
    mint_df=mint_act(log,df,file_path,1)
    today_mint_cnt=mint_df.iloc[-1,0]
    total_mint=mint_df.sum()[0]
    cent=round((total_mint/MAX_SUPPLY)*100,2)

    output=('''- '''+str(df.iloc[0]["TOKEN_NAME"])+''' Mint Actvity -
Progress : '''+str(cent)+'''%
Minted Today : '''+str(today_mint_cnt)+'''
Supply : '''+str(total_mint)+'''/'''+str(MAX_SUPPLY)+'''

Remaining : '''+str(MAX_SUPPLY-total_mint))

    oauth=OAuth1Session(config.get("CONSUMER_KEY"),
                     client_secret=config.get("CONSUMER_SECRET"),
                     resource_owner_key=config.get("ACCESS_TOKEN"),
                     resource_owner_secret=config.get("ACCESS_SECRET"))

    url="https://upload.twitter.com/1.1/media/upload.json"

    file_size=os.path.getsize(file_path)
    file_data=open(file_path,"rb")
    files={"media":file_data}

    response=oauth.post(url,files=files)
    if (response.ok):
        dta=json.loads(response.text)
        ids=[dta["media_id"]]

        post_url="https://api.twitter.com/1.1/statuses/update.json"
        payload={"status":output,"media_ids":ids}

        post_tweet=oauth.post(post_url,params=payload)

        if (post_tweet.status_code!=200):
            log.info(str(datetime.datetime.now())+"|hive_mint_act|post_tweet response code: "+str(post_tweet.status_code))
            raise exception(post_tweet.text)
    else:
        log.info(str(datetime.datetime.now())+"|hive_mint_act|response code: "+str(response.status_code))
        raise exception(post_tweet.text)

    log.info(str(datetime.datetime.now())+"|hive_mint_act|completed")


def bear_mint_act(log, df, config):
    log.info(str(datetime.datetime.now())+"|bear_mint_act|starting")

    MAX_SUPPLY=6900
    mint_df=mint_act(log,df,"",0)
    today_mint_cnt=mint_df.iloc[-1,0]
    total_mint=mint_df.sum()[0]
    cent=round((total_mint/MAX_SUPPLY)*100,2)

    output=('''- '''+str(df.iloc[0]["TOKEN_NAME"])+''' Migration -
Progress : '''+str(cent)+'''%
Migrated Today : '''+str(today_mint_cnt)+'''
Supply : '''+str(total_mint)+'''/'''+str(MAX_SUPPLY)+'''

Remaining : '''+str(MAX_SUPPLY-total_mint))

    oauth=OAuth1Session(config.get("CONSUMER_KEY"),
                     client_secret=config.get("CONSUMER_SECRET"),
                     resource_owner_key=config.get("ACCESS_TOKEN"),
                     resource_owner_secret=config.get("ACCESS_SECRET"))

    url="https://api.twitter.com/2/tweets"
    payload={"text":output}

    response=oauth.post(url,json=payload)
    if (response.status_code!=201):
        log.info(str(datetime.datetime.now()+"|bear_mint_act|response code: "+str(response.status_code)))
        raise exception("Tweet could not be posted...")
    else:
        log.info(str(datetime.datetime.now())+"|bear_mint_act|response code: "+str(response.status_code))

    log.info(str(datetime.datetime.now())+"|bear_mint_act|completed")


def get_minted_hives(log, start, end, contract_address, abi, queue, alchemy_url):
    log.info(str(datetime.datetime.now())+"|get_minted_hives|starting")

    w3=Web3(HTTPProvider(alchemy_url))
    contract=w3.eth.contract(address=contract_address,abi=abi)

    result=list()
    for i in range(start,end):
        if (contract.functions.exists(i).call()):
            result.append(i)

    queue.put(result)
    log.info(str(datetime.datetime.now())+"|get_minted_hives|completed")


def hive_mint_count(log, hive_arr, contract_address, abi, queue, alchemy_url):
    log.info(str(datetime.datetime.now())+"|hive_mint_count|starting")

    w3=Web3(HTTPProvider(alchemy_url))
    contract=w3.eth.contract(address=contract_address,abi=abi)

    result=list()
    for i in range(0,len(hive_arr)):
        usage_cnt=contract.functions.getUsageOfMintingBee(i).call()
        result.append(usage_cnt)

    queue.put(result)
    log.info(str(datetime.datetime.now())+"|hive_mint_count|completed")


def hive_status(log, config, contract_address):
    log.info(str(datetime.datetime.now())+"|hive_status|starting")

    abi_file=open(config.get("ETC_DIR")+"/HoneyHiveDeluxeAbi.json","r")
    abi=json.load(abi_file)

    queue=Queue()
    processes=list()
    for i in range(1,8):
        if (i==7):
            start=(i*1000)-1000
            end=(i*1000)-100
        else:
            end=i*1000
            start=end-1000

        processes.append(Process(target=get_minted_hives,args=(log,start,end,contract_address,abi,queue,config.get("ALCHEMY_API_URL"),)))

    log.info(str(datetime.datetime.now())+"|main|starting processes...")
    for p in processes:
        p.start()

    log.info(str(datetime.datetime.now())+"|main|joining processes...")
    for p in processes:
        p.join()

    results=[queue.get() for _ in processes]

    mint_cnt=0
    for result in results:
        mint_cnt+=len(result)

    res_queue=Queue()
    processes=list()
    for i in range(0,7):
        processes.append(Process(target=hive_mint_count,args=(log,results[i],contract_address,abi,res_queue,config.get("ALCHEMY_API_URL"),)))

    log.info(str(datetime.datetime.now())+"|main|starting processes...")
    for p in processes:
        p.start()

    log.info(str(datetime.datetime.now())+"|main|joining processes...")
    for p in processes:
        p.join()

    counts=[res_queue.get() for _ in processes]

    '''3:inact/0:virg/1:sing/2:doub'''
    inact_cnt=0
    virg_cnt=0
    sing_cnt=0
    doub_cnt=0

    for result in counts:
        for x in result:
            if x==0:
                virg_cnt+=1
            elif x==1:
                sing_cnt+=1
            elif x==2:
                doub_cnt+=1
            elif x==3:
                inact_cnt+=1

    unmint_cnt=6900-inact_cnt-virg_cnt-sing_cnt-doub_cnt

    x=["Unminted","0","1","2","3"]
    y=[unmint_cnt,virg_cnt,sing_cnt,doub_cnt,inact_cnt]

    fig=go.Figure(data=[go.Bar(
                    x=x,
                    y=y,
                    text=y,
                    textposition='auto',
                )])
    fig.update_layout(title="Honey Hives Deluxe Current Status",xaxis_title="Mint Count",yaxis_title="Number of Hives")
    fig.layout.template='plotly_dark'
    #fig.show() 

    file_path=config.get("WORK_DIR")+"/"+(str(datetime.datetime.now())[:-7]).replace(" ","_")+"_hive_mint_bar.png"
    pio.write_image(fig,file_path,width=1000,height=750)

    file_size=os.path.getsize(file_path)
    file_data=open(file_path, "rb")
    files={"media":file_data}

    oauth=OAuth1Session(config.get("CONSUMER_KEY"),
            client_secret=config.get("CONSUMER_SECRET"),
            resource_owner_key=config.get("ACCESS_TOKEN"),
            resource_owner_secret=config.get("ACCESS_SECRET"))

    url="https://upload.twitter.com/1.1/media/upload.json"
    response=oauth.post(url,files=files)

    if (response.ok):
        dta=json.loads(response.text)
        ids=[dta["media_id"]]

        post_url="https://api.twitter.com/1.1/statuses/update.json"
        payload={"media_ids":ids}
        post_tweet=oauth.post(post_url,params=payload)

        if (post_tweet.status_code!=200):
            log.info(str(datetime.datetime.now())+"|hive_status|post_tweet response code: "+str(post_tweet.status_code))
            raise exception(post_tweet.text)
    else:
        log.info(str(datetime.datetime.now())+"|hive_status|response code: "+str(response.status_code))
        raise exception(post_tweet.text)

    log.info(str(datetime.datetime.now())+"|hive_status|completed")

def get_config(file_name):
    if (file_name=="" or file_name==None):
        raise Exception(str(datetime.datetime.now())+"|get_config|file_name is invalid|file_name="+str(file_name))

    result=dict()
    root=ET.parse(file_name).getroot()
    for prop in root.findall('property'):
        result[prop.find('name').text]=prop.find('value').text

    return result



