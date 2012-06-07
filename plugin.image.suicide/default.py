#!/usr/bin/python
#Code Heavily modified from  Demo by TV DASH - by You 2008.
#
# Written by Ksosez with help from anarchintosh
# this is setup for Suicidegirls.com, changes made by sp00nhead
# Released under GPL(v2)

import urllib,urllib2,htmllib
import re,string
import os
import xbmcplugin,xbmcaddon,xbmcgui,xbmc

#addon name
__addonname__ = "plugin.image.suicide"

__settings__ = xbmcaddon.Addon(id=__addonname__)
__cwd__ = __settings__.getAddonInfo('path')

#get path the default.py is in.
__addonpath__= __cwd__

#datapath
__datapath__ = xbmc.translatePath('special://profile/addon_data/'+__addonname__)
sys.path.append( xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')))
#append lib directory
#sys.path.append( os.path.join( __addonpath__, 'resources', 'lib' ) )

#import from lib directory
import weblogin
import gethtml

#import img_merge

pluginhandle = int(sys.argv[1])

# example of how to get path to an image
default_image = os.path.join(__addonpath__,'resources','images','sg.jpg')

# string to simplify urls
baseurl = 'http://suicidegirls.com'
main_url = baseurl
# ip
fip = 'http://66.40.17.55/'



def get_html(url):
     return gethtml.get(url,__datapath__)

def get_avatar(lc):
        #using lowercase username, build the url to the user's avatar
        url = fip+'avatar/'+lc[0]+'/'+lc[1]+'/'+lc[2]+'/'+lc

        #trial and error to find the correct image format
        urlist = [url+'.jpeg',url+'.jpg',url+'.png',url+'.gif']
        for surl in urlist:
                try:
                    resp = urllib2.urlopen(surl)
                except urllib2.URLError, e:
                    pass
                else:
                    return surl
                
def Notify(title,message,times,icon):
        xbmc.executebuiltin("XBMC.Notification("+title+","+message+","+times+","+icon+")")

def LOGIN(username,password):
        uc = username[0].upper() + username[1:]
        lc = username.lower()
        
        logged_in = weblogin.doLogin(__datapath__,username,password)
        print logged_in
        if logged_in == True:

                #avatar = get_avatar(lc)

                Notify('Welcome back '+uc,'','4000','')

                

        elif logged_in == False:

                Notify('Login Failure',uc+' could not login','4000',default_image)

def STARTUP_ROUTINES():
        #deal with bug that happens if the datapath doesn't exist
        if not os.path.exists(__datapath__):
          os.makedirs(__datapath__)

        #check if user has enabled use-login setting
        usrsettings = xbmcaddon.Addon(id=__addonname__)
                
        #get username and password and do login with them
        username = usrsettings.getSetting('username')
        password = usrsettings.getSetting('password')
         
        LOGIN(username,password)

def CATEGORIES():
        STARTUP_ROUTINES()        
        
	addDir('PhotoSets','http://suicidegirls.com/albums/girls/page1/',1,default_image)

        # didn't need to pass search a url. so i was lazy and passed it the main_url as a dummy
	addDir('Search',main_url,5,default_image)
	
	print pluginhandle
	xbmcplugin.endOfDirectory(pluginhandle)

def SEARCH(url):
     # define the keyboard
     kb = xbmc.Keyboard('', 'Search Fantasti.cc Videos', False)

     # call the keyboard
     kb.doModal()

     # if user presses enter
     if (kb.isConfirmed()):

          # get text from keyboard
          search = kb.getText()

          # if the search text is not nothing
          if search is not '':

                  # encode the search phrase to put in url (ie replace ' ' with '+' etc)
                  # normally you would use: search = urllib.quoteplus(search)
                  # but fantasti's search urls are a bit weird
                  search = re.sub('  ','+',search) # this one is just in case the user accidently enters two spaces
                  search = re.sub(' ','+',search)

                  # create the search url
                  search_url = main_url + 'search/' + search + '/videos/'
                  print 'SEARCH:',search_url
                  
                  # get the source code of first page
                  first_page = get_html(search_url)

                  # do a search to see if no results found
                  no_results_found = re.search('did not match any content.',first_page)

                  # if there are results on page...
                  if no_results_found is None:

                          # scrape to get the number of all the results pages (this is listed on the first page)
                          match = re.compile('/videos/page_(.+?)">').findall(first_page)
                          print 'Number of pages:',match

                          # if there were'nt any multiple pages of search results
                          if not match:
                                  # ...directly call the results scraper for the first page to add the directories.
                                  SEARCH_RESULTS(url=False,html=first_page)

                          # if there were any multiple pages of search results
                          if match:

                                  # convert the list of strings produced by re.compile to a list of integers, so we can use them for calculations
                                  match = [int(result) for result in match]
                          
                                  # get the highest results page number, to get the total number of results pages.
                                  # this gets the highest integer in the list of integers
                                  total_pages = max(match)

                                  # generate a list of numbers 1 to total_pages (eg if total_pages is 3 generate: 1,2,3)
                                  num = 1
                                  numlist = list('1')
                                  while num < total_pages:
                                      num = num+1
                                      numlist.append(str(num))
        
                                  # for every number in the list
                                  for thenumber in numlist:

                                          # transform thenumber from an integer to a string, to use in name and url strings
                                          thenumber = str(thenumber)
                                  
                                          # make the page name
                                          name = 'Page ' + thenumber

                                          # make the page url
                                          url = search_url + 'page_' + thenumber

                                          # add the results page as a directory
                                          addDir(name,url,6,default_image)



def SEARCH_RESULTS(url,html=False):
        # this function scrapes the search results pages
        # accepts page source code (html) for any searches where there is only one page of results
       
	if html is False:
		html = get_html(url)
	match=re.compile('<a href="(.+?)" onclick="document.cookie = \'ii=1;path=/\';"  class="xxx" target="_blank"><img alt="(.+?)"   src="(.+?)"').findall(html)
	for gurl,name,thumbnail in match:
			for each in SUPPORTEDSITES:
				if each in gurl:
					realurl = "http://fantasti.cc%s" % gurl
					mode = 4
					addLink(name,realurl, mode, thumbnail)
				else:
					pass
       

   
# def INDEX(url):
# 		html = get_html(url)
# 		if "collection" in url: # Collections
#                         match=re.compile('<a href=(.+?)" title="(.+?)">\s*<img src="(.+?)" border="0" alt="(.+?)"  width="100" height="100" class="collection_image" />').findall(html)
# 			for gurl,name,thumbnail,junk in match:
# 				id = string.split(gurl, "=")[2][:-5]
# 				realurl = "http://fantasti.cc/video.php?id=%s" % id
# 				mode = 4
# 				print realurl
# 				addLink(name,realurl, mode, thumbnail)
# 			html = get_html(url)
# #			match = re.compile('container_[0-9]*').findall(html)
# 			match = re.compile('\(\'(.+?)\', ([0-9]*),\'(.+?)\', \'(.+?)\'\);return false;" href="#">next').findall(html)
# 			if len(match) >= 1:
# 				fixedNext = None
# 				for next in match:
# 					print next
# 					mode = 1
# 					page = next[0][-1]
# 					id = next[1]
# 					#id = string.split(next, '_')[1]
# 					fixedNext = "http://fantasti.cc/ajax/pager.php?page=%s&pid=%s&div=collection_%s&uid=14657" % (page, id, id)
# 					print fixedNext
# 				addDir('Next Page',fixedNext,mode,default_image)
# 			xbmcplugin.endOfDirectory(pluginhandle)
def INDEX(url):
	link = get_html(url)
	match=re.compile('<a class="pngSpank" href="/girls/(.+?)/photos/(.+?)/" title="(.+?)"><img src="(.+?)" ').findall(link)
	for girl,photoset,null,thumbnail in match:
	    name = girl + " ~ " + photoset
	    url = baseurl + "/girls/" + girl +"/photos/" + photoset +"/"
	    #thumblist = list(thumbnail)
	    #thumblist.insert(-4,"t")
	   # thumbnail = "".join(thumblist)
	   # thumbnail = baseurl + thumbnail
	    thumbnail = baseurl +urllib.quote(thumbnail)
	    print thumbnail
	    addDir(name,url,2,thumbnail)			 
	xbmcplugin.endOfDirectory(pluginhandle)

	
def INDEXCOLLECT(url):
	link = get_html(url)
	
	match=re.compile('<a href="(.+?)" onclick="PicViewerNav.').findall(link)
	for url in match:
		url = urllib.quote(url)
		print url
		thumbnail=url
		thumblist = list(thumbnail)
		thumblist.insert(-4,"t")
		thumbnail = "".join(thumblist)

		addLink(name,url,thumbnail)
	xbmcplugin.endOfDirectory(pluginhandle)

#  def INDEXCOLLECT(url):   # Index Collections Pages
# 	print "URL Loading: %s" % url
#  	html = get_html(url)
# 	match = re.compile('<div style="font-size:24px; line-height:30px; "><a href="(.+?)">(.+?)</a>(.+?)<span id="chunk.+?\>(.+?)</div>',re.DOTALL).findall(html)
# 	for gurl,name,chtml,description in match:
#                 print name
# 		realurl = "http://fantasti.cc%s" % gurl
# 		name = unescape(name)
# 		mode = 1

#                 #scrape number of vids
#                 num_of_vids = (re.compile('line-height:100\%;">(.+?) videos<br>',re.DOTALL).findall(chtml))[0]
#                 #trim whitespace from beginning of string
#                 num_of_vids = re.sub('^[ \t\r\n]+','',num_of_vids)
                
#                 # do some cool stuff to get the images and join them.
#                 icons = re.compile('<img src="(.+?)"').findall(chtml)

#                 addDir(name+' *'+num_of_vids+' vids*',realurl, mode,icons[0])

                        
# 	match = re.compile('<a href="(.+?)">next &gt;&gt;</a></span></div>').findall(html)
# 	for next in match:
# 		print "Next: %s" % next
# 		mode = 2 
# 		next = string.split(next, '"')[-1]
# 		fixedNext = "http://fantasti.cc%s" % next
# 		print "FixedNext: %s" % fixedNext
# 		addDir('Next Page',fixedNext, mode,default_image)
		
# 	xbmcplugin.endOfDirectory(pluginhandle)  
		

def PLAY(url):
	print "Play URL:%s" % url
	if "id=" in url:
		realurl = GET_LINK(url, 1)
	else:
		realurl = GET_LINK(url, 0)
	print "Real url:%s" % realurl
	item = xbmcgui.ListItem(path=realurl)
	return xbmcplugin.setResolvedUrl(pluginhandle, True, item)
		
	

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param




def addLink(name,url,mode,iconimage):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Image", infoLabels={ "Title": name } )
	liz.setProperty('IsPlayable', 'true')
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
	return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Image", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def unescape(s):
	p = htmllib.HTMLParser(None)
	p.save_bgn()
	p.feed(s)
	return p.save_end()              

params=get_params()
url=None
name=None
mode=None
cookie=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None:
    print "Generate Main Menu"
    CATEGORIES()
elif mode == 1:
   print "Indexing Videos"
   INDEX(url)
elif mode == 2:
	print "Indexing Collections"
	INDEXCOLLECT(url)

#elif mode == "top rated":
#    print "Category: Top Rated"
 #   TOPRATED()
elif mode == 4:
    print "Play Video"
    PLAY(url)
#elif mode =="categories":
#    print "Category: Categories"
#    CATEGORIES(url)

elif mode == 5:
    print "Category: Search"
    SEARCH(url)

elif mode == 6:
    print "Category: SEARCH_RESULTS"
    SEARCH_RESULTS(url)

#else:
#    print ""+url
#   INDEX(url)




xbmcplugin.endOfDirectory(int(sys.argv[1]))
