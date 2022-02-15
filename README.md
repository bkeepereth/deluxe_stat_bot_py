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

Bees Deluxe 7D Mint Activity </br>
-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 0 -a 0x1c2CD50f9Efb463bDd2ec9E36772c14A8D1658B3 -t 0 </br></br>

OR </br></br>

-> ./deluxe_stat_bot.py -c /Users/daemon1/Dev/dev14/etc/config.xml -i 0 -a 0x1c2CD50f9Efb463bDd2ec9E36772c14A8D1658B3  </br>
** -t option is not required because the default setting for this command is 7D. </br>


