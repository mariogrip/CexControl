
from __future__ import print_function

import mapi
import re
import time
import json
import sys
import urllib2

version = "0.0.1"

LTCThreshold = 0.00010000

def LoadSettings():

    print ("Attempting to load Settings")

    try:

        fp = open("MarketsBotSettings.conf")
        settings = json.load(fp)

        if ( settings ):
            print ("File found, loading")

    except IOError:
        print ("Could not open file, attempting to create new one")
        CreateSettings()
        settings = LoadSettings()

    return settings

def CreateSettings():

    print ("")
    print ("Please enter your credentials")
    print ("")
    username = raw_input("Username: ")
    key      = raw_input("API Key: ")
    secret   = raw_input("API Secret: ")

    settings = { "username":str(username), "key":str(key), "secret":str(secret) }

    try:
        json.dump(settings, open("MarketsBotSettings.conf", 'w'))
        print ("")
        print ("Configuration file created, attempting reload")
        print ("")
    except:
        print (sys.exc_info())
        print ("Failed to write configuration file, giving up")
        exit()

def main():

    print ("======= MarketsBot version %s =======" % version)

    ParseArguments()

    try:
        settings = LoadSettings()
    except:
        print ("Could not load settings, exiting")
        exit()

    username    = str(settings['username'])
    api_key     = str(settings['key'])
    api_secret  = str(settings['secret'])

    try:
        context = mapi.api(username, api_key, api_secret)
        balance = context.balance()

        print ("========================================")

        print ("Account       : %s" % username)
        print ("KHS balance   : %s" % balance['KHS']['available'])

        print ("========================================")

    except:
        print ("== !! ============================ !! ==")
        print ("Error:")

        try:
            ErrorMessage = balance['error']
        except:
            ErrorMessage = ("Unkown")

        print(ErrorMessage)

        print ("")

        print ("Could not connect Markets.cx, exiting")
        print ("== !! ============================ !! ==")
        exit()

    while True:
        try:
            now = time.asctime( time.localtime(time.time()) )

            print ("")
            print ("%s" % now)

            CancelOrder(context)

            ##balance = context.balance()
            KHSBalance = GetBalance(context, 'KHS')
            print ("KHS balance: %s" % KHSBalance)
            print ("")
      

            print ("")
            PrintBalance( context, "LTC")            
                             
            ReinvestCoin(context, "LTC", LTCThreshold, "KHS" )


        except urllib2.HTTPError, err:
            print ("HTTPError :%s" % err)

        except:
            print ("Unexpected error:")
            print ( sys.exc_info()[0] )
            print ("An error occurred, skipping cycle")

        cycle = 150

        while cycle > 0:
            cycle = cycle - 1
            time.sleep(1)


    pass

## Convert a unicode based float to a real float for us in calculations
def ConvertUnicodeFloatToFloat( UnicodeFloat ):

    ## I need to use a regular expression
    ## get all the character from after the dot
    position = re.search( '\.', UnicodeFloat)
    if ( position ):
        first = position.regs
        place = first[0]
        p = place[0]
        p = p + 1

        MostSignificant  = float(UnicodeFloat[:p-1])
        LeastSignificant = float(UnicodeFloat[p:])

        Factor = len(UnicodeFloat[p:])
        Divider = 10 ** Factor

        LeastSignificant = LeastSignificant / Divider

        NewFloat = MostSignificant + LeastSignificant
    else:
        NewFloat = float(UnicodeFloat)


    return NewFloat

def CancelOrder(context):
    ## LTC Order cancel
    order = context.current_orders("KHS/LTC")
    for item in order:
        try:
            context.cancel_order(item['id'])
            print ("KHS/LTC Order %s canceled" % item['id'])
        except:
            print ("Cancel order failed")

## Get the balance of certain type of Coin
def GetBalance(Context, CoinName):

    balance = ("NULL")

    try:

        balance = Context.balance()

        Coin =  balance[CoinName]
        Saldo = ConvertUnicodeFloatToFloat(Coin["available"])

    except:
        print (balance)
        Saldo = 0

    return Saldo

