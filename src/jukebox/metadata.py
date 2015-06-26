import os
import sys
import subprocess
import types
from optparse import OptionParser

from mutagen.apev2 import APEv2
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import HeaderNotFoundError
from mutagen.asf import ASF
from xdg import Mime
import magic

# Deprecated (see http://musicbrainz.org/doc/python-musicbrainz2). TODO: replace with https://github.com/alastair/python-musicbrainzngs
#from musicbrainz2.webservice import *

from urllib2 import urlopen

from PIL import Image
from StringIO import StringIO

debug = False

class WAV:
    class Info:
        def __init__(self, music_file):
            # Assume that it's 44.1kHz stereo 16 bit. Anyone storing music as wav
            # deserves anything they get.
            self.length = os.path.getsize(music_file) / ( 2 * 2 * 44100) 

    def __init__(self, music_file):
        self.info = WAV.Info(music_file)
        self.tags = None

class NullTags:
    class Info:
        def __init__(self):
            self.length = 0

    def __init__(self):
        self.info = NullTags.Info()
        self.tags = None

def get_tags(mime, music_file):
    try:
        if mime == 'audio/mpeg':
            tags = MP3(music_file)
        elif mime in ['application/ogg', 'audio/x-vorbis+ogg']:
            tags = OggVorbis(music_file)
        elif mime in ['audio/x-flac', 'audio/flac']:
            tags = FLAC(music_file)
        elif mime in ['video/mp4','audio/mp4']:
            tags = MP4(music_file)
        elif mime == 'audio/x-wav':
            tags = WAV(music_file)
        elif mime in ['audio/x-ms-asf','video/x-ms-asf']:
            tags = ASF(music_file)
        else: # don't have anything better to give the user
            print "can't find tags for mime type", mime
            tags = NullTags()
        return tags
    except HeaderNotFoundError, e:
        # Someone has uploaded a zero-length or badly corrupt file
        return NullTags()


def get_gain(mime, music_file):
    gain = None

    try:
        if mime == 'audio/mpeg':
            # mp3gain stores replay gain info in an APEv2 tag, not ID3.
            apev2 = APEv2(music_file)
            gain = apev2['REPLAYGAIN_TRACK_GAIN'].value

        elif mime == 'application/ogg':
            tags = OggVorbis(music_file)
            gain = tags['replaygain_track_gain'][0]

        elif mime == 'audio/mp4':
            tags = MP4(music_file)
            gain = tags['----:com.apple.iTunes:replaygain_track_gain'][0] # Oh, how I wish I were kidding

        elif mime == 'audio/x-flac':
            tags = FLAC(music_file)
            gain = tags['replaygain_track_gain'][0]

    except:
        pass # Lazily we assume that if anything went wrong it's because the tag was not there

    if gain:
        # We have e.g. -3.100000 dB. Remove the "dB" and convert to float
        gain = float(gain.split(" ")[0])
    return gain

# If the file does not have a gain tag, try to add one. This is expensive, so we try
# not to do it.
def evaluate_gain(mime, music_file):
    cmd = None

    if mime == 'audio/mpeg':
        cmd = ["mp3gain", "-T", music_file] # -T means modify existing file
    elif mime == 'application/ogg':
        cmd = ["vorbisgain", "-f", music_file] # -f means ignore file if it has tags
    elif mime == 'audio/mp4':
        cmd = ["aacgain", "-T", music_file] # -T means modify existing file
    elif mime == 'audio/x-flac':
        cmd = ["metaflac", "--add-replay-gain", music_file]

    if cmd:
        try:
            subprocess.call(cmd, stdout=open("/dev/null"), stderr=open("/dev/null"))
        except OSError, e:
            pass # It's probably not installed. Just continue.

def add_tag(tags, metadata, read_name, write_name):
    if tags.tags and read_name in tags.tags:
        tag = tags.tags[read_name]
        tag = tag[0]

        if isinstance(tag, tuple):
            # m4a files seem to return track number as a tuple: (tracknumber, totaltracks)
            (tag, _ignore) = tag

        metadata[write_name] = tag
        if debug:
            print "'%s' '%s'"%(write_name,tag)
        tags[write_name] = tag

