# -*- coding: utf-8 -*-
"""
[[File(filename)]]

use [[Image]] for images.  
"""

# Imports
import urllib

from Sycamore import config
from Sycamore import wikiutil

from Sycamore.action import Files

def execute(macro, args, formatter=None):
    if not formatter:
        formatter = macro.formatter
    action = 'Files'
    pagename = formatter.page.page_name
    baseurl = macro.request.getScriptname()
    urlpagename = wikiutil.quoteWikiname(formatter.page.proper_name())

    if not args:
        return formatter.rawHTML('<b>Please supply at least a file name, '
                                 'e.g. [[File(filename.txt)]], where '
                                 'filename.txt is a file that\'s been '
                                 'uploaded to this page.</b>')
    filename = args

    macro.request.cursor.execute("""SELECT name
                                    FROM files
                                    WHERE name=%(filename)s and
                                          attached_to_pagename=%(pagename)s and
                                          wiki_id=%(wiki_id)s""",
                                 {'filename':filename,
                                  'pagename':pagename.lower(),
                                  'wiki_id':macro.request.config.wiki_id})
    result = macro.request.cursor.fetchone()
    file_exists = result

    urlfile = urllib.quote(filename)
    if not file_exists:
        #lets make a link telling them they can upload the file
        linktext = 'Upload new file "%s"' % (filename)
        return wikiutil.attach_link_tag(
            macro.request,
            '%s?action=Files&amp;rename=%s%s#uploadFileArea' % (
                wikiutil.quoteWikiname(formatter.page.proper_name()),
                urlfile,
                ''),
            linktext)

    urlfile = urllib.quote(filename)
    html = ('<span class="fileLink"><img src="%(icon)s"/>'
            '<a href="%(baseurl)s/%(urlpagename)s?action=%(action)s&amp;'
                     'do=view&target=%(urlfile)s">'
                '%(file)s'
            '</a></span>' %
            {'icon':Files.get_icon(filename, macro.request), 'baseurl':baseurl,
             'urlpagename':urlpagename, 'urlfile':urlfile, 'file':filename,
             'action':action})
    return html
