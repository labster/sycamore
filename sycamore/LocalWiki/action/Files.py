# -*- coding: iso-8859-1 -*-
"""
    LocalWiki - Files action

    This action lets a page have multiple attachment files.
    It writes to the images and oldimages tables.

    Form values: action=Attachment
    1. with no 'do' key: returns file upload form
    2. do=attach: accept file upload and saves the file in images
    3. /pagename/fname?action=Attachment&do=view&target=fname
       return contents of the image file with the name fname along with some html and stuff.

    To insert an attachment into the page, use the "attachment:" pseudo
    schema.  

    @copyright: 2001 by Ken Sugino (sugino@mediaone.net)
    @copyright: 2001-2004 by J�rgen Hermann <jh@web.de>
    @copyright: 2005 by Philip Neustrom <philipn@gmail.com>
    @license: GNU GPL, see COPYING for details.
"""

import os, mimetypes, time, urllib, string
from LocalWiki import config, user, util, wikiutil, wikidb
from LocalWiki.Page import Page
from LocalWiki.util import LocalWikiNoFooter, filesys
import xml.dom.minidom

action_name = __name__.split('.')[-1]
htdocs_access = isinstance(config.attachments, type({}))


#############################################################################
### External interface - these are called from the core code
#############################################################################


def getAttachUrl(pagename, filename, request, addts=0, escaped=0, deleted=0, version='', thumb=False, size=0):
    """ Get URL that points to image `filename` of page `pagename`.

        If 'addts' is true, a timestamp with the file's modification time
        is added, so that browsers reload a changed file.
        NOTE:  FOR NOW we ignore addts..may add back if needed later.
    """
    if not deleted:
      if not thumb:
        url = "%s/%s?img=true&file=%s" % (wikiutil.baseScriptURL(), 
            wikiutil.quoteWikiname(pagename),
            urllib.quote_plus(filename))
      else:
        if not size:
	  url = "%s/%s?img=true&file=%s&thumb=yes" % (wikiutil.baseScriptURL(), 
            wikiutil.quoteWikiname(pagename),
            urllib.quote_plus(filename))
	else:
	  url = "%s/%s?img=true&file=%s&thumb=yes&size=%s" % (wikiutil.baseScriptURL(), 
            wikiutil.quoteWikiname(pagename),
            urllib.quote_plus(filename), size)
    else:
      url = "%s/%s?img=true&file=%s&deleted=true&version=%s" % (wikiutil.baseScriptURL(), 
            wikiutil.quoteWikiname(pagename),
            urllib.quote_plus(filename), version)



    return url

def getIndicator(request, pagename):
    """ Get an attachment indicator for a page (linked clip image) or
        an empty string if not attachments exist.
    """
    _ = request.getText

    db = wikidb.connect()
    cursor = db.cursor()
    cursor.execute("SELECT count(name) from images where attached_to_pagename=%s", (self.page_name))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result:
      if result[0]:
        num_images == _('[%d images]') % result[0]
    image_icon = request.theme.make_icon('attach', vars={ 'attach_count': attach_count })
    image_link = wikiutil.link_tag(request,
        "%s?action=Files" % wikiutil.quoteWikiname(pagename),
        attach_icon)

    return attach_link

def _info_header(request, pagename, in_images_list_area=True):
    """ just spews out the initial bit of info tabbery on the images page so our interface is consistent.
    """
    qpagename = wikiutil.quoteWikiname(pagename)
    historylink =  wikiutil.link_tag(request, '%s?action=info' % qpagename,
        '%(title)s' % {'title': 'Page\'s Revision History'})
    generallink =  wikiutil.link_tag(request, '%s?action=info&amp;general=1' % qpagename,
        '%(title)s' % {'title': 'Page\'s General Info'})
    imageslink = wikiutil.link_tag(request, '%s?action=Files' % qpagename, 'Page\'s Images')

    if in_images_list_area:
      header = "<p>[%s] [%s] [Page's Images]</p>" % (historylink, generallink)
    else:
      header = "<p>[%s] [%s] [%s]</p>" % (historylink, generallink, imageslink)

    return header