def write_albumart(image_tag, metadata, tags):
    if not image_tag:
        if 'albumTitle' in tags:
            if 'artistName' in tags:
                rf = ReleaseFilter(title=tags['albumTitle'],artistName=tags['artistName'])
            else:
                rf = ReleaseFilter(title=tags['albumTitle'])
        elif 'artistName' in tags:
            rf = ReleaseFilter(artistName=tags['artistName'])
        else:
            return
        q = Query()
        try:
            r = q.getReleases(rf)
            if len(r) == 0:
                print "no such release"
                return
            r = r[0].getRelease()
            if r.getAsin() != None:
                asin = r.getAsin()
                AMAZON_IMAGE_PATH = '/images/P/%s.%s.%sZZZZZZZ.jpg'
                url = "http://ec1.images-amazon.com"+ AMAZON_IMAGE_PATH % (asin, '01', 'L')
                image_tag = urlopen(url).read()
            else:
                print "no asin"
                return
        except ConnectionError:
            print "issue connecting to Musicbrainz"
            return

    image_file = cache_base + ".jpeg"

    input_image = None
    
    if type(image_tag) == types.ListType:
        image_tag = image_tag[0]
    if isinstance(image_tag, str):
        input_image = StringIO(image_tag)
    else:
        input_image = StringIO(image_tag.data)

    image = Image.open(input_image)
    image.thumbnail((96,96), Image.ANTIALIAS)
    image.save(image_file)

    metadata["albumArt"] = True

def get_good_mime(music_file):
    mime = Mime.get_type_by_contents(music_file)
    if mime == None: # try magic instead
        mime = magic.from_file(music_file)
        mime = mime.split(";")[0]
    else:
        mime = str(mime)
    return mime

def get_metadata(music_file):
    global cache_base
    cache_base = music_file
    metadata = {}

    mime = get_good_mime(music_file)

    try:
        tags = get_tags(mime, music_file)
        gain = get_gain(mime, music_file)
        
        if not gain:
            evaluate_gain(mime, music_file)
            gain = get_gain(mime, music_file)

        metadata["totalTime"]  =tags.info.length
        if gain:
            metadata["replayGain"] = gain
    
        if mime == 'audio/mp4':
            # I don't know if this counts as a defect in Mutagen or iTunes
            add_tag(tags, metadata, "\xa9ART", "artistName")
            add_tag(tags, metadata, "\xa9alb", "albumTitle")
            add_tag(tags, metadata, "\xa9nam", "trackName")
            add_tag(tags, metadata, "trkn", "trackNumber")

            if tags.tags:
                write_albumart(tags.tags.get('covr'), metadata, tags)

        elif mime == 'audio/mpeg':
            add_tag(tags, metadata, "TPE1", "artistName")
            add_tag(tags, metadata, "TALB", "albumTitle")
            add_tag(tags, metadata, "TIT2", "trackName")
            add_tag(tags, metadata, "TRCK", "trackNumber")

            if tags.tags:
                write_albumart(tags.tags.getall('APIC'), metadata, tags)

        elif mime == "audio/x-ms-asf":
            add_tag(tags, metadata, "Author", "artistName")
            add_tag(tags, metadata, "WM/AlbumArtist", "albumTitle")
            add_tag(tags, metadata, "Title","trackName")
            add_tag(tags, metadata, "WM/TrackNumber","trackNumber")
    
        else:
            add_tag(tags, metadata, "artist", "artistName")
            add_tag(tags, metadata, "album", "albumTitle")
            add_tag(tags, metadata, "title", "trackName")
            add_tag(tags, metadata, "tracknumber", "trackNumber")
    
    except:
        if debug:
            raise
        import traceback
        metadata["error"] = traceback.format_exc()

    return metadata

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d","--debug",help="Write errors out to command line rather than the file for debugging purposes",default=False,dest="debug",action="store_true")
    (opts,args) = parser.parse_args()
    debug = opts.debug

    if len(args)!=1:
        parser.error("Usage: %s <path to file>"%sys.argv[0])

    print get_metadata(args[0])
# vim: tabstop=4 shiftwidth=4 et
