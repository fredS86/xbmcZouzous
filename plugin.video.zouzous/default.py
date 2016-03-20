# -*- coding: utf-8 -*-

# xbmc modules
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
# os and lib modules
import os
import sys 
import urllib
import re
import time
import cPickle as pickle
import zipfile
import simplejson as json
import ast
# print_exc
from traceback import print_exc
# parseDOM
import CommonFunctions
common = CommonFunctions
common.plugin = "plugin.video.Zouzous"


__addonID__         = "plugin.video.Zouzous"
__author__          = "LINUXMAN"
__date__            = "20-03-2016"
__version__         = "1.0.1"
__credits__         = ""
__addon__           = xbmcaddon.Addon( __addonID__ )
__settings__        = __addon__
__language__        = __addon__.getLocalizedString
__addonDir__        = __settings__.getAddonInfo( "path" )

   

# Global Variable
ROOTDIR             = __addonDir__
BASE_RESOURCE_PATH  = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH          = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA          = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
CACHEDIR            = os.path.join( ADDON_DATA, "cache")
THUMB_CACHE_PATH    = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )
FANART_PATH         = os.path.join( ROOTDIR, "fanart.jpg" )
# Web variable
USERAGENT           = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:37.0) Gecko/20100101 Firefox/41.0"
# List of directories to check at startup
dirCheckList        = (CACHEDIR,)
# Catalogue
CATALOG_PATH        = os.path.join(CACHEDIR,'ZouzousCatalog.json')
DIRECT_PATH        = os.path.join(CACHEDIR,'ZouzousDirect.json')
jsonReplayCatalog   = "http://webservices.francetelevisions.fr/jeunesse/getCatchup.php"
jsonDirect          ="http://webservices.francetelevisions.fr/jeunesse/getGuideWebTv.php"

if not os.path.exists(CACHEDIR) :
    os.makedirs(CACHEDIR, mode=0777)

class AppURLopener(urllib.FancyURLopener):
    version = USERAGENT
    
urllib._urlopener = AppURLopener()