def _revisions_footer(request,revisions, baseurl, urlpagename, action, filename):
    text = '<div><h4>Image history</h4></div><ul>'
    for revision in revisions:
      text += '<li>[<a href="%s/%s?action=%s&amp;do=restore&amp;target=%s&amp;uploaded_time=%s&amp;">revert</a>] <a href="%s/%s?action=%s&amp;do=view&amp;target=%s&amp;version=%s">%s</a> uploaded by %s.  %s deleted by %s.</li>' % (baseurl, urlpagename, action, filename, revision[4], baseurl, urlpagename, action, filename, revision[4], revision[0], Page(revision[1]).link_to(request), revision[2], Page(revision[3]).link_to(request))
    text += '</ul>'
    return text

def info(pagename, request):
    """ Generate snippet with info on the attachment for page `pagename`.
    """
    _ = request.getText

    db = wikidb.connect()
    cursor = db.cursor()
    cursor.execute("SELECT count(name) from images where attached_to_pagename=%s",(pagename))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result:  image_num = result[0]
    else: image_num = 0

    if image_num: 
      image_attach_info = _('There are <a href="%(link)s">%(count)s image(s)</a> stored for this page.') % {
        'count': image_num,
        'link': Page(pagename).url(request, "action=Files")
    }
    else:
      image_attach_info = _('There are no <a href="%(link)s">image(s)</a> stored for this page.') % {
        'link': Page(pagename).url(request, "action=Files")
    }



    request.write("\n<p>\n%s\n</p>\n" % image_attach_info)


#############################################################################
### Internal helpers
#############################################################################

def _has_deleted_images(pagename):
    db = wikidb.connect()
    cursor = db.cursor()
    cursor.execute("""
        SELECT oldimages.name from oldimages where
	            (oldimages.name, oldimages.attached_to_pagename) not in (SELECT images.name, images.attached_to_pagename from images) and oldimages.attached_to_pagename=%s""", (pagename))

    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result: return True
    else: return False
	
   

def _get_filelist(request, pagename):
    _ = request.getText
    files = []

    # access directory
    db = wikidb.connect()
    cursor = db.cursor()
    cursor.execute("SELECT name from images where attached_to_pagename=%s", (pagename))
    result = cursor.fetchone()
    while result:
     files.append(result[0])
     result = cursor.fetchone()
    cursor.close()
    db.close()

    files.sort()

    str = ""
    baseurl = request.getScriptname()
    action = action_name
    urlpagename = wikiutil.quoteWikiname(pagename)

    if files:
        str = str + _("<p>"
            "To refer to images on a page, use <strong><tt>attachment:filename</tt></strong>, \n"
            "as shown below in the list of files. \n"
            "Do <strong>NOT</strong> use the URL of the image \n"
            "since this is subject to change and can break easily.</p>"
        )
        str = str + "<ul>"

        label_del = _("Delete")
        label_edit = _("Edit")
        label_view = _("View & Info")

                
        for file in files:
            urlfile = urllib.quote_plus(file)
            file = urllib.quote(file)
            base, ext = os.path.splitext(file)
            get_url = getAttachUrl(pagename, file, request, escaped=1)
            parmdict = {'baseurl': baseurl, 'urlpagename': urlpagename, 'action': action,
                        'urlfile': urlfile, 'label_del': label_del,
                        'base': base, 'label_edit': label_edit,
                        'label_view': label_view, 'get_url': get_url,
                        'file': file, 
                        'pagename': pagename}
            
            del_link = ''
            if request.user.may.delete(pagename):
                del_link = ' | <a href="%(baseurl)s/%(urlpagename)s' \
                    '?action=%(action)s&amp;do=del&amp;target=%(urlfile)s">%(label_del)s</a>' % parmdict

            viewlink = '<a href="%(baseurl)s/%(urlpagename)s?action=%(action)s&amp;do=view&target=%(urlfile)s">%(label_view)s</a>' % parmdict

            parmdict['viewlink'] = viewlink
            parmdict['del_link'] = del_link
            str = str + ('<li>[%(viewlink)s'
                '%(del_link)s]'
                ' attachment:<strong>%(file)s</strong></li>') % parmdict
        str = str + "</ul>"
    else:
        str = '%s<p>%s</p>' % (str, _("No images stored for %(pagename)s") % {'pagename': pagename})
    
    if _has_deleted_images(pagename): str += '[<a href="%s/%s?action=%s&amp;do=show_deleted">Page\'s deleted images</a>]' % (baseurl, urlpagename, action)

    return str
        
    
