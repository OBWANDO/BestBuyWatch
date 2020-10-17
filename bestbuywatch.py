import requests
import json
import webbrowser
from time import sleep
import logging
from datetime import datetime

# BestBuy API here: https://bestbuyapis.github.io/api-documentation/
# Sign up and get your API key here: https://developer.bestbuy.com/

# BE SURE TO PUT YOUR API KEY IN BELOW!
# various 3080 and 3090 cards: 6432447, 6429434, 6436192, 6429440, 6432400, 6436195, 6430175, 6432399, 6436191, 6432445, 6436196, 6430215, 6432446
# You can find the SKUs on the best buy search page for each item you want.

logging.basicConfig(filename='output.log', format='%(asctime)s %(message)s')

def getrequest(searchstr, api_key, showvar, skus):
        try:
            response = requests.get('https://api.bestbuy.com/v1/products({srchstr})?apiKey={key}&show={showval}&pageSize=100&format=json'.format (
                srchstr = searchstr, key = api_key, showval = showvar
                )
            )
        except Exception as exc:
            logging.error(exc)
            print ('Exception hit, sleeping 5 seconds!')
            sleep(5)
            return

# uncomment this below if you want to search for specific skus
#        response = requests.get('https://api.bestbuy.com/v1/products(sku in ({skuin}))?apiKey={key}&show={showval}&format=json'.format (
#            skuin = skus, key = api_key, showval = showvar
#            )
#        )
        return response

def notifyCart():
    print ("send an email or text)")

def showItem(item, openlink = True):
    avmsg = (':AVAIL: ' + item['addToCartUrl'] + " :: " + item['name'])
    logging.info(avmsg)
    print ('\n' + gettimeformat() + avmsg)
    if openlink is True:
        webbrowser.open(item['addToCartUrl'])
        notifyCart()

def checkshow(item, avails):
    for avl in avails:
        if item[avl] is True:
            showItem(item)
            return True
    return False

def monitorCards(searchstr, api_key, showvar, skus, avails):
    holdweb = False
    
    response = getrequest(searchstr, api_key, showvar, skus)
    if response is None: 
        return

    data = response.json()
    
    if data is None: 
        return
    
    if 'products' not in data: 
        return
    
    for item in data['products']:
        holdweb = holdweb | checkshow(item, avails)

    if holdweb is True:
        print ("Target hit, sleeping 5 minutes to allow for purchase")
        sleep(300)

def gettimeformat():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

def hourlymsg(mnchk):
    if (mnchk % 30 == 0):
        logging.info("Monitor Active")
        print (gettimeformat() + ": Monitor Active")

def main():
    loopcount = 10
    mnchk = 0
    print (gettimeformat() + ": Monitor Started")

    #search string to keep it narrow
    searchstr = 'search in(3090,3080)&productTemplate="Graphics_Cards"'

    #your BestBuy API key goes here (REQUIRED!!!)
    #api_key = 'YOURAPIKEY'
    api_key = ''

    if len(api_key) == 0:
        print ("You need to get an API key and put it in the api_key field for this to work.")
        print ("To get one, go to: https://developer.bestbuy.com/")
        return

    #What we want to pull back
    showvar = 'sku,name,onlineAvailability,orderable,addToCartUrl,inStorePickup,inStoreAvailability,onlineAvailabilityUpdateDate,salePrice'

    #what we need to check if true or not
    avails = ['onlineAvailability', 'inStorePickup', 'inStoreAvailability']
    
    # you can only use 6 SKUs per request
    skus = '6432447, 6429434, 6436192'
    
    while (1):
        monitorCards(searchstr, api_key, showvar, skus)
        sleep(3) # This is how long it will wait in between requests. You have a daily limit of 50k, so going under 2 sec isnt advised
        loopcount = loopcount - 1
        if loopcount < 1:
            loopcount = 10
            mnchk = mnchk + 1
            hourlymsg(mnchk)
        
        print('Scanning: ' + gettimeformat() + '  ' + chr(60 + (loopcount % 3)), end='\r', flush=True)

    print (gettimeformat() + ": Monitor Exiting")

if __name__ == "__main__":
    # execute only if run as a script
    main()


