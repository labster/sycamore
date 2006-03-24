# -*- coding: iso-8859-1 -*-
"""
    Sycamore - Configuration

    Note that there are more config options than you'll find in
    the version of this file that is installed by default; see
    the module Scyamore.config for a full list of names and their
    default values.

    Also, the URL http://purl.net/wiki/moin/HelpOnConfiguration has
    a list of config options.
            (for MoinMoin)

    @copyright: 2000-2003 by J?rgen Hermann <jh@web.de>
    @copyright: 2005-2006 by Philip Neustrom <philipn@gmail.com>
    @license: GNU GPL, see COPYING for details.
"""
import os.path
__directory__ = os.path.dirname(os.path.abspath(__file__))

# If you run several wikis on one host (commonly called a wiki farm),
# uncommenting the following allows you to load global settings for
# all your wikis. You will then have to create "farm_config.py" in
# the MoinMoin package directory.
# this file is also used for the blacklist (which, by, default, has nothing in it)..just leave it uncommented and it won't cause any problems, promise.
from farmconfig import *

# basic options (you normally need to change these)
sitename = 'Sycamore Default Install'
interwikiname = None

#no slashes at the end on these guys !!
data_dir = os.path.join(__directory__, 'data')

# this is the root where, say, a href="/" resolves to (considering whther or not you have a domain)
web_root = os.path.join(__directory__, 'web')

# this is what's after the url if your wiki is in a directory
# e.g. '' for the root, and '/mywiki' if it's in directory mywiki
web_dir = ''

# this is where the theme css is stored
#  this is relative to the web server's root
url_prefix = '/wiki'

#displayed logo. If you don't want an image logo, comment this out and the sitename will be used as a text-based logo.
#image_logo = 'syclogo.png'

# the phrase displayed in the title on the front page
#catchphrase = 'The definitive resource for Davis, California'
catchphrase = 'Your phrase here..'

#if the main files are placed somewhere inside of a directory such as http://daviswiki.org/dev/index.cgi as opposed to http://daviswiki.org/index.cgi
#then this var lets us figure out the proper relative link
#as of 12-29-04 we aren't yet using this, but we should use this once we have an independent dev database
# this is where the main code is installed -- in your web server documents' directory
# so if you have ~/public_html/wiki/index.cgi as your wiki executable then this would be "wiki/index.cgi"
# if there is no index.cgi then it would be "wiki"
# this is anything after the root of where your web stuff is installed
relative_dir = 'index.cgi'

#your domain (used for cookies, etc)
# uncomment only if you've got a domain and want cookies to work across subdomains
domain = 'localhost'

# turn to 0 if you want to disable the built-in talk-page theme stuff
talk_pages = 1

# This is the license text that appears in the page footer.  If you don't want a license, comment this out.  You'll want to make the <a href="copyrightpage"> yourself.
license_text = """<!-- Creative Commons Licence -->Except where otherwise noted, this content is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/2.0/">Creative Commons License</a>.  See <a href="/index.cgi/Copyrights">Copyrights</a>.<!-- /Creative Commons License --><!--  <rdf:RDF xmlns="http://web.resource.org/cc/" xmlns:dc="http://purl.org/dc/elements/1.1/"     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"> <Work rdf:about=""><dc:type rdf:resource="http://purl.org/dc/dcmitype/Text" /><license rdf:resource="http://creativecommons.org/licenses/by/2.0/" /> </Work>  <License rdf:about="http://creativecommons.org/licenses/by/2.0/"> <permits rdf:resource="http://web.resource.org/cc/Reproduction" /> <permits rdf:resource="http://web.resource.org/cc/Distribution" /> <requires rdf:resource="http://web.resource.org/cc/Notice" /> <requires rdf:resource="http://web.resource.org/cc/Attribution" /> <permits rdf:resource="http://web.resource.org/cc/DerivativeWorks" /> </License>  </rdf:RDF>  -->"""

# This will be shown under "save changes" in the wiki editor.  If you're going to use a license then it's good to have a small snippet of text that they see when saving.
edit_agreement_text = """By clicking "Save Changes" you are agreeing to release your contribution under the <a href="http://creativecommons.org/licenses/by/2.0/">Creative Commons-By license</a>, unless noted otherwise. <b>Do not submit copyrighted work (including images) without permission.</b>  For more information, see <a href="/index.cgi/Copyrights">Copyrights</a>."""


# These are the buttons that appear to the right in the footer.
footer_buttons = ["""<a href="http://creativecommons.org/licenses/by/2.0/"><img alt="Creative Commons License" border="0" src="/wiki/eggheadbeta/img/cc.png"/></a>""", """<a href="/index.cgi/Donate"><img name="rollover" onMouseOver="document.rollover.src=donate2.src;" onMouseOut="document.rollover.src=donate.src;" src="/wiki/eggheadbeta/img/donate.png" border="0" alt="donate"/></a>"""]

# MySQL database settings.
db_type = 'mysql'
db_name = 'wiki'
db_user = 'root'
db_user_password = ''
db_host = 'localhost'

# location of the GNU Diff3 application.
diff3_location = '/usr/bin/diff3'

#Memcache settings.  This is if you want a high-performance wiki.
memcache = True
memcache_servers = ['127.0.0.1:11211']
# memcache_servers can be either ['server1:port', 'server2:port'] or given with weights as in
#  [('server1:port', 1), ('server2:port', 3)]  (say that server2 has 3x the memory as server1)

has_xapian = True
#location of the search dbs.  you probably shouldn't have to change this.
search_db_location = os.path.join(data_dir, 'search')

# Referer regular expression is used to filter out http referers from image viewing.
# It's for stopping image hotlinking, basically.
# leave blank if you don't care about people leeching images.
# to match against any url from any subdomain of daviswiki we would write:
# referer_regexp = 'http\:\/\/(([^\/]*\.)|())daviswiki\.org\/.*'
#referer_regexp = 'http\:\/\/(([^\/]*\.)|())localhost\/.*'

# encoding and WikiName char sets
# (change only for outside America or Western Europe)
charset = 'utf-8'
upperletters = "A-Z??????????????????????????????"
lowerletters = "0-9a-z?????????????????????????????????"

# options people are likely to change due to personal taste
#show_hosts = 1                          # show hostnames?
#nonexist_qm = 0                         # show '?' for nonexistent?
#backtick_meta = 1                       # allow `inline typewriter`?
#allow_extended_names = 1                # allow ["..."] markup?
##edit_rows = 20                          # editor size
#max_macro_size = 50                     # max size of RecentChanges in KB (0=unlimited)
#bang_meta = 1                           # use ! to escape WikiNames?
#show_section_numbers = 0                # enumerate headlines?

allowed_actions = ['DeletePage','AttachFile']

# for standalone http server (see installhtml/index)
httpd_host = "localhost"
httpd_port = 80
httpd_user = "nobody"

theme_default = 'eggheadbeta'
theme_force = True
acl_enabled = 1
acl_rights_default = "AdminGroup:admin,read,write,delete,revert TestMe:admin,read,write,delete,revert BannedGroup:read Trusted:read,write,revert,delete Known:read,write,delete,revert All:read,write"

#attachments = {
# dir and url are depricated
#    'dir': '/Library/Webserver/Documents/installhtml/wiki/data/pages',
#    'url': '/installhtml/wiki/data/pages',
#    'img_script': 'img.cgi'
#}

mail_smarthost = "localhost"
mail_from = "dont_respond@daviswiki.org"