def error_msg(pagename, request, msg):
    #Page(pagename).send_page(request, msg=msg)
    request.http_headers()
    wikiutil.simple_send_title(request, pagename)
    request.write('<div id="content">')
    send_uploadform(pagename, request)
    request.write('</div>')

#############################################################################
### Create parts of the Web interface
#############################################################################

def send_link_rel(request, pagename):
    attach_dir = ''
    if os.path.isdir(attach_dir):
        files = os.listdir(attach_dir)
        files.sort()
        for file in files:
            get_url = getAttachUrl(pagename, file, request, escaped=1)
            request.write('<link rel="Appendix" title="%s" href="%s">\n' % (
                wikiutil.escape(file), get_url))


def send_uploadform(pagename, request):
    """ Send the HTML code for the list of already stored attachments and
        the file upload form.
	
 	Currently, the upload form is a part of the 'info' interface.  This means that it contains links to the other info things, despite not being, code-wise, a part of the info set of actions.
    """
    _ = request.getText
    
    if not request.user.may.read(pagename):
        request.write('<p>%s</p>' % _('You are not allowed to view this page.'))
        return

    #request.write('<h2>' + _("Attached Images") + '</h2>')
    request.write(_info_header(request, pagename))

    request.write(_get_filelist(request, pagename))

    if not request.user.may.edit(pagename):
        request.write('<p>%s</p>' % _('You are not allowed to attach an image to this page.'))
        return


    request.write('<h2>' + _("New Image Attachment") + '</h2><p>' +
_("""An upload will never overwrite an existing file. If there is a name
conflict, you have to rename the file that you want to upload.
Otherwise, if "Save as" is left blank, the original filename will be used (might be ugly) . You should give it a name!  Just name it whatever.jpg/png/gif (in "Save as"). Try to avoid spaces because they come out poorly.""") + '</p>')
    request.write("""
<form action="%(baseurl)s/%(pagename)s" method="POST" enctype="multipart/form-data">
<dl>
<dt>%(upload_label_file)s</dt>
<dd><input type="file" name="file" size="50"></dd>
<dt>%(upload_label_rename)s</dt>
<dd><input type="text" name="rename" size="50" value="%(rename)s"></dd>
</dl>
<p>
<input type="hidden" name="action" value="%(action_name)s">
<input type="hidden" name="do" value="upload">
<input type="submit" value="%(upload_button)s">&nbsp;&nbsp;<input type="button" onclick="opener.preview();window.close();" value="Close and Preview">
</p>
</form>
""" % {
    'baseurl': request.getScriptname(),
    'pagename': wikiutil.quoteWikiname(pagename),
    'action_name': action_name,
    'upload_label_file': _('File to upload'),
    #'upload_label_mime': _('MIME Type (optional)'),
    'upload_label_rename': _('Save as'),
    'rename': request.form.get('rename', [''])[0],
    'upload_button': _('Upload'),
})
    request.write('<h3>' + _("How do I do this?") + '</h3>' +
_("""Once you've selected a file on your hard disk, use "Save as" to name it whateveryouwant.png/jpg/gif.  Then click "Upload" to upload the file to the page.  But, <b>you have to tell the page where you want the image to go!</b>  So, just go into the page (edit it) and add the line <tt>attachment:whatyounamedyourimage</tt> where you want the image to appear.  That's it!<br><br>Next to each uploaded image is the line you need to put into the page to make the image appear, e.g. <tt>attachment:theimage.jpg</tt>"""))


