# -*- coding: utf-8 -*-

# xbmc modules
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
# os and lib modules
import os
import sys 
import simplejson as json
# print_exc
from traceback import print_exc
import CommonFunctions
common = CommonFunctions
from urlparse import parse_qsl

__addonID__         = "plugin.video.Zouzous"
__author__          = "FredS86"
__date__            = "02-11-2016"
__version__         = "1.1-beta2"
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
FANART_PATH         = os.path.join( ROOTDIR, "fanart.jpg" )
# List of directories to check at startup
dirCheckList        = (CACHEDIR,)
# Catalogue
heroesUrl          = 'http://www.zouzous.fr'
heroUrl            = "http://www.zouzous.fr/heros/{0}/playlist" # + "?limit=10&offset=4"
videoUrl           = "http://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion={0}"

# Get the plugin url in plugin:// notation.
__url__ = sys.argv[0]
# Get the plugin handle as an integer number.
__handle__ = int(sys.argv[1])

FANART_ID='1024x576'
THUMB_ID='262x262'

class Zouzous:
    """
    main plugin class
    """
    debug_mode = False
    
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
 
        # Check if directories in user data exist
        for i in range(len(dirCheckList)):
            self.checkfolder(dirCheckList[i]) 
    
        self.router(sys.argv[2])


    def router(self, paramstring):
        """
        Router function that calls other functions
        depending on the provided paramstring
        :param paramstring:
        :return:
        """
        # Parse a URL-encoded paramstring to the dictionary of
        # {<parameter>: <value>} elements
        params = dict(parse_qsl(paramstring[1:]))

        if self.debug_mode:
            print "Params : "
            for item in params.items() : 
                print item
            
        # Check the parameters passed to the plugin
        if params:
            if params['action'] == 'listing':
                # Display the list of videos in a provided category.
                self.list_videos(params['heroe'])
            elif params['action'] == 'play':
                # Play a video from a provided URL.
                self.play_video(params['video'])
        else:
            # If the plugin is called from Kodi UI without any parameters,
            # display the list of video categories
            self.list_heroes()

        xbmcplugin.setPluginCategory( handle=__handle__, category=__language__ ( 30000 ) )

            
    def list_heroes(self):
        """
        Create the list of video heroes in the Kodi interface.
        :return: None
        """
        # Get video heroes
        heroes = self.get_heroes()
        # Create a list for our items.
        listing = []
        
        # Add direct first
        thumb = os.path.join(MEDIA_PATH, "img_zouzous_tv.png")
        list_item = xbmcgui.ListItem(label='Zouzous TV', thumbnailImage=thumb)
        # Set a fanart image for the list item.
        # Here we use the same image as the thumbnail for simplicity's sake.
        list_item.setProperty('fanart_image', FANART_PATH)
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': 'Zouzous TV', 'genre': 'Dessin animé'})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        url = 'http://medias2.francetv.fr/playlists/zouzous/zouzous_mobiles.m3u8'
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
        
        # Iterate through heroes
        for heroe in heroes:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=heroe['name'], thumbnailImage=heroe['thumb'])
            # Set a fanart image for the list item.
            # Here we use the same image as the thumbnail for simplicity's sake.
            list_item.setProperty('fanart_image', heroe['fanart'])
            # Set additional info for the list item.
            # Here we use a heroe name for both properties for for simplicity's sake.
            # setInfo allows to set various information for an item.
            # For available properties see the following link:
            # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
            list_item.setInfo('video', {'title': heroe['name'], 'genre': 'Dessin animé'})
            # Create a URL for the plugin recursive callback.
            # Example: plugin://plugin.video.example/?action=listing&heroe=heroe-id
            url = '{0}?action=listing&heroe={1}'.format(__url__, heroe['id'])
            # is_folder = True means that this item opens a sub-list of lower level items.
            is_folder = True
            # Add our item to the listing as a 3-element tuple.
            listing.append((url, list_item, is_folder))
        # Add our listing to Kodi.
        # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
        # instead of adding one by ove via addDirectoryItem.
        xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
        # Add sort methods
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL )
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(__handle__)
    
    def list_videos(self, heroe):
        """
        Create the list of playable videos in the Kodi interface.
        :param category: str
        :return: None
        """
        # Get the list of videos in the category.
        videos = self.get_videos(heroe)
        # Create a list for our items.
        listing = []
        # Iterate through videos.
        for video in videos:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=video['name'], thumbnailImage=video['thumb'])
            # Set a fanart image for the list item.
            # Here we use the same image as the thumbnail for simplicity's sake.
            list_item.setProperty('fanart_image', video['fanart'])
            # Set additional info for the list item.
            list_item.setInfo('video', {'title': video['name']
                                        , 'genre': 'Dessin animé'
                                        , 'date' : video['sortDate'] 
                                        , 'tagline' : video['summary']
                                        , 'plotoutline' : video['summary'] 
                                        , 'duration' : video['time'] 
                                        #, 'aired' : video['date'][0:10]
                                        })
            # Set 'IsPlayable' property to 'true'.
            # This is mandatory for playable items!
            list_item.setProperty('IsPlayable', 'true')
            # Create a URL for the plugin recursive callback.
            # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
            url = '{0}?action=play&video={1}'.format(__url__, video['url'])
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False
            # Add our item to the listing as a 3-element tuple.
            listing.append((url, list_item, is_folder))
        # Add our listing to Kodi.
        # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
        # instead of adding one by ove via addDirectoryItem.
        xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
        # Add sort methods
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DATE )
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL )
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(__handle__)
    
  
    def play_video(self, path):
        """
        Play a video by the provided path.
        :param path: str
        :return: None
        """
        # Create a playable item with a path to play.
        play_item = xbmcgui.ListItem(path=path)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)


    def get_heroes(self):
        """
        Get the list of heroes.
        :return: list
        """
        if self.debug_mode:
            print "get_heroes"
        heroes = []
        zouzous = common.fetchPage({'link': heroesUrl})
        if zouzous['status'] == 200 :
            heroesHtml = common.parseDOM(zouzous['content'], name = 'ul', attrs = { 'class': 'Heroes__List__Content' }, ret = False) 
            
            heroesId = common.parseDOM(heroesHtml, name = 'li', attrs = { 'class': 'Hero' }, ret = 'data-hero-id') 
            
            for heroId in heroesId :
                heroHtml = common.parseDOM(heroesHtml, name = 'li', attrs = { 'class': 'Hero', 'data-hero-id' : heroId }, ret = False)
                heroes.append({
                        'id' : heroId,
                        'name': common.replaceHTMLCodes(common.parseDOM(heroHtml, name = 'h2')[0]),
                        'thumb': common.parseDOM(heroHtml, name = 'img', attrs = { 'class': 'Hero__Icon' }, ret = 'src')[0].replace('88x88', THUMB_ID),
                        'fanart': common.parseDOM(heroHtml, name = 'img', attrs = { 'class': 'Hero__Icon' }, ret = 'src')[0].replace('88x88', FANART_ID)
                    })