class Zouzous:
    """
    main plugin class
    """
    debug_mode = False #self.debug_mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  Zouzous - Version: %s"%__version__
        print "==============================="
        print
        self.set_debug_mode()
        if self.debug_mode:
            print "Python version:"
            print sys.version_info
            print "ROOTDIR: %s"%ROOTDIR
            print "ADDON_DATA: %s"%ADDON_DATA
            print "CACHEDIR: %s"%CACHEDIR 
            print "FANART_PATH: %s"%FANART_PATH 
        params     = self.get_params()
        name       = None
        mode       = None
        iconimage  = None   
        url = None
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
        try:
            iconimage=urllib.unquote_plus(params["iconimage"])
        except:
            pass
                               
        if self.debug_mode:
            print "Mode: "+str(mode)
            print "Name: "+str(name)
            print "Iconimage: "+str(iconimage)
            print "URL: "+str(url)
 
        # Check if directories in user data exist
        for i in range(len(dirCheckList)):
            self.checkfolder(dirCheckList[i]) 
    
        if mode==None:
            self.download_catalogs()
            self.addDirect()
            self.addReplay(1)
            self.addLastDay(3)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        
        elif mode==1:
            self.addSeries(2)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )

        elif mode==2:
            self.addEpisodes(name, iconimage)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )

        elif mode==3:
            self.addEpisodes(name, iconimage)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )

        elif mode==5:
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)


    def addEpisodes(self, name, iconimage):
            data        = open(CATALOG_PATH).read()
            jsoncat     = json.loads(data.decode('iso-8859-1'))
            response  = jsoncat['response']
            programmes =response['programmes']
            for serie in programmes :
                serie_name          = serie['serie'].encode('utf-8')
                if serie_name == name : 
                    episodes =serie['liste_episodes']
                    for episode in episodes :
                        episode_name = episode['episode'].encode('utf-8')
                        episode_url = episode['url_contenu'].encode('utf-8')
                        self.addLink(episode_name,episode_url,5,iconimage,FANART_PATH,{})


    def addReplay(self, new_mode):
            self.addDir("Replay",new_mode,os.path.join(MEDIA_PATH, "btn_videos_on.png"),FANART_PATH,{},"Replay")

    def addLastDay(self, new_mode):
            self.addDir("Dernier jour",new_mode,os.path.join(MEDIA_PATH, "btn_videos_off.png"),FANART_PATH,{},"LastDay")

    def addSeries(self, new_mode):
            data        = open(CATALOG_PATH).read()
            jsoncat     = json.loads(data.decode('iso-8859-1'))
            response  = jsoncat['response']
            programmes =response['programmes']
            for serie in programmes :
                serie_name          = serie['serie'].encode('utf-8')
                serie_image          = serie['url_image_serie'].encode('utf-8')
                serie_infos         = {}
                self.addDir(serie_name,new_mode,serie_image,FANART_PATH,serie_infos,serie_name)


    def addDirect(self):
            data        = open(DIRECT_PATH).read()
            jsoncat     = json.loads(data.decode('iso-8859-1'))
            response  = jsoncat['response']
            url_live =response['url_live']
            self.addLink("Direct Zouzous",url_live,5,os.path.join(MEDIA_PATH, "btn_webtv_on.png"),FANART_PATH,{})       
    
    def download_catalogs(self):
        if os.path.exists(CATALOG_PATH):
            os.remove(CATALOG_PATH)
        if self.debug_mode:
            print "REPLAY CATALOG URL: "+jsonReplayCatalog
        urllib.urlretrieve(jsonReplayCatalog,CATALOG_PATH)
        if os.path.exists(DIRECT_PATH):
            os.remove(DIRECT_PATH)
        if self.debug_mode:
            print "DIRECT CATALOG URL: "+jsonDirect
        urllib.urlretrieve(jsonDirect,DIRECT_PATH)
    
    def set_debug_mode(self):
        self.debug_mode=__settings__.getSetting('debug')
        if self.debug_mode== 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "Zouzous:self.debug_mode Mode:"
        print self.debug_mode        
        
    def addLink(self,name,url,mode,iconimage,fanart,infos={}):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        infos['Title'] = name
        liz.setInfo( type="Video", infoLabels=infos )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('Fanart_Image', fanart )
        ok =xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok         

    def addDir(self,name,mode,iconimage,fanart,infos={},cat=''):
        u  =sys.argv[0]+"?mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&cat="+urllib.quote_plus(cat)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        infos['Title'] = name
        liz.setInfo( type="Video", infoLabels=infos )
        if fanart != '' :
            liz.setProperty('Fanart_Image',fanart)
        else :
            liz.setProperty('Fanart_Image',FANART_PATH)
        ok =xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
    def get_params(self):
        param      =[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params         =sys.argv[2]
            cleanedparams  =params.replace('?','')
            if (params[len(params)-1]=='/'):
                params     =params[0:len(params)-2]
            pairsofparams  =cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        return param

    def checkfolder(self,folder):
        try:
            if not os.path.exists(folder):
                print "checkfolder Impossible to find the directory - trying to create the directory: "+folder
                os.makedirs(folder)
        except Exception, e:
            print "Exception while creating folder "+folder
            print str(e)

    def clean_thumbnail(self,video_url):
        try:
            filename = xbmc.getCacheThumbName(video_url)
            filepath = xbmc.translatePath(os.path.join(THUMB_CACHE_PATH,filename[0],filename))
            if os.path.isfile(filepath):
                os.remove(filepath)
                if self.debug_mode:
                    print "Deleted %s thumb matching to %s video"%(filepath,video_url)
            elif self.debug_mode:
                print "No thumb found %s thumb matching to %s video"%(filepath,video_url)
            return True
        except:
            print "Error: clean_thumbnail()"
            print_exc()
            return False  

#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        Zouzous()
    except:
        print_exc()