#############################################################################
### Web interface for file upload, viewing and deletion
#############################################################################

def execute(pagename, request):
    """ Main dispatcher for the 'Files' action.
    """
    _ = request.getText

    msg = None
    if action_name in config.excluded_actions:
        msg = _('File attachments are not allowed in this wiki!')
    elif not request.form.has_key('do'):
        upload_form(pagename, request)
    elif request.form['do'][0] == 'upload':
        if request.user.may.edit(pagename):
            do_upload(pagename, request)
        else:
            msg = _('You are not allowed to attach an image to this page.')
    elif request.form['do'][0] == 'del':
        if request.user.may.delete(pagename):
            del_image(pagename, request)
        else:
            msg = _('You are not allowed to delete images on this page.')
    elif request.form['do'][0] == 'restore':
        if request.user.may.edit(pagename):
            restore_image(pagename, request)
        else:
            msg = _('You are not allowed to restore images to this page.')

    elif request.form['do'][0] == 'show_deleted':
           show_deleted_images(pagename, request)
    elif request.form['do'][0] == 'get':
        if request.user.may.read(pagename):
            get_file(pagename, request)
        else:
            msg = _('You are not allowed to get imagse from this page.')
    elif request.form['do'][0] == 'view':
        if request.user.may.read(pagename):
            view_file(pagename, request)
        else:
            msg = _('You are not allowed to view images of this page.')
    else:
        msg = _('Unsupported upload action: %s') % (request.form['do'][0],)

    if msg:
        error_msg(pagename, request, msg)


def upload_form(pagename, request, msg=''):
    _ = request.getText

    request.http_headers()
    wikiutil.simple_send_title(request, pagename, msg=msg, strict_title='Images for "%s"' % pagename)

    request.write('<div id="content">\n') # start content div
    send_uploadform(pagename, request)
    request.write('</div>\n') # end content div
    wikiutil.send_footer(request, pagename, showpage=1, noedit=True)

def send_title(request, desc, pagename, msg, title=''):
    request.write(
        '<html><head>'
        '<link rel="stylesheet" type="text/css" charset="iso-8859-1" media="all" href="' +config.url_prefix + '/eggheadbeta/css/common.css">'
        '<link rel="stylesheet" type="text/css" charset="iso-8859-1" media="screen" href="' +config.url_prefix + '/eggheadbeta/css/screen.css">'
        '<link rel="stylesheet" type="text/css" charset="iso-8859-1" media="print" href="' +config.url_prefix + 'eggheadbeta/css/print.css">'
        '<meta name="robots" content="noindex,nofollow"/><title>%s</title></head><body><p><h3>&nbsp;%s</h3></p>' % (title, desc)
        )
    if msg :
      request.write('<div id="message"><p>%s</p></div>' % msg)

