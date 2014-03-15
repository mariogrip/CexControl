## MarketsBot
### Description
MarketsBot is a simple utility script to manage mining reinvestments on Markets.cx, simply put, it takes the full profit from LTC minig and automatically uses that to buy more KHS. It has some nice features that calculate prices and try to optimize orders.
This is Beta software. Use at your own risk.

### Installation
Put all the files in a user writeable directory. 

### User guide
#### To start
Run the script on a commandline, ie, "python ./MarketsBot.py"
The script will detect if there is a configuration file or not, and prompt for user input if not.

#### To configre
To create a new configuration, start with "python ./MarketsBot.py newconfig", this will delete the existing configuration.

### Features
The script will run and check every 5 minutes if there are more then 0.001 LTC available. 

If that is the case, the script will retrieve both Bid and Ask prices and average those in a on order spending as close to maximum as possible. If those orders are not fulfilled within 5 minutes, they will be canceled and new orders put in.

###Thanks to Eloque For making the base of this!
