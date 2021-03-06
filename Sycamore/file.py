# -*- coding: utf-8 -*-
"""
This is the code that's use for serving up a file from the database.

It's called from RequestBase.run() if the query string indicates we want
a file (sendfile=true)
"""
# Imports
import os
import urllib
import mimetypes
import re
import time
import calendar
import math
import email

from email.Utils import parsedate_tz, mktime_tz

from Sycamore import wikidb
from Sycamore import config
from Sycamore import farm
from Sycamore.macro.image import checkTicket
from Sycamore.wikiutil import unquoteWikiname, getDomainFromURL
from Sycamore.Page import Page

def _modified_since(request, file_modified_time):
    modified_since_str = request.env.get('HTTP_IF_MODIFIED_SINCE')
    if modified_since_str:
        try:
            modified_since = mktime_tz(parsedate_tz(modified_since_str))
        except:
            # couln't parse
            return True

        if math.floor(file_modified_time) <= modified_since:
            return False

    return True

def staticFileSend(request, file_path, filename):
    file_path = os.path.join(config.web_root, file_path[1:])
    static_file = open(file_path, 'r')
    file_content = ''.join(static_file.readlines())
    static_file.close()
    mimetype = mimetypes.guess_type(file_path)[0]
    modified_time_unix = os.path.getmtime(file_path)
    datestring = time.strftime('%a, %d %b %Y %H:%M:%S',
                               time.gmtime(modified_time_unix)) + ' GMT'
    length = len(file_content)
    contentstring = 'filename="%s"' % filename
    # images are usually compressed anyway, so let's not bother gziping
    request.do_gzip = False
    request.http_headers([("Content-Type", mimetype),
                          ("Content-Length", length),
                          ("Last-Modified", datestring),
                          ("Content-Disposition", contentstring)])
    #output image
    request.write(file_content, raw=True)

def fileSend(request, pagename=None, filename=None):
    # Front_Page?file=larry_coho.jpg&thumb=yes&size=240
    # httpd_referer is like "http://daviswiki.org/blahblah/page?test=goajf"
    # (the whole string)
    # let's test against it using their possibly configured regular expression. 
    # this is to prevent image hotlinking
    referer_domain = getDomainFromURL(request.http_referer)
    if farm.isDomainInFarm(referer_domain, request):
        allowed = True
    elif request.config.referer_regexp and request.http_referer:
        allowed = re.search(request.config.referer_regexp,
                            request.http_referer, re.IGNORECASE)
    else:
        allowed = True

    if not pagename:
        pagename = request.pagename

    # if they aren't allowed to view this page or this image (bad referer)
    # then don't send them the image
    if allowed:
        if not request.user.may.read(Page(pagename, request)):
            return
    else:
        return

    deleted = False
    version = 0
    thumbnail = False
    thumbnail_size = 0
    do_download = False
    ticket = None
    size = None

    if not filename:
        filename_encoded = request.form['file'][0]
        filename = urllib.unquote(filename_encoded)
    
    if request.form.has_key('deleted'):
        if request.form['deleted'][0] == 'true':
            deleted = True
    if request.form.has_key('thumb'):
        if request.form['thumb'][0] == 'yes':
            thumbnail = True
    if request.form.has_key('size'):
        thumbnail_size = int(request.form['size'][0])
    if request.form.has_key('version'):
        version = float(request.form['version'][0])
    if request.form.has_key('download') and request.form['download'][0]:
        do_download = True
    if request.form.has_key('ticket'):
        ticket = request.form['ticket'][0]
        if not checkTicket(ticket) or not request.form.has_key('size'):
            request.http_headers()
            request.write("No file..?")
            return
        try:
            size = int(request.form['size'][0])
        except:
            request.http_headers()
            request.write("No file..?")

    d = {'filename':filename, 'page_name':pagename, 'file_version':version,
         'maxsize': size} 

    try:
        file, modified_time_unix = wikidb.getFile(request, d, deleted=deleted,
            thumbnail=thumbnail, version=version, ticket=ticket)
    except:
        request.http_headers()
        request.write("No file..?")
        return

    mimetype = mimetypes.guess_type(filename)[0]
    
    if not mimetype:
        mimetype = "application/octet-stream"

    # we're good to go to output the image
    if modified_time_unix is None: modified_time_unix = 0
    # if we're sent an If-Modified-Since header and the file hasn't
    # been modified, send 304 Not Modified
    if not _modified_since(request, modified_time_unix): 
        request.do_gzip = False
        request.status = "304 Not Modified"
        request.http_headers()
        return
    datestring = time.strftime('%a, %d %b %Y %H:%M:%S',
                               time.gmtime(modified_time_unix)) + ' GMT' 
    length = len(file)
    contentstring = 'filename="%s"' % filename.encode(config.charset)
    # images are usually compressed anyway, so let's not bother gziping
    request.do_gzip = False
    if do_download:  
        contentstring = 'attachment; %s' % contentstring
        # bogus mimetype to force browsers to behave
        mimetype = 'application/x-download' 
    request.http_headers([("Content-Type", mimetype),
                          ("Content-Length", length),
                          ("Last-Modified", datestring),
                          ("Content-Disposition", contentstring)])
    #output image
    request.write(file, raw=True)
