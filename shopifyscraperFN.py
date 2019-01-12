#This file contains helper functions that make stuff look less cluttered
#Using requests to grab page source, beautifulsoup to grab product details on a shopify site, regex to match keywords, lxml for format, discordwebhook for webhook settings

##IMPORTING MODULES##
import requests
from bs4 import BeautifulSoup as soup
import re
import lxml
from discord_webhook import DiscordWebhook,DiscordEmbed

##SITE CLASS##
class siteProd():
    def __init__(self, url):
        self.url = url + "/sitemap.xml"
        smList = siteMap(self.url)
        self.prodDet = {}
        for link in smList:
            self.prodDet.update(prodDict(smScraper(link)))

##HELPER FUNCTION #1: IDENTIFIES IF SITE IS SHOPIFY##
def isShopify(link):
    pageHead = soup(requests.get(link).content, 'lxml').head
    pageHead = str(pageHead)
    shopPat = r'shopify'
    if re.search(shopPat, str(pageHead), re.IGNORECASE):
        return True
    return False



##HELPER FUNCTION #2: SEPARATING KEYWORDS TO POSITIVE AND NEGATIVE##
def kwSeparator(keywords):
    #Returned dictionary containg lists of positive and negative keywords
    retDict = {}

    keywordList = keywords.split(',')
    posKW = []
    negKW = []

    for kw in keywordList:
        if kw[0] == '+':
            posKW.append(kw[1:])
        elif kw[0] == '-':
            negKW.append(kw[1:])
        else:
            pass

    #Removing duplicates
    posKW = set(posKW)
    negKW = set(negKW)

    for kw in negKW:
        if posKW.__contains__(kw):
            posKW.remove(kw)

    retDict.update({'pos':posKW,'neg':negKW})

    return retDict

##HELPER FUNCTION #3: RETRIEVING PAGE SOURCE USING REQUESTS, SOUPIFYING IT, AND RETURNING SITEMAP LINKS CONTAINING PRODUCTS##
def siteMap(link):
    pageSource = soup(requests.get(link).content, 'lxml')
    #Retrieving all sitemap urls in source
    urlList = [x.loc.text for x in pageSource.find_all('sitemap')]

    #Regex to retrieve sitemap url containing all products on the shopify site
    smPat = r'sitemap_products'
    retList = []

    for url in urlList:
        if re.search(smPat, url):
            retList.append(url)

    return retList

##HELPER FUNCTION #4: RETRIEVING PRODUCT DETAILS AVAILABLE ON THE SITEMAP##
def smScraper(link):
    pageSource = soup(requests.get(link).content, 'lxml')
    #Retrieving all product details
    retList = pageSource.find_all('url')[1:]
    return retList

##HELPER FUNCTION #5: CREATING DICTIONARIES OF {PRODUCT NAME: (PRODUCT LINK, PRODUCT IMAGE)} FORMAT##
def prodDict(prodDet):
    retDict = {}
    ind = 1
    for prod in prodDet:
        if (prod.find_all('image:title')):
            prodName = prod.find_all('image:title')[0].text
            prodImg = prod.find_all('image:loc')[0].text
        else:
            prodName = 'Untitled #' + str(ind)
            prodImg = 'data:image/png;base64,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'
            ind += 1
        prodLink = prod.loc.text

        retDict.update({prodName:(prodLink, prodImg)})

    return retDict

##HELPER FUNCTION #6: FILTERING PRODUCTS USING KEYWORDS##
def prodSearch(prodDet, keywords):
    retDict = {}
    mFlag = 0
    posKW = keywords.get('pos')
    negKW = keywords.get('neg')
    for pName, pDet in prodDet.items():
        mFlag = 0
        for kw in posKW:
            kwPat = r'' + kw
            if re.search(kwPat, pName, re.IGNORECASE):
                mFlag = 1
            else:
                mFlag = 0
                break

        for kw in negKW:
            kwPat = r'' + kw
            if re.search(kwPat, pName, re.IGNORECASE):
                mFlag = 0
                break

        if mFlag == 1:
            retDict.update({pName:pDet})

    return retDict