def do_upload(pagename, request):
    _ = request.getText

    # make filename
    filename = None
    if request.form.has_key('file__filename__'):
        filename = request.form['file__filename__']
    rename = None
    if request.form.has_key('rename'):
        rename = request.form['rename'][0].strip()

    # if we use twisted, "rename" field is NOT optional, because we
    # can't access the client filename
    if rename:
        filename = target = rename
    elif filename:
        target = filename
    else:
        error_msg(pagename, request, _("Filename of image not specified!"))
        return

    # RESTRICT FILE EXTENSIONS - EXPERIMENTAL

    if not string.upper(filename).endswith(".JPG") and not string.upper(filename).endswith(".JPEG") and not string.upper(filename).endswith(".PNG") and not string.upper(filename).endswith(".GIF"): 
        error_msg(pagename, request, _("You may only attach image files."))
        return

    if string.find(filename, '<') or string.find(filename, '>') or string.find(filename, '&') or string.find(filename, '?') or string.find(filename, '"'):
        error_msg(pagename, request, _("The characters '<', '>', '&', '\"', and '?' are not allowed in file names."))
        return

	
    # get file content
    filecontent = request.form['file'][0]
    
    # LIMIT ATTACHMENT SIZE - EXPERIMENTAL
    if len(filecontent) > 512000 :
        error_msg(pagename, request, _("Files must be 500Kb or smaller.")) 
        return

    target = wikiutil.taintfilename(target)

    # set mimetype from extension, or from given mimetype
    type, encoding = mimetypes.guess_type(target)
    if not type:
        ext = None
        if request.form.has_key('mime'):
            ext = mimetypes.guess_extension(request.form['mime'][0])
        if not ext:
            type, encoding = mimetypes.guess_type(filename)
            if type:
                ext = mimetypes.guess_extension(type)
            else:
                ext = ''
        target = target + ext
    
    # get directory, and possibly create it
    #attach_dir = getAttachDir(pagename, create=1)
    # save file
    db = wikidb.connect()
    cursor = db.cursor()
    cursor.execute("SELECT name from images where attached_to_pagename=%s and name=%s", (pagename, filename))
    result = cursor.fetchone()

    if result:
      if result[0]:
        msg = _("Attachment '%(target)s' already exists.") % {
            'target': target}
	cursor.close()
	db.close()
    else:
	uploaded_time = time.time()
	uploaded_by = request.user.id
	cursor.execute("start transaction;")
	cursor.execute("INSERT into images set name=%s, image=%s, uploaded_time=FROM_UNIXTIME(%s), uploaded_by=%s, attached_to_pagename=%s, uploaded_by_ip=%s", (filename, filecontent, uploaded_time, uploaded_by, pagename, request.remote_addr))
	cursor.execute("commit;")

	
        bytes = len(filecontent)
        msg = _("Attachment '%(target)s'"
                " with %(bytes)d bytes saved.") % {
                'target': target, 'bytes': bytes}

    # return attachment list
    upload_form(pagename, request, msg)


def del_image(pagename, request):
    _ = request.getText

    filename = request.form['target'][0]
    db = wikidb.connect()
    cursor = db.cursor()
    cursor.execute("start transaction;")
    cursor.execute("INSERT into oldimages set name=%s, attached_to_pagename=%s, image=(select image from images where name=%s and attached_to_pagename=%s), uploaded_by=(select uploaded_by from images where name=%s and attached_to_pagename=%s), uploaded_time=(select uploaded_time from images where name=%s and attached_to_pagename=%s), deleted_time=FROM_UNIXTIME(%s), deleted_by=%s, uploaded_by_ip=(select uploaded_by_ip from images where name=%s and attached_to_pagename=%s), deleted_by_ip=%s;",(filename, pagename, filename, pagename, filename, pagename, filename, pagename, time.time(), request.user.id, filename, pagename, request.remote_addr))
    cursor.execute("DELETE from images where name=%s and attached_to_pagename=%s", (filename, pagename))
    cursor.execute("commit;")
    result = cursor.fetchone()
    cursor.close()
    db.close()

    upload_form(pagename, request, msg=_("Image '%(filename)s' deleted.") % {'filename': filename})