## Return the Contex for connection
def GetContext():

    try:
        settings = LoadSettings()
    except:
        print ("Could not load settings, exiting")
        exit()

    username    = str(settings['username'])
    api_key     = str(settings['key'])
    api_secret  = str(settings['secret'])

    try:
        context = mapi.api(username, api_key, api_secret)

    except:
        print (context)

    return context

def ParseArguments():
    arguments = sys.argv

    if (len(arguments) > 1):
        print ("MarketsBot started with arguments")
        print ("")

        ## Remove the filename itself
        del arguments[0]

        for argument in arguments:

            if argument == "newconfig":
                print ("newconfig:")
                print ("  Delete settings and create new")
                CreateSettings()


## Print the balance of a Coin
def PrintBalance( Context, CoinName):

    Saldo = GetBalance(Context, CoinName)

    print ("%s" % CoinName, end = " ")
    print ("Balance: %.8f" % Saldo)
    

## Reinvest a coin
def ReinvestCoin(Context, CoinName, Threshold, TargetCoin ):

    Saldo = GetBalance(Context, CoinName)
    
    if ( Saldo > Threshold ):

        TradeCoin( Context, CoinName, TargetCoin )

def GetPriceByCoin(Context, CoinName, TargetCoin ):

    Ticker = GetTickerName( CoinName, TargetCoin )

    return GetPrice(Context, Ticker)

## Fall back function to get TickerName

## Trade one coin for another
def TradeCoin( Context, CoinName, TargetCoin ):

    ## Get the Price of the TargetCoin
    Price = GetPriceByCoin( Context, CoinName, TargetCoin )

    print ("----------------------------------------")

    ## Get the balance of the coin
    Saldo = GetBalance( Context, CoinName)
    print (CoinName , end = " " )
    print ("Balance %.8f" % Saldo)

    ## Caculate what to buy
    AmountToBuy = Saldo / Price
    AmountToBuy = round(AmountToBuy-0.0000005,7)

    print ("Amount to buy %.08f" % AmountToBuy)

    ## This is an HACK
    Total = AmountToBuy * Price

    while ( Total > Saldo ):
        AmountToBuy = AmountToBuy - 0.0000005
        AmountToBuy = round(AmountToBuy-0.0000005,7)

        print ("")
        print ("To buy adjusted to : %.8f" % AmountToBuy)
        Total = AmountToBuy * Price

    TickerName = GetTickerName( CoinName, TargetCoin )

    ## Hack, to differentiate between buy and sell
    action = ''
    if TargetCoin == "LTC":
        action = 'sell'
        AmountToBuy = Saldo ## sell the complete balance!
        print ("To sell adjusted to : %.8f NMC" % AmountToBuy)
    else:
        action = 'buy'

    result = Context.place_order(action, AmountToBuy, Price, TickerName )

    print ("")
    print ("Placed order at %s" % TickerName)
    print ("     Buy %.8f" % AmountToBuy, end = " ")
    print ("at %.10f" % Price)
    print ("   Total %.8f" % Total)
    print ("   Funds %.8f" % Saldo)

    try:
        OrderID = result['id']
        print ("Order ID %s" % OrderID)
    except:
        print (result)

    print ("----------------------------------------")

## Simply reformat a float to 8 numbers behind the comma
def FormatFloat( number):

    number = unicode("%.8f" % number)
    return number



## Fall back function to get TickerName
def GetTickerName( CoinName, TargetCoin ):

    Ticker = "KHS/LTC"
    return Ticker

## Get Price by ticker
def GetPrice(Context, Ticker):

    ## Get price
    ticker = Context.ticker(Ticker)

    Ask = ConvertUnicodeFloatToFloat(ticker["ask"])
    Bid = ConvertUnicodeFloatToFloat(ticker["bid"])

    ## Get average
    Price = Ask

    ## Change price to 7 decimals
    Price = round(Price,8)

    ##print Price
    ##Price = int(Price * INTEGERMATH)

    return Price


if __name__ == '__main__':
    main()