##FULL SCRAPER FUNCTION##
def searchItem(siteURL, keywords):

    #Separate keywords to positive and negative
    kwDict = kwSeparator(keywords)
    #Grabbing link containing products
    siteClass = siteProd(siteURL)
    retDict = prodSearch(siteClass.prodDet, kwDict)

    return retDict

##GRAB VARIANTS##
def variantGrab(pLink):
    retDict = {}

    varContainer = soup(requests.get(pLink).content, 'lxml')
    varContainer = varContainer.find_all('select')[0]
    varDet = varContainer.find_all('option')
    for var in varDet:
        retDict.update({var.text:var['value']})
    return retDict

##DISCORD WEBHOOK##
def discWebhook(discURL, prodDet, siteURL):
    try:
        webhook = DiscordWebhook(url=discURL)
        #setup webhook
        embed = DiscordEmbed(title='ShopifyScraper', description='I scrape shopify sites', color=242424)
        embed.set_author(name='Kane-Bot', url='https://github.com/ahmad-afiquddin', icon_url='https://pbs.twimg.com/profile_images/905928854740586496/piFPvtXM_400x400.jpg')
        if (prodDet):
            for pName, pDet in prodDet.items():
                pLink = pDet[0]
                pImg = pDet[1]
                embed = DiscordEmbed(title='ShopifyScraper', description='I scrape shopify sites', color=242424)
                embed.set_author(name='Kane-Bot', url='https://github.com/ahmad-afiquddin', icon_url='https://pbs.twimg.com/profile_images/905928854740586496/piFPvtXM_400x400.jpg')
                embed.set_image(url=pImg)
                embed.add_embed_field(name=pName, value=pLink)
                embed.add_embed_field(name='PD QUICK TASK', value='[' + pName +']' + '(' + 'https://api.destroyerbots.io/quicktask?url=' + pLink + ')')
                varDict = variantGrab(pLink)
                for size, var in varDict.items():
                    embed.add_embed_field(name=size, value=siteURL + '/cart/' + var + ':1' + ' [**PD**]' + '(' + 'https://api.destroyerbots.io/quicktask?url=' + siteURL + '/cart/' + var + ':1' + ')')
                embed.set_timestamp()
                webhook.add_embed(embed)
                webhook.execute()
                webhook.remove_embed(0)
        else:
            embed = DiscordEmbed(title='ShopifyScraper', description='I scrape shopify sites', color=242424)
            embed.set_author(name='Kane-Bot', url='https://github.com/ahmad-afiquddin', icon_url='https://pbs.twimg.com/profile_images/905928854740586496/piFPvtXM_400x400.jpg')
            embed.set_image(url='https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png')
            embed.add_embed_field(name='NOT LOADED YET, OR BAD KW', value='PATIENCE FROM ZHOU')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
            webhook.remove_embed(0)
    except:
        print('Something is wrong with the discord webhook link you provided')

##MAIN FUNCTION##
def searchForMe(discURL, siteURL, keywords):
    if isShopify(siteURL):
        prodDet = searchItem(siteURL, keywords)
        discWebhook(discURL, prodDet, siteURL)
    else:
        discWebhook(discURL, {'DUMBASS':(siteURL + ' IS NOT SHOPIFY','https://downtrend.com/wp-content/uploads/2018/03/rfda2.jpg')}, siteURL)

if __name__ == '__main__':
    incFlag = 1
    while incFlag:
        try:
            disc = input('Enter your discord webhook link: ')
            shopLink = input('Enter the shopify site link that you would like to use in the format https://site-name.com: ')
            kw = input('Enter keywords in the format +positivekw,-negativekw, you can use multiple kw: ')
            searchForMe(disc, shopLink, kw)
        except:
            print('Please be serious')