def restore_image(pagename, request):
    _ = request.getText

    timenow = time.time()
    filename = request.form['target'][0]
    uploaded_time = request.form['uploaded_time'][0]

    db = wikidb.connect()
    cursor = db.cursor()
    cursor.execute("SELECT name from images where name=%s and attached_to_pagename=%s", (filename, pagename))
    is_in_images = cursor.fetchone()
    if is_in_images:
	# this means the image wasn't most recently deleted but the user still would like to revert to this version of the image
	cursor.execute("start transaction;")
	#backup the current version of the image
	cursor.execute("INSERT into oldimages set name=%s, attached_to_pagename=%s, image=(select image from images where name=%s and attached_to_pagename=%s), uploaded_by=(select uploaded_by from images where name=%s and attached_to_pagename=%s), uploaded_time=(select uploaded_time from images where name=%s and attached_to_pagename=%s), deleted_time=FROM_UNIXTIME(%s), deleted_by=%s;",(filename, pagename, filename, pagename, filename, pagename, filename, pagename, timenow, request.user.id))
	#revert by putting their version as the current version
	cursor.execute("UPDATE images set image=(select image from oldimages where name=%s and attached_to_pagename=%s and uploaded_time=FROM_UNIXTIME(%s)), uploaded_by=%s, uploaded_time=FROM_UNIXTIME(%s)", (filename, pagename, uploaded_time, request.user.id, timenow))
	cursor.execute("commit;")

    else:
      cursor.execute("start transaction;")
      cursor.execute("INSERT into images set name=%s, attached_to_pagename=%s, image=(select image from oldimages where name=%s and attached_to_pagename=%s and uploaded_time=FROM_UNIXTIME(%s)), uploaded_by=%s, uploaded_time=FROM_UNIXTIME(%s);",(filename, pagename, filename, pagename, uploaded_time, request.user.id, time.time()))
      cursor.execute("commit;")
    cursor.close()
    db.close()

    upload_form(pagename, request, msg=_("Image '%s' version %s reactivated on page \"%s\".") % (filename, time.asctime(time.gmtime(float(uploaded_time))), pagename))




