import hmac
import hashlib
import time
import urllib
import urllib2
import json

class api:
 previous_nonce = 0;      
 __username	= '';
 __api_key	= '';
 __api_secret	= '';
 __nonce_v	= '';
 

 ##Init class##
 def __init__(self,username,api_key,api_secret):
  self.__username = username
  self.__api_key = api_key
  self.__api_secret = api_secret
  
 ##get timestamp as nonce
 def __nonce(self):
          
  noncevalue = int(time.time())
  
  ## Make sure the next nonce is different from the previous within a fixed API call 
  while ( self.previous_nonce >= noncevalue):
      noncevalue = noncevalue + 1
       
  self.__nonce_v = str(noncevalue).split('.')[0]
  self.previous_nonce = noncevalue
  ## print noncevalue
 
 ##generate segnature
 def __signature(self):
  string = self.__nonce_v + self.__username + self.__api_key ##create string
  signature = hmac.new(self.__api_secret, string, digestmod=hashlib.sha256).hexdigest().upper() ##create signature
  return signature

 def __post(self, url, param): ##Post Request (Low Level API call)
  params = urllib.urlencode(param)
  req = urllib2.Request(url, params, {'User-agent': 'bot'})
  page = urllib2.urlopen(req).read()
  return page;
 
 def api_call(self, method, param = {}, private = 0, couple = ''): ## api call (Middle level)
  url = 'https://markets.cx/api/'+method+'/' ##generate url
  if couple != '': 
   url = url + couple + '/' ##set couple if needed
  if private == 1: ##add auth-data if needed
   self.__nonce()
   param.update({
    'key' : self.__api_key,
    'signature' : self.__signature(),
    'nonce' : self.__nonce_v})
  answer = self.__post(url, param); ##Post Request
  return json.loads(answer) ## generate dict and return
 
 def ticker(self, couple = 'KHS/LTC'):
  return self.api_call('ticker', {}, 0, couple)

 def order_book(self, couple = 'KHS/LTC'):
  return self.api_call('order_book', {}, 0, couple)

 def trade_history(self, since = 1, couple = 'KHS/LTC'):
  return self.api_call('trade_history',{"since" : str(since)}, 0, couple)

 def balance(self):
  return self.api_call('balance', {}, 1)

 def current_orders(self, couple = 'KHS/LTC'):
  return self.api_call('open_orders',{},1,couple)

 def cancel_order(self, order_id):
  return self.api_call('cancel_order', {"id" : order_id},1)
 
 def place_order(self, ptype = 'buy', amount = 1, price = 1, couple = 'KHS/LTC'):
  return self.api_call('place_order', {"type" : ptype, "amount" : str(amount), "price" : str(price)},1,couple)