#        <li class="Hero" style="background-color: #dbbfd0" data-hero-id="peppa-pig-1">
#                    <a title="Peppa Pig" href="/heros/peppa-pig-1">
#                        <img class="Hero__Icon" src="http://www.zouzous.fr/image/88x88/pictos-heros-peppa-800x800.png" alt="Peppa Pig" title="Peppa Pig">
#                        <div class="Hero__Name " style="color: #dbbfd0"><h2 class="Hero__Name__Content">Peppa Pig</h2></div>
#                    </a>
#        </li>
        return heroes
    
    def get_videos(self, hero):
        """
        Get the list of video for a heroes.
        :param heroe: str
        :return: list
        """
        if self.debug_mode:
            print "get_videos " + hero
        videos = []
        data = self.get_data(heroUrl, hero)
        for video in data['items'] :
            videos.append({
                    'name' : video['title'],
                    'thumb' : video['thumbnail']['uri'][THUMB_ID],
                    'fanart' : video['hero']['avatar']['uri'][FANART_ID],
                    'time' : self.calc_time(video['time']),
                    'summary' : video['videoSummary'],
                    'date' : video['diffusionDate'],
                    'dateEnd' : video['publication']['dateEnd'],
                    'sortDate' : video['publication']['dateEnd'][8:10] + '.' + video['publication']['dateEnd'][5:7] + '.' + video['publication']['dateEnd'][0:4],  
                    'url' : self.get_video_url(video['identity'])
                })
    
        return videos
    
    def calc_time(self, time):
        if (time == None) :
            return 0
        else :
            return time * 60 
        
    def get_video_url(self, identity):
        data = self.get_data(videoUrl, identity.replace("@", "&catalogue="))
        return data['videos'][0]['url']
    
    def get_data(self, baseUrl, url_id):
        url = baseUrl.format(url_id)
        if self.debug_mode:
            print "DATA URL: "+url
        data = common.fetchPage({'link': url})

        return json.loads(data['content'])
        
    def checkfolder(self,folder):
        try:
            if not os.path.exists(folder):
                print "checkfolder Impossible to find the directory - trying to create the directory: "+folder
                os.makedirs(folder)
        except Exception, e:
            print "Exception while creating folder "+folder
            print str(e)

    def set_debug_mode(self):
        self.debug_mode=__settings__.getSetting('debug')
        if self.debug_mode== 'true':
            self.debug_mode = True
            # append pydev remote debugger
            # Make pydev debugger works for auto reload.
            # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
            try:
                sys.path.append("/home/bureau/.p2/pool/plugins/org.python.pydev_5.2.0.201608171824/pysrc")
                import pydevd # with the addon script.module.pydevd, only use `import pydevd`
                # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
                pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
            except ImportError:
                sys.stderr.write("Error: " +
                    "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
                sys.exit(1)

        else:
            self.debug_mode = False
        print "Zouzous:self.debug_mode Mode:"
        print self.debug_mode        
        
    
#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        Zouzous()
    except:
        print_exc()