def send_viewfile(pagename, request):
    _ = request.getText
    revisions = []

    if not request.form.get('target', [''])[0]:
        error = _("Filename of attachment not specified!")
        request.write(error)
	return

    else:
        filename = request.form['target'][0]
	if request.form.get('version', [''])[0]: version = request.form['version'][0]
	else: version = ''

	db = wikidb.connect()
        cursor = db.cursor()
        if not version:
 	  # in some rare cases the images were not uploaded by a user, so let's check to see if there's information on the upload-er
	  cursor.execute("SELECT images.uploaded_by from images where name=%s and attached_to_pagename=%s", (pagename, filename))
	  result = cursor.fetchone()
 	  cursor.execute("SELECT images.name, images.uploaded_time, users.name, length(image), UNIX_TIMESTAMP(images.uploaded_time) from images, users where attached_to_pagename=%s and images.name=%s and users.id=images.uploaded_by", (pagename,filename))
	else:
          cursor.execute("SELECT images.name, images.uploaded_time, users.name, length(image), UNIX_TIMESTAMP(images.uploaded_time) from images, users where attached_to_pagename=%s and images.name=%s and users.id=images.uploaded_by and images.uploaded_time=%s", (pagename,filename,version))
        result = cursor.fetchone()
        cursor.close()
        db.close()
	deleted_image = False

	request.write("<h4 style=\"padding-bottom: 1em;\">Image '%s' of page %s:</h4>" % (filename, Page(pagename).link_to(request)))

	if result:
	# this means the image is 'active' and wasn't most recently deleted.
        # let's get some image history, if it's around
   	   db = wikidb.connect()
           cursor = db.cursor()
           cursor.execute("SELECT oldimages.name, oldimages.uploaded_time, users.name, oldimages.deleted_time, users2.name, UNIX_TIMESTAMP(oldimages.uploaded_time) from oldimages, users, users as users2 where attached_to_pagename=%s and oldimages.name=%s and users.id=oldimages.uploaded_by and users2.id=oldimages.deleted_by order by oldimages.uploaded_time desc;", (pagename, filename))
           revisions_item = cursor.fetchone()
	   while revisions_item:
   	     revisions.append((revisions_item[1], revisions_item[2], revisions_item[3], revisions_item[4], revisions_item[5]))
             revisions_item = cursor.fetchone()
           cursor.close()
           db.close()
        else:
	   # let's see if the image was deleted, and if so we'll display it with a note about how it was removed.
	   db = wikidb.connect()
           cursor = db.cursor()
	   if not version:
	   # grab the most recent version of the image
             cursor.execute("SELECT oldimages.name, oldimages.uploaded_time, users.name, length(oldimages.image), oldimages.deleted_time, users2.name, UNIX_TIMESTAMP(oldimages.uploaded_time) from oldimages, users, users as users2 where attached_to_pagename=%s and oldimages.name=%s and users.id=oldimages.uploaded_by and users2.id=oldimages.deleted_by order by oldimages.uploaded_time desc;", (pagename,filename))
	   else:
	     # let's grab the proper version of the image
	     cursor.execute("SELECT oldimages.name, oldimages.uploaded_time, users.name, length(oldimages.image), oldimages.deleted_time, users2.name, UNIX_TIMESTAMP(oldimages.uploaded_time) from oldimages, users, users as users2 where attached_to_pagename=%s and oldimages.name=%s and users.id=oldimages.uploaded_by and users2.id=oldimages.deleted_by and oldimages.uploaded_time=FROM_UNIXTIME(%s) order by oldimages.uploaded_time desc;", (pagename,filename, version))
	   revisions_and_latest = cursor.fetchall()
	   if revisions_and_latest:
	      result = revisions_and_latest[0]
	      revisions = revisions_and_latest[1:]
	      revisions_tuples = []	
	      for item in revisions:
	        revisions_tuples.append((item[1], item[2], item[4], item[5], item[6]))
	      revisions = revisions_tuples
           cursor.close()
           db.close()
	   if result:
	      deleted_image = True
	   else:
             error = _("Image '%(filename)s' does not exist!") % {'filename': filename}
	     request.write(error)
	     return

	uploaded_time = ''
	uploaded_by = ''
	deleted_time = ''
	deleted_by = ''
	image_size = 0
	if result[1]: uploaded_time = result[1]
	if result[2]: uploaded_by = result[2]
	if result[3]: image_size = result[3]
	if deleted_image:
	  deleted_time = result[4]
	  deleted_by = result[5]
	  uploaded_time_unix = result[6]
	else:
	  uploaded_time_unix = result[4]

        image_size = image_size/1024
    

    #request.write('<h2>' + _("Attachment '%(filename)s'") % {'filename': filename} + '</h2>')
    baseurl = request.getScriptname()
    action = action_name
    urlpagename = wikiutil.quoteWikiname(pagename)

    timestamp = ''
    if deleted_image:
      request.write('<p>This version of the image was <b>deleted</b> by %s on %s.</p>' % (Page(deleted_by).link_to(request), deleted_time))
      request.write('<img src="%s%s" alt="%s">' % (
        getAttachUrl(pagename, filename, request, escaped=1, deleted=1, version=version), timestamp, wikiutil.escape(filename, 1)))
    else:
      request.write('<img src="%s%s" alt="%s">' % (
        getAttachUrl(pagename, filename, request, escaped=1), timestamp, wikiutil.escape(filename, 1)))

    if uploaded_by:
      request.write('<p>Uploaded by %s to page %s on %s.  Image size: %sKB</p>' % (Page(uploaded_by).link_to(request), Page(pagename).link_to(request),uploaded_time, image_size))
    else:
      request.write('<p>Upload information unknown.  Please refer to the original page </p>')

    if deleted_image: request.write('<p>[<a href="%s/%s?action=%s&amp;do=restore&amp;target=%s&amp;uploaded_time=%s">revert to this version of the image</a>]</p>' %(baseurl, urlpagename, action, filename, uploaded_time_unix))

    if revisions:
      request.write(_revisions_footer(request, revisions, baseurl, urlpagename, action, filename))


    
