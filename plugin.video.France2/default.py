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

__addonID__         = "plugin.video.Ludo"
__version__         = "1.0"
__addon__           = xbmcaddon.Addon( __addonID__ )
__settings__        = __addon__
__language__        = __addon__.getLocalizedString
__addonDir__        = __settings__.getAddonInfo( "path" )

# Global Variable
ROOTDIR             = __addonDir__
MEDIA_PATH          = os.path.join( os.path.join( ROOTDIR, "resources" ), "media" )
ADDON_DATA          = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
FANART_PATH         = os.path.join( ROOTDIR, "fanart.png" )
FANART_ID='1024x576'
THUMB_ID='262x262'
# Catalogues URL
heroesUrl          = 'http://www.ludo.fr/'
heroUrl            = "http://www.ludo.fr/heros/{0}/playlist" # + "?limit=10&offset=4"
videoUrl           = "http://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion={0}"


#Le zip avec les json n'est plus dispo, par contre il existe una API assez similaire pour avoir le listing des programmes:
#http://pluzz.webservices.francetelevisions.fr/pluzz/liste/type/replay/nb/10000/chaine/france2 (france3, france4, france5, franceo)

#Ce qui change c'est que l'URL de la playlist du stream n'est plus dans le json, il faut appeler une seconde API avec l'ID:
#http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=%s&catalogue=Pluzz

#Là on retrouve les URL des playlist "classiques", j'ai noté que la HD n'est dispo que dans celle "hls_v5_os" (ayant le standard5).

"Bon j'ai rien inventé, j'ai eu besoin d'adapter une app perso en lisant le code de https://github.com/SylvainCecchetto/plugin.video.catchuptvandmore :)



# Get the plugin url in plugin:// notation.
__url__ = sys.argv[0]
# Get the plugin handle as an integer number.
__handle__ = int(sys.argv[1])
# Get the URL-encoded paramstring
__paramString__ = sys.argv[2]

class Ludo:
    """
    main plugin class
    """
    debug_mode = False
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  Ludo - Version: %s"%__version__
        print "==============================="
        print
        self.__set_debug_mode__()
        if self.debug_mode:
            print "Python version:"
            print sys.version_info
            print "ROOTDIR: %s"%ROOTDIR
            print "MEDIA_PATH: %s"%MEDIA_PATH
            print "ADDON_DATA: %s"%ADDON_DATA
            print "FANART_PATH: %s"%FANART_PATH 
            print "FANART_ID: %s"%FANART_ID 
            print "THUMB_ID: %s"%THUMB_ID 
 
        # Parse a URL-encoded __paramString__ to the dictionary of
        # {<parameter>: <value>} elements
        params = dict(parse_qsl(__paramString__[1:]))

        if self.debug_mode:
            print "Params : "
            for item in params.items() : 
                print item
            
        # Check the parameters passed to the plugin
        if params:
            if params['action'] == 'listing':
                # Display the list of videos for a provided hero.
                self.list_videos(self.get_videos(params['hero']))
            elif params['action'] == 'play':
                # Play a video from a provided URL.
                self.play_video(params['video'])
        else:
            # If the plugin is called from Kodi UI without any parameters,
            # display the list of video categories
            self.list_heroes(self.get_heroes())

        xbmcplugin.setPluginCategory( handle=__handle__, category=__language__ ( 30000 ) )

            
    def list_heroes(self, heroes):
        """
        Create the list of video heroes in the Kodi interface.
        :return: None
        """
        # Create a list for our items.
        listing = []
        
        # Iterate through heroes
        for hero in heroes:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=hero['name'], thumbnailImage=hero['thumb'])
            # Set a fanart image for the list item.
            list_item.setProperty('fanart_image', hero['fanart'])
            # Set additional info for the list item.
            list_item.setInfo('video', {'title': hero['name'], 'genre': 'Dessin animé'})
            # Create a URL for the plugin recursive callback.
            # Example: plugin://plugin.video.Ludo/?action=listing&hero=hero
            url = '{0}?action=listing&hero={1}'.format(__url__, hero['id'])
            # is_folder = True means that this item opens a sub-list of lower level items.
            is_folder = True
            # Add our item to the listing as a 3-element tuple.
            listing.append((url, list_item, is_folder))
        # Add our listing to Kodi.
        xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
        # Add sort methods
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL )
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(__handle__)
    
    def list_videos(self, videos):
        """
        Create the list of playable videos in the Kodi interface.
        :param category: str
        :return: None
        """
        # Create a list for our items.
        listing = []
        # Iterate through videos.
        for video in videos:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=video['name'], thumbnailImage=video['thumb'])
            # Set a fanart image for the list item.
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
            # Example: plugin://plugin.video.Ludo/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
            print video['url']
            url = '{0}?action=play&video={1}'.format(__url__, video['url'])
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False
            # Add our item to the listing as a 3-element tuple.
            listing.append((url, list_item, is_folder))
        # Add our listing to Kodi.
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
        ludo = common.fetchPage({'link': heroesUrl})
        if ludo['status'] == 200 :
            heroesHtml = common.parseDOM(ludo['content'], name = 'ul', attrs = { 'class': 'Heroes__List__Content' }, ret = False) 
            
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
#                        <img class="Hero__Icon" src="http://www.ludo.fr/image/88x88/pictos-heros-peppa-800x800.png" alt="Peppa Pig" title="Peppa Pig">
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
        data = self.__get_data__(heroUrl, hero)
        for video in data['items'] :
            videos.append({
                    'name' : video['title'],
                    'thumb' : video['thumbnail']['uri'][THUMB_ID],
                    'fanart' : video['hero']['avatar']['uri'][FANART_ID],
                    'time' : self.__calc_time__(video['time']),
                    'summary' : video['videoSummary'],
                    'date' : video['diffusionDate'],
                    'dateEnd' : video['publication']['dateEnd'],
                    'sortDate' : video['publication']['dateEnd'][8:10] + '.' + video['publication']['dateEnd'][5:7] + '.' + video['publication']['dateEnd'][0:4],  
                    'url' : self.__get_video_url__(video['identity'])
                })
    
        return videos
    
    
    def __calc_time__(self, time):
        if (time == None) :
            return 0
        else :
            return time * 60 
        
    def __get_video_url__(self, identity):
        data = self.__get_data__(videoUrl, identity.replace("@", "&catalogue="))
        return data['videos'][1]['url']
    
    def __get_data__(self, baseUrl, url_id):
        url = baseUrl.format(url_id)
        if self.debug_mode:
            print "DATA URL: "+url
        data = common.fetchPage({'link': url})

        return json.loads(data['content'])
        
    def __set_debug_mode__(self):
        if __settings__.getSetting('debug') == 'true':
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
        print "Ludo:self.debug_mode Mode:"
        print self.debug_mode        
        
    
#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        Ludo()
    except:
        print_exc()
