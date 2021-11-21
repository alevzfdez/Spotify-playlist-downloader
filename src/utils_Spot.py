#!/usr/bin/python3


from urllib3 import parse
from urllib3 import request
import config as cfg
from bs4 import BeautifulSoup
import youtube_dl

from mutagen.mp4 import MP4
from mutagen.mp4 import MP4Cover

# Spotify class
class Spoty:

    ###############################
    ######      METHODS      ######
    ###############################

    # Get full track info
    def get_track_info(Spot_URL):
        # Set and encode query params
        Query_String_Parameters = {
                'play' : 'true',
                'utm_source' : 'open.spotify.com',
                'utm_medium' : 'open',
            }

        DATA = urllib3.parse.urlencode(Query_String_Parameters)
        DATA = DATA.encode('ascii')

        # Modify original track url
        URL = Spot_URL.replace('open','play')

        # Merge data to create request URL
        request_URL = urllib3.request.Request(URL, DATA, cfg.Request_Headers)

        # Perform request and return response
        with urllib3.request.urlopen(request_URL) as response:
            track_info = response.read()
            return track_info

    # Get track name
    def get_track_name(track_info):
        # Locate and extract track name and artist
        name_begin = track_info.decode('utf-8').find('Spotify Web Player - ')
        track_info = track_info.decode('utf-8')[name_begin+21:]
        Song_name = track_info.partition('<')[0]

        Song_name = Song_name.replace('&amp;', '&')
        print ('Downloading: ' + Song_name + ' ...')
        return Song_name

    # Get album art
    def get_track_img(track_info):
        # Locate and extract track album art
        img_begin = track_info.decode('utf-8').find('https://d3rt1990lpmkn.cloudfront.net/')
        track_info = track_info.decode('utf-8')[img_begin:]
        image_URL = track_info.partition(')')[0]

        # Get album art
        return image_URL

# Download class
class Dnld:

    ###############################
    ######      METHODS      ######
    ###############################

    # Search song in download page
    def search_song(Song_name):
        # Set and encode query params
        Query_String_Parameters = {
            'search_query' : Song_name,
        }

        DATA = urllib3.parse.urlencode(Query_String_Parameters)
        DATA = DATA.encode('ascii')

        URL = 'https://www.youtube.com/results'

        request_URL = urllib3.request.Request(URL, DATA, cfg.Request_Headers)

        # Perform request and return response
        with urllib3.request.urlopen(request_URL) as response:
            response = response.read()
            soup = BeautifulSoup(response, 'lxml')
            #for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            #   print (vid['href'].partition('=')[2])
            vid = soup.find(attrs={'class':'yt-uix-tile-link'})
            vid = 'http://www.youtube.com/'+vid['href']
            return vid

    def download_track(vid, Song_name):
        # Download options
        download_options = {
                'no_warnings' : True,
                'nooverwrites' : True,
                'format': 'bestaudio/best',     # choice of quality
                'extractaudio' : True,          # only keep the audio
                'audioformat' : "mp3",          # convert to mp3 
                'outtmpl': Song_name+'.mp3',    # name the file with the ID of the video
                'noplaylist' : True,            # only download single song, not playlist
            }
        with youtube_dl.YoutubeDL(download_options) as ydl:
            ydl.download([vid])

    def add_id3(filePath, image_URL):
        # Set track and album art paths
        trackPath = str(filePath)+'.mp3'
        artist = trackPath.partition(' - ')[2].partition('.')[0]
        title = trackPath.partition(' - ')[0]

        print (artist)
        print (title)

        # Open track
        audio = MP4(trackPath)

        # Clear previous meta tags
        audio.delete()

        # Drop the entire PIL part
        with urllib3.request.urlopen(image_URL) as imFD:
            covr = MP4Cover(imFD.read(), getattr(
                        MP4Cover,
                        'FORMAT_JPEG'
                    ))

        audio['covr'] = [covr]                  # Set audio cover
        audio['title'] = title                  # Set audio title
        audio['artist'] = artist                # Set audio artist

        audio.save()

##################################################################
## MAIN
if __name__ == '__main__':

    req_track = 'https://open.spotify.com/track/7m2VsHmjyXZegtndWPgxOw'


    track_info = Spoty.get_track_info(req_track)

    Song_name = Spoty.get_track_name(track_info)

    vid = Dnld.search_song(Song_name)
    Dnld.download_track(vid, Song_name)

    image_URL = Spoty.get_track_img(track_info)
    Dnld.add_id3(Song_name, image_URL)