def view_file(pagename, request):
    _ = request.getText

    filename = request.form['target'][0]

    # send header & title
    pagetitle = filename + " on " + config.sitename
    request.http_headers()
    wikiutil.simple_send_title(request, pagename, strict_title='Image \'%s\' on "%s"' % (filename, pagename))

    # send body
    request.write('<div id="content">\n') # start content div
    request.write(_info_header(request, pagename, in_images_list_area=False))
    send_viewfile(pagename, request)
    request.write('</div>\n') # end content div
    #wikiutil.send_footer(request, pagename, showpage=1, noedit=True)

def show_deleted_images(pagename, request):
    _ = request.getText

    # send header & title
    pagetitle = "Deleted images for \"%s\"" % (pagename)
    db = wikidb.connect()
    cursor = db.cursor()
    cursor.execute("SELECT * from (SELECT oldimages.name as name, oldimages.deleted_time, users.name as user_name, UNIX_TIMESTAMP(oldimages.uploaded_time) from oldimages, users where attached_to_pagename=%s and users.id=oldimages.deleted_by and (oldimages.name, oldimages.attached_to_pagename) not in (SELECT images.name, images.attached_to_pagename from images) order by deleted_time desc) as hack_table group by name order by deleted_time desc;", (pagename))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    text_list = "<p><ul>"
    baseurl = request.getScriptname()
    action = action_name
    urlpagename = wikiutil.quoteWikiname(pagename)

    for item in result:
      text_list += "<li>[<a href=\"%s/%s?action=%s&amp;do=restore&amp;target=%s&amp;uploaded_time=%s\">restore to page</a>] <a href=\"%s/%s?action=%s&amp;do=view&amp;target=%s\">%s</a> deleted by %s on %s.</li>" % (baseurl, urlpagename, action, item[0], item[3], baseurl, urlpagename, action, item[0], item[0], Page(item[2]).link_to(request), item[1])


    request.http_headers()
    wikiutil.simple_send_title(request, pagetitle, strict_title='Deleted imags for "%s"' % pagename)


    # send body
    request.write('<div id="content">\n') # start content div
    request.write(_info_header(request, pagename, in_images_list_area=False))
    request.write('<p>These images have been <b>deleted</b> from the original page, which means they can\'t be included in the wiki anymore and are possibly (in some cases) subject to permanent deletion:</p>')
    request.write(text_list)
    request.write('</div>\n') # end content div
    wikiutil.send_footer(request, pagename, showpage=1, noedit=True)



#############################################################################
### File attachment administration
#############################################################################

def do_admin_browser(request):
    """ Browser for SystemAdmin macro.
	This shit is broken.
    """
    from LocalWiki.util.dataset import TupleDataset, Column
    _ = request.getText

    data = TupleDataset()
    data.columns = [
        Column('page', label=('Page')),
        Column('file', label=('Filename')),
        Column('size',  label=_('Size'), align='right'),
        Column('action', label=_('Action')),
    ]

    # iterate over pages that might have attachments
    pages = os.listdir(getBasePath())
    for pagename in pages:
        # check for attachments directory
        page_dir = getAttachDir(pagename)
        if os.path.isdir(page_dir):
            # iterate over files of the page
            files = os.listdir(page_dir)
            for filename in files:
                filepath = os.path.join(page_dir, filename)
                data.addRow((
                    Page(pagename).link_to(request, querystr="action=Files"),
                    wikiutil.escape(filename),
                    os.path.getsize(filepath),
                    '',
                ))

    if data:
        from LocalWiki.widget.browser import DataBrowserWidget

        browser = DataBrowserWidget(request)
        browser.setData(data)
        return browser.toHTML()

    return ''
