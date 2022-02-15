# deluxe_stat_bot_py

https://twitter.com/DeluxeStatBot </br>

The OG design for the DeluxeStatBot, written in python. </br></br>

Included features: </br>
- Bears Deluxe Migration Progress </br>
- Bees Deluxe 7D Mint Activity </br>
- Bees Deluxe Historical Mint Activity </br>
- Honey Hive Deluxe 7D Mint Activity </br>
- Honey Hive Deluxe Historical Mint Activity </br>
- Honey Hive Deluxe Current Hive Status </br></br>

**Discontinued. PROD will be refactored to rust. 

## Configuration

- Set absolute paths for bin, etc, log, work </br>
- ES_KEY => etherscan api key </br>
- CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET => twitter api pre-generated v1.1 access  </br>
- ALCHEMY_API_URL => alchemy api key </br>

## Usage 

./deluxe_stat_bot.py -c [config_path] -i [cmd] -a [contract_addr] </br>

cmd = 0, mint progress, supported=[bears,bees,hives]</br>
cmd = 1, status, supported=[hives]</br>

## Output

Bears Deluxe Migration Progress </br>
-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 0 -a 0x4BB33f6E69fd62cf3abbcC6F1F43b94A5D572C2B </br></br>

<p align="center" width="15%" size="50%">
   <img src="work/bears_deluxe_migration_output2022_02_14.png">  
</p>

Bees Deluxe 7D Mint Activity </br>
-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 0 -a 0x1c2CD50f9Efb463bDd2ec9E36772c14A8D1658B3 -t 0 </br>
OR </br>
-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 0 -a 0x1c2CD50f9Efb463bDd2ec9E36772c14A8D1658B3  </br>
** -t option is not required because the default setting for this command is 7D. </br></br>

<p align="center" width="15%" size="50%">
   <img src="work/bees_deluxe_7d_mint_act_2022_02_14.png">  
</p>

Bees Deluxe Historical Mint Activity </br>
-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 0 -a 0x1c2CD50f9Efb463bDd2ec9E36772c14A8D1658B3 -t 1 </br></br>

<p align="center" width="15%" size="50%">
   <img src="work/bees_deluxe_hist_mint_2022_02_07.png">  
</p>

Honey Hive Deluxe 7D Mint Activity </br>
-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 0 -a 0x5df89cC648a6bd179bB4Db68C7CBf8533e8d796e -t 0 </br>
OR </br>
-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 0 -a 0x5df89cC648a6bd179bB4Db68C7CBf8533e8d796e </br></br>

<p align="center" width="15%" size="50%">
   <img src="work/honey_hive_deluxe_7d_mint_act_2022_02_14.png">  
</p>

Honey Hive Deluxe Historical Mint Activity </br>
-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 0 -a 0x5df89cC648a6bd179bB4Db68C7CBf8533e8d796e -t 1 </br></br>

<p align="center" width="15%" size="50%">
   <img src="work/honey_hive_deluxe_hist_mint_act_2022_02_07.png">  
</p>

Honey Hive Current Status </br>
-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 1 -a 0x5df89cC648a6bd179bB4Db68C7CBf8533e8d796e </br></br>

<p align="center" width="15%" size="50%">
   <img src="work/honey_hive_deluxe_current_status_2022_01_22.png">  
</p>


