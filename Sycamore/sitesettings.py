# -*- coding: utf-8 -*-
"""
    Sycamore - General site settings, web interface

    @copyright: 2006-2007 by Philip Neustrom <philipn@gmail.com>
    @license: GNU GPL, see COPYING for details.
"""

# Imports
import string
import time
import re
import Cookie
from copy import copy

# import pytz from support
import sys, os.path
__directory__ = os.path.dirname(__file__)
sys.path.extend([os.path.abspath(os.path.join(__directory__, 'support'))])
import pytz

from Sycamore import config
from Sycamore import user
from Sycamore import util
from Sycamore import wikiutil
from Sycamore import wikidb
from Sycamore import wikiacl

import Sycamore.util.web as web
import Sycamore.util.mail
import Sycamore.util.datetime
from Sycamore.Page import Page
from Sycamore.widget import html
from Sycamore.wikiaction import isValidPageName
from Sycamore.wikiacl import ACL_RIGHTS_TABLE
from Sycamore.wikiutil import quoteWikiname, unquoteWikiname
from Sycamore.action import Files
from Sycamore.macro import image

_debug = 0

SANE_TEXT_UPPER_LIMIT = 1024*10

#############################################################################
### Form POST Handling
#############################################################################

def savedata_general(request):
    """
    Handle POST request of the settings form.

    Return error msg or None.  
    """
    return SiteSettingsHandler(request).handleData()

def savedata_security(request):
    """
    Handle POST request of the security settings form.

    Return error msg or None.  
    """
    return SiteSettingsSecurityHandler(request).handleData()

def savedata_usergroups(request):
    """
    Handle POST request of the user group settings form.

    Return error msg or None.  
    """
    return UserGroupsSettingsHandler(request).handleData()


def savedata_map(request):
    """
    Handle POST request of the settings form.

    Return error msg or None.  
    """
    return MapSettingsHandler(request).handleData()


class SiteSettingsHandler(object):
    def __init__(self, request):
        """
        Initialize site settings form.
        """
        self.request = request
        self._ = request.getText

    def handleData(self):
        _ = self._
        form = self.request.form
        msg = ''
    
        settings_pagename = "%s/%s" % (config.wiki_settings_page,
                                       config.wiki_settings_page_general)
        if self.request.user.may.admin(Page(settings_pagename, self.request)):
            # try to get the wiki name, if empty return an errror message
            if (form.has_key('wikiname') and
                form['wikiname'][0].replace('\t', '').strip()):
                sitename = form['wikiname'][0]
                if len(sitename) > 32:
                    return _("Your sitename must be less than 32 characters "
                             "long!")
                self.request.config.sitename = sitename
            else:
                return _("Please enter a name for your wiki!")

            if (form.has_key('catchphrase') and
                form['catchphrase'][0].replace('\t', '').strip()):
                catchphrase = form['catchphrase'][0]
                if len(catchphrase) > 100:
                    return _("Please enter a catchphrase for your wiki!")
                self.request.config.catchphrase = catchphrase
            if (form.has_key('edit_agreement_text') and
                form['edit_agreement_text'][0].replace('\t', '').strip()):
                edit_agreement_text = form['edit_agreement_text'][0] 
                if len(edit_agreement_text) > SANE_TEXT_UPPER_LIMIT:
                    return _("Too much edit agreement text...enter less!")
                self.request.config.edit_agreement_text = \
                    wikiutil.sanitize_html(edit_agreement_text)
            if (form.has_key('license_text') and
                form['license_text'][0].replace('\t', '').strip()):
                license_text = form['license_text'][0]
                if len(license_text) > SANE_TEXT_UPPER_LIMIT:
                    return _("Too much license text...enter less!")
                self.request.config.license_text = \
                    wikiutil.sanitize_html(license_text)
            if (form.has_key('tabs_nonuser') and
                form['tabs_nonuser'][0].replace('\t', '').strip()):
                tabs_nonuser_text = form['tabs_nonuser'][0]
                if len(tabs_nonuser_text) > SANE_TEXT_UPPER_LIMIT:
                    return _("Too much text in the tabs area...enter less!")
                tabs_nonuser = tabs_nonuser_text.strip().split('\n')
                fixed_tabs_nonuser = []
                for pagename in tabs_nonuser:
                  if not isValidPageName(pagename):
                    return _('"%s" is not a valid page name.  '
                             'You may only set tabs to page names..sorry!' % (
                                wikituil.escape(pagename)))
                  fixed_tabs_nonuser.append(pagename.strip())
                self.request.config.tabs_nonuser = fixed_tabs_nonuser
            if (form.has_key('tabs_user') and
                form['tabs_user'][0].replace('\t', '').strip()):
                tabs_user_text = form['tabs_user'][0]
                if len(tabs_user_text) > SANE_TEXT_UPPER_LIMIT:
                    return _("Too much text in the tabs area...enter less!")
                tabs_user = tabs_user_text.strip().split('\n')
                fixed_tabs_user = []
                for pagename in tabs_user:
                  if not isValidPageName(pagename):
                    return _('"%s" is not a valid page name.  '
                             'You may only set tabs to page names..sorry!' % (
                                pagename))
                  fixed_tabs_user.append(pagename.strip())
                self.request.config.tabs_user = fixed_tabs_user
            
            footer_buttons = []
            if (form.has_key('footer_button_1') and
                form['footer_button_1'][0].replace('\t', '').strip()):
                footer_button_1 = form['footer_button_1'][0]
                if len(footer_button_1) > SANE_TEXT_UPPER_LIMIT:
                    return _("Too much text in your footer button 1"
                             "..enter less!")
                footer_buttons.append(wikiutil.sanitize_html(footer_button_1))
            if (form.has_key('footer_button_2') and
                form['footer_button_2'][0].replace('\t', '').strip()):
                footer_button_2 = form['footer_button_2'][0]
                if len(footer_button_2) > SANE_TEXT_UPPER_LIMIT:
                    return _("Too much text in your footer button 2"
                             "..enter less!")
                footer_buttons.append(wikiutil.sanitize_html(footer_button_2))
            if (form.has_key('footer_button_3') and
                form['footer_button_3'][0].replace('\t', '').strip()):
                footer_button_3 = form['footer_button_3'][0]
                if len(footer_button_3) > SANE_TEXT_UPPER_LIMIT:
                    return _("Too much text in your footer button 3"
                             "..enter less!")
                footer_buttons.append(wikiutil.sanitize_html(footer_button_3))
            self.request.config.footer_buttons = footer_buttons
            if form.has_key('tz'):
                tz = form['tz'][0]
                if tz  in pytz.common_timezones:
                    self.request.config.tz = tz

            checkbox_fields = config.local_config_checkbox_fields
            for key, description in checkbox_fields:
                if form.has_key(key):
                    self.request.config.__dict__[key] = True
                    if key == 'is_disabled':
                        msg = ("<p>You have <strong>marked this wiki as "
                               "deleted</strong>.  The wiki will be deleted "
                               "permanently in 30 days.  If you made a "
                               "mistake, uncheck the \"delete this wiki\" "
                               "checkbox.</p>"
                               "<p>Until this wiki is permanently purged, "
                               "it will be be visible only to the admins of "
                               "this wiki.</p>")
                else:
                    self.request.config.__dict__[key] = False

            # sets the config -- becomes active as soon as this line is
            # executed!
            self.request.config.set_config(self.request.config.wiki_name,
                                           self.request.config.get_dict(),
                                           self.request)
            return _("General settings updated!") + msg

class SiteSettingsSecurityHandler(object):
    def __init__(self, request):
        """
        Initialize site settings form.
        """
        self.request = request
        self._ = request.getText

    def handleData(self):
        _ = self._
        form = self.request.form
    
        security_pagename = "%s/%s" % (config.wiki_settings_page,
            config.wiki_settings_page_security_defaults)
        if self.request.user.name in wikiacl.Group("Admin", self.request):
            grouplist = user.getGroupList(self.request)

            # intialize default rights
            default_rights = {}
            for groupname in grouplist:
                if groupname == 'Admin':
                    default_rights['Admin'] = [True, True, True, True]
                else:
                    default_rights[groupname] = [False, False, False, False]

            for key in form: 
                if key.endswith('_may_read'):
                    action = 'read'
                elif key.endswith('_may_edit'):
                    action = 'edit'
                elif key.endswith('_may_delete'):
                    action = 'delete'
                elif key.endswith('_may_admin'):
                    action = 'admin'
                else:
                    continue 

                groupname = unquoteWikiname(key[:key.find('_may_%s' % action)])
                # is valid group? 
                if groupname in grouplist:
                    default_rights[groupname][ACL_RIGHTS_TABLE[action]] = True

            for groupname in default_rights:
                default_rights[groupname] = tuple(default_rights[groupname]) 

            self.request.config.acl_rights_default = default_rights
            # sets the config -- becomes active as soon as this line is
            # executed!
            self.request.config.set_config(self.request.config.wiki_name,
                                           self.request.config.get_dict(),
                                           self.request)

            return _("Security settings updated!")

class UserGroupsSettingsHandler(object):
    def __init__(self, request):
        """
        Initialize site user groups form.
        """
        self.request = request
        self._ = request.getText

    def handleData(self):
        _ = self._
        form = self.request.form
    
        groups_pagename = "%s/%s" % (config.wiki_settings_page,
            config.wiki_settings_page_security_defaults)
        if self.request.user.name in wikiacl.Group("Admin", self.request):
            if (self.request.form.has_key('delete') and
                self.request.form['delete']):
                # delete user group
                delete_group = unquoteWikiname(self.request.form['delete'][0])
                del self.request.config.acl_rights_default[delete_group]
                # process altered configuration
                # TODO: abstract this into Groups-y class.
                self.request.config.set_config(self.request.config.wiki_name,
                                               self.request.config.get_dict(),
                                               self.request)
                return 'User group "%s" deleted.' % (
                  self.request.form['delete'][0])

            else:
                grouplist_all = user.getGroupList(self.request)
                grouplist = copy(grouplist_all)

                # remove immutable groups
                grouplist.remove("All")
                grouplist.remove("Known")

                new_group_name = None
                new_group_dict = None
                for key in form: 
                    if key.startswith('group_'):
                        groupname = unquoteWikiname(key[len('group_'):])
                        if len(groupname) > 100:
                            return _("Group names must be less than 100 "
                                     "characters.")
                        if groupname not in grouplist:
                            continue  # throw out invalid group names
                        # keep track of empty textarea responses
                        grouplist.remove(groupname) 
                        memberlist = [member.strip() for member in
                            form[key][0].split('\n')]
                        newmemberlist = []
                        for member in memberlist:
                            if len(member) > 100:
                                return _("User names must be less than 100 "
                                         "characters.")
                            if member:
                                newmemberlist.append(member)
                        memberlist = newmemberlist
                        # initialize the group dictionary
                        group_dict = {}
                        for membername in memberlist:
                            group_dict[membername.lower()] = None

                        group = wikiacl.Group(groupname, self.request,
                                              fresh=True) 
                        group.update(group_dict)
                        group.save()
                    elif key == 'ips_banned':
                        ips_banned = {}
                        for ip in form['ips_banned'][0].split('\n'):
                            ip = ip.strip()
                            if not web.isIpAddress(ip):
                                return _('Invalid IP address "%s" entered.' % (
                                    ip))
                            ips_banned[ip] = None

                        group = wikiacl.Group("Banned", self.request,
                                              fresh=True)
                        group.update_ips(ips_banned)
                        group.save()
                    elif key == 'new_group_name':
                        new_group_name = form['new_group_name'][0].strip()
                        if len(new_group_name) > 100:
                            return _("Group names must be less than 100 "
                                     "characters.")
                        elif new_group_name in grouplist_all:
                            return _("Group %s already exists." % (
                                new_group_name))
                    elif key == 'new_group_users':
                        new_group_users = [member.strip() for member in
                            form['new_group_users'][0].split('\n')]
                        new_group_users_copy = []
                        for member in new_group_users:
                            if len(member) > 100:
                                return _("User names must be less than 100 "
                                         "characters.")
                            if member:
                                new_group_users_copy.append(member)
                        new_group_users = new_group_users_copy
                        # initialize the group dictionary
                        new_group_dict = {}
                        for membername in new_group_users:
                            new_group_dict[membername.lower()] = None

                for emptygroupname in grouplist:
                    group = wikiacl.Group(emptygroupname, self.request)
                    group.update({})
                    group.save()

                if new_group_name:
                    new_group = wikiacl.Group(new_group_name, self.request)
                    if new_group_dict:
                        new_group.update(new_group_dict)
                    new_group.save()

                return _("User groups updated!")
                

class MapSettingsHandler(object):
    def __init__(self, request):
        """
        Initialize site settings form.
        """
        self.request = request
        self._ = request.getText

    def handleData(self):
        _ = self._
        form = self.request.form
        msg = ''
    
        settings_pagename = "%s/%s" % (config.wiki_settings_page,
                                       config.wiki_settings_page_general)
        if self.request.user.may.admin(Page(settings_pagename, self.request)):
            # try to get the wiki name, if empty return an errror message

            if (form.has_key('latitude') and
                form['latitude'][0].replace('\t', '').strip()):
                latitude = form['latitude'][0]
                if latitude == '':
                    self.request.config.latitude = latitude
                try:
                    float(latitude)
                except ValueError:
                    return _("Please enter a valid latitude")
                self.request.config.latitude = float(latitude)
            if (form.has_key('longitude') and
                form['longitude'][0].replace('\t', '').strip()):
                longitude = form['longitude'][0]
                if longitude == '':
                    self.request.config.longitude = longitude
                try:
                    float(longitude)
                except ValueError:
                    return _("Please enter a valid longitude")
                self.request.config.longitude = float(longitude)

            if form.has_key('address_locale'):
                address_locale = form['address_locale'][0]
                if len(address_locale) > 40:
                    return _("Too much text in your address locale"
                             "..enter less!")
                address_locale = address_locale
                self.request.config.address_locale = address_locale
            else:
                self.request.config.address_locale = ''

	    if form.has_key('gmaps_api_key'):
		gmaps_key = form['gmaps_api_key'][0]
                if len(gmaps_key) > 9000:
		    #go super saiyan
                    return _("Your API key power level is too high.")
                self.request.config.gmaps_api_key = gmaps_key

            #process tags line by line
            i = 0
            while i < 19:
                if (form.has_key('marker%s' % i) and
                    form.has_key('marker_display_%s' % i) and
                    form.has_key('marker_tag_%s' % i) ):
                    try:
                        marker_position = int(form['marker%s' % i][0])
                    except ValueError:
                        return _("Way to hack the form, asstard")
                    marker_display = form['marker_display_%s' % i][0]
                    marker_tag = form['marker_tag_%s' % i][0]
                    if len(marker_display) > 40:
                        return _("Too much text in marker display %s." % i)
                    if len(marker_tag) > 40:
                        return _("Too much text in marker tag %s." % i)
                    self.request.config.map_names[i] = marker_display.strip()
                    self.request.config.map_tags[i] = marker_tag.strip()
                    self.request.config.map_markers[i] = marker_position
                i = i + 1
            if (form.has_key('marker%s' % i) and
                form.has_key('marker_display_%s' % i) ):
                try:
                    marker_position = int(form['marker%s' % i][0])
                except ValueError:
                    return _("Way to hack the form, asstard")
                marker_display = form['marker_display_%s' % i][0]
                if len(marker_display) > 40:
                    return _("Too much text in marker display %s." % i)
                # self.request.config.map_names.append(marker_display.strip())
                self.request.config.map_names[i] = marker_display.strip()
                self.request.config.map_markers[i] = marker_position


            if (form.has_key('edit_agreement_text') and
                form['edit_agreement_text'][0].replace('\t', '').strip()):
                edit_agreement_text = form['edit_agreement_text'][0] 
                if len(edit_agreement_text) > SANE_TEXT_UPPER_LIMIT:
                    return _("Too much edit agreement text...enter less!")
                self.request.config.edit_agreement_text = \
                    wikiutil.sanitize_html(edit_agreement_text)

            # sets the config -- becomes active as soon as this line is
            # executed!
            self.request.config.set_config(self.request.config.wiki_name,
                                           self.request.config.get_dict(),
                                           self.request)
            return _("Map settings updated!") + msg


#############################################################################
### Form Generation
#############################################################################

class GeneralSettings:
    """
    Site settings management.
    """
    def __init__(self, request):
        """
        Initialize site settings form.
        """
        self.request = request
        self._ = request.getText

    def _tz_select(self):
        """
        create time zone selection.
        """
        tz  = self.request.config.tz

        options = []
        for timezone in pytz.common_timezones:
            options.append((timezone, timezone))

        return util.web.makeSelection('tz', options, tz)
  
    def _theme_select(self):
        """
        Create theme selection.
        """
        cur_theme = self.request.config.theme_default
        options = []
        for theme in wikiutil.getPlugins('theme'):
            options.append((theme, theme))
                
        return util.web.makeSelection('theme_name', options, cur_theme)
  
    def make_form(self):
        """
        Create the FORM, and the DIVs with the input fields
        """
        self._form = html.FORM(action=(self.request.getScriptname() + 
            self.request.getPathinfo()))
        self._inner = html.DIV(html_class="settings_form")

        # Use the user interface language and direction
        lang_attr = self.request.theme.ui_lang_attr()
        self._form.append(html.Raw("<div %s>" % lang_attr))

        self._form.append(html.INPUT(type="hidden", name="action",
                                     value="generalsettings"))
        self._form.append(self._inner)
        self._form.append(html.Raw("</div>"))

    def make_row(self, label, cell, option_text=None, **kw):
        """
        Create a row in the form.
        """
        if not option_text:
          self._inner.append(html.DIV(html_class="settings_form_item").extend([
              html.DIV(html_class="settings_form_label", **kw).extend([label]),
              html.DIV().extend(cell),
          ]))
        else:
          option_label = html.SPAN(html_class="optional", **kw).extend([
            option_text])
          settings_label = html.DIV(html_class="settings_form_label",
                                    **kw).extend([label, option_label])
          self._inner.append(html.DIV(html_class="settings_form_item").extend([
              settings_label,
              html.DIV().extend(cell),
          ]))


    def asHTML(self):
        """
        Create the complete HTML form code.
        """
        _ = self._
        self.make_form()

        # different form elements depending on login state
        html_uid = ''
        html_sendmail = ''
        settings_pagename = "%s/%s" % (config.wiki_settings_page,
                                       config.wiki_settings_page_general)
        if self.request.user.may.admin(Page(settings_pagename, self.request)):
            # start generalSettings div
            self._inner.append(html.Raw('<div class="generalSettings">')) 
            self.make_row(_("Name of wiki"), [
              html.INPUT(type="text", size="32", maxlength="32",
                         name="wikiname", value=self.request.config.sitename)
            ])

            self.make_row(_("Tabs, not logged in"), [
              html.TEXTAREA(name="tabs_nonuser", id="tabs_nonuser_textarea",
                            rows="6", cols="40").append(
                                '\n'.join(map(wikiutil.escape,
                                    self.request.config.tabs_nonuser)))
            ], option_text=_("(one per line)"))

            self.make_row(_("Tabs, logged in"), [
              html.TEXTAREA(name="tabs_user", id="tabs_user_textarea",
                            rows="6", cols="40").append(
                                '\n'.join(map(wikiutil.escape,
                                    self.request.config.tabs_user)))
            ], option_text=_("(one per line)"))


            self.make_row(_("Catchphrase"), [
              html.INPUT(type="text", size="32", maxlength="100",
                name="catchphrase", value=self.request.config.catchphrase)
            ])

            self.make_row(_("License text"), [
              html.TEXTAREA(name="license_text", id="license_text_textarea",
                rows="10", cols="60").append(self.request.config.license_text)
            ], option_text=_("(HTML ok)"))

            self.make_row(_("Edit agreement text"), [
              html.TEXTAREA(name="edit_agreement_text",
                id="edit_agreement_textarea", rows="10", cols="60").append(
                    self.request.config.edit_agreement_text)
            ], option_text=_("(HTML ok)"))

            footer_buttons = self.request.config.footer_buttons
            footer_button_1 = ''
            footer_button_2 = ''
            footer_button_3 = ''
            if len(footer_buttons) > 0:
                footer_button_1 = footer_buttons[0]
                if len(footer_buttons) > 1:
                    footer_button_2 = footer_buttons[1]
                    if len(footer_buttons) > 2:
                        footer_button_3 = footer_buttons[2]

            self.make_row(_("Footer button 1"), [
              html.TEXTAREA(name="footer_button_1", rows="5",
                            cols="60").append(footer_button_1)
            ], option_text=_("(HTML ok)"))

            self.make_row(_("Footer button 2"), [
              html.TEXTAREA(name="footer_button_2", rows="5",
                            cols="60").append(footer_button_2)
            ], option_text=_("(HTML ok)"))

            self.make_row(_("Footer button 3"), [
              html.TEXTAREA(name="footer_button_3", rows="5",
                            cols="60").append(footer_button_3)
            ], option_text=_("(HTML ok)"))

            self.make_row(_("Default time zone"), [self._tz_select()])

            bool_options = []
            checkbox_fields = config.local_config_checkbox_fields
            for key, label in checkbox_fields:
                bool_options.extend([ html.INPUT(type="checkbox", name=key,
                        value=1, checked=getattr(self.request.config, key, 0)
                    ),
                    ' ', label(_), html.BR(), ])
            self.make_row(_('General options'), bool_options)

            self._inner.append(html.Raw("</div>")) # close generalSettings div

            buttons = [
                ('save', _('Save Settings')),
            ]

            # Add buttons
            button_cell = []
            for name, label in buttons:
                button_cell.extend([
                    html.INPUT(type="submit", name=name, value=label),
                    ' ',
                ])
            self.make_row('', button_cell)

        return str(self._form)

class SecuritySettings(object):
    """
    security settings defaults management.
    """
    def __init__(self, request):
        """
        Initialize security settings form.
        """
        self.request = request
        self._ = request.getText

    def make_form(self):
        """
        Create the FORM, and the DIVs with the input fields
        """
        self._form = html.FORM(action=self.request.getScriptname() +
            self.request.getPathinfo())
        self._inner = html.DIV(html_class="settings_form")

        # Use the user interface language and direction
        lang_attr = self.request.theme.ui_lang_attr()
        self._form.append(html.Raw("<div %s>" % lang_attr))

        self._form.append(html.INPUT(type="hidden", name="action",
                                     value="securitysettings"))
        self._form.append(self._inner)
        self._form.append(html.Raw("</div>"))

    def make_row(self, label, cell, **kw):
        """
        Create a row in the form.
        """
        self._inner.append(html.DIV(html_class="settings_form_item").extend([
            html.DIV(html_class="settings_form_label", **kw).extend([label]),
            html.DIV().extend(cell),
        ]))

    def asHTML(self):
        """
        Create the complete HTML form code.
        """
        _ = self._
        self.make_form()

        # different form elements depending on login state
        html_uid = ''
        html_sendmail = ''
        security_pagename = "%s/%s" % (config.wiki_settings_page,
            config.wiki_settings_page_security_defaults)
        if not self.request.user.name in wikiacl.Group("Admin", self.request):
            return ''
        else:
            self._inner.append(html.Raw('<div class="securitySettings">'))
            self.make_row(_("Everybody may:"), [
                html.INPUT(type="checkbox", name="All_may_read", value=1,
                    checked=self.request.config.acl_rights_default['All'][
                        ACL_RIGHTS_TABLE['read']]),
                'read', 
                html.INPUT(type="checkbox", name="All_may_edit", value=1,
                    checked=self.request.config.acl_rights_default['All'][
                        ACL_RIGHTS_TABLE['edit']]),
                'edit',
                html.INPUT(type="checkbox", name="All_may_delete", value=1,
                    checked=self.request.config.acl_rights_default['All'][
                        ACL_RIGHTS_TABLE['delete']]),
                'delete',
            ])

            self.make_row(_("Logged in people may:"), [
                html.INPUT(type="checkbox", name="Known_may_read", value=1,
                    checked=self.request.config.acl_rights_default['Known'][
                        ACL_RIGHTS_TABLE['read']]),
                'read', 
                html.INPUT(type="checkbox", name="Known_may_edit", value=1,
                    checked=self.request.config.acl_rights_default['Known'][
                        ACL_RIGHTS_TABLE['edit']]),
                'edit',
                html.INPUT(type="checkbox", name="Known_may_delete", value=1,
                    checked=self.request.config.acl_rights_default['Known'][
                        ACL_RIGHTS_TABLE['delete']]),
                'delete',
            ])

            self.make_row(_("Banned people may:"), [
                html.INPUT(type="checkbox", name="Banned_may_read", value=1,
                    checked=self.request.config.acl_rights_default['Banned'][
                        ACL_RIGHTS_TABLE['read']]),
                'read', 
                html.INPUT(type="checkbox", name="Banned_may_edit", value=1,
                    checked=self.request.config.acl_rights_default['Banned'][
                        ACL_RIGHTS_TABLE['edit']]),
                'edit',
                html.INPUT(type="checkbox", name="Banned_may_delete", value=1,
                    checked=self.request.config.acl_rights_default['Banned'][
                        ACL_RIGHTS_TABLE['delete']]),
                'delete',
            ])

            custom_groups = user.getGroupList(self.request,
                exclude_special_groups=True)
            for groupname in custom_groups:
                group = wikiacl.Group(groupname, self.request, fresh=True)
                self.make_row(_("People in the %s group may:" % (
                    wikiutil.escape(groupname))), [
                    html.INPUT(type="checkbox",
                        name="%s_may_read" % quoteWikiname(groupname),
                        value=1, checked=group.default_rights()[
                            ACL_RIGHTS_TABLE['read']]),
                    'read', 
                    html.INPUT(type="checkbox",
                        name="%s_may_edit" % quoteWikiname(groupname),
                        value=1, checked=group.default_rights()[
                            ACL_RIGHTS_TABLE['edit']]),
                    'edit',
                    html.INPUT(type="checkbox",
                        name="%s_may_delete" % quoteWikiname(groupname),
                        value=1, checked=group.default_rights()[
                            ACL_RIGHTS_TABLE['delete']]),
                    'delete',
                    html.INPUT(type="checkbox",
                        name="%s_may_admin" % quoteWikiname(groupname),
                        value=1, checked=group.default_rights()[
                            ACL_RIGHTS_TABLE['admin']]),
                    'change security' 
                ])
            
            self._inner.append(html.Raw("</div>")) # close securitySettings div
            buttons = [
                ('save', _('Save Settings')),
            ]

        # Add buttons
        button_cell = []
        for name, label in buttons:
            button_cell.extend([
                html.INPUT(type="submit", name=name, value=label),
                ' ',
            ])
        self.make_row('', button_cell)

        return str(self._form)

class UserGroupSettings(object):
    """
    User group management.
    """
    def __init__(self, request):
        """
        Initialize user groups form.
        """
        self.request = request
        self._ = request.getText

    def make_form(self):
        """
        Create the FORM, and the DIVs with the input fields
        """
        self._form = html.FORM(action=self.request.getScriptname() +
            self.request.getPathinfo())
        self._inner = html.DIV(html_class="settings_form")

        # Use the user interface language and direction
        lang_attr = self.request.theme.ui_lang_attr()
        self._form.append(html.Raw("<div %s>" % lang_attr))

        self._form.append(html.INPUT(type="hidden", name="action",
                                     value="usergroupsettings"))
        self._form.append(self._inner)
        self._form.append(html.Raw("</div>"))

    def make_row(self, label, cell, option_text=None, **kw):
        """
        Create a row in the form.
        """
        if not option_text:
            self._inner.append(html.DIV(
                html_class="settings_form_item").extend([
                    html.DIV(html_class="settings_form_label", **kw).extend(
                        [label]),
                    html.DIV().extend(cell),
                ]))
        else:
            option_label = html.SPAN(
                html_class="optional", **kw).extend([option_text])
            settings_label = html.DIV(
                html_class="settings_form_label", **kw).extend(
                    [html.Raw(label), option_label])
            self._inner.append(html.DIV(
                html_class="settings_form_item").extend([
                    settings_label,
                    html.DIV().extend(cell),
                ]))

    def asHTML(self):
        """
        Create the complete HTML form code.
        """
        _ = self._
        self.make_form()

        # different form elements depending on login state
        html_uid = ''
        html_sendmail = ''
        groups_pagename = "%s/%s" % (config.wiki_settings_page,
            config.wiki_settings_page_security_defaults)
        if self.request.user.name in wikiacl.Group("Admin", self.request):
            group_admin = wikiacl.Group("Admin", self.request, fresh=True)
            self.make_row(_("Admins"), [
                html.TEXTAREA(name="group_Admin", rows="6", cols="40",
                              id="group_Admin").append(
                                '\n'.join(map(wikiutil.escape,
                                    group_admin.users(proper_names=True))))
                ],
                option_text=_("(one per line)"))


            group_banned = wikiacl.Group("Banned", self.request, fresh=True)
            self.make_row(_("Banned Users"), [
                html.TEXTAREA(name="group_Banned", rows="6", cols="40",
                              id="group_Banned").append(
                                '\n'.join(map(wikiutil.escape,
                                    group_banned.users(proper_names=True))))
                ],
                option_text=_("(one per line)"))

            self.make_row(_("Banned IP Addresses"), [
                html.TEXTAREA(name="ips_banned", rows="6", cols="40",
                              id="ips_banned").append(
                                '\n'.join(map(wikiutil.escape,
                                    group_banned.get_ips().keys())))
                ],
                option_text=_("(one per line)"))

            custom_groups = user.getGroupList(self.request,
                exclude_special_groups=True)
            for groupname in custom_groups:
                group = wikiacl.Group(groupname, self.request, fresh=True)
                delete_label = ('<span class="minorActionBox">[<a href="%s/'
                                '%s?action=usergroupsettings&delete=%s">'
                                'delete group</a>]</span>') % (
                                    self.request.getScriptname(),
                                    quoteWikiname(groups_pagename),
                                    quoteWikiname(groupname))
                self.make_row('%s %s' % (wikiutil.escape(groupname),
                                         delete_label),
                              [
                                  html.TEXTAREA(
                                    name="group_%s" % quoteWikiname(groupname),
                                    rows="6", cols="40",
                                    id="group_%s" % quoteWikiname(groupname)
                                  ).append('\n'.join(map(wikiutil.escape,
                                    group.users(proper_names=True))))
                              ], option_text=_("(one per line)"))

            buttons = [
                ('save', _('Save Groups')),
            ]

            # Add buttons
            button_cell = []
            for name, label in buttons:
                button_cell.extend([
                    html.INPUT(type="submit", name=name, value=label),
                    ' ',
                ])
            self.make_row('', button_cell)

            self._inner.append(html.H2().append("Create a new group"))

            self.make_row(_("Group name"), [
              html.INPUT(type="text", size="40", name="new_group_name"),
            ])

            self.make_row('Group users', [
              html.TEXTAREA(name="new_group_users", rows="6", cols="40")
            ])

            buttons = [
                ('save', _('Add new group')),
            ]

            # Add buttons
            button_cell = []
            for name, label in buttons:
                button_cell.extend([
                    html.INPUT(type="submit", name=name, value=label),
                    ' ',
                ])
            self.make_row('', button_cell)


        return str(self._form)

class MapSettings:
    """
    Site settings management.
    """
    def __init__(self, request):
        """
        Initialize site settings form.
        """
        self.request = request
        self._ = request.getText

    def _tz_select(self):
        """
        create time zone selection.
        """
        tz  = self.request.config.tz

        options = []
        for timezone in pytz.common_timezones:
            options.append((timezone, timezone))

        return util.web.makeSelection('tz', options, tz)
  
    def _theme_select(self):
        """
        Create theme selection.
        """
        cur_theme = self.request.config.theme_default
        options = []
        for theme in wikiutil.getPlugins('theme'):
            options.append((theme, theme))
                
        return util.web.makeSelection('theme_name', options, cur_theme)
  
    def make_form(self):
        """
        Create the FORM, and the DIVs with the input fields
        """
        self._form = html.FORM(action=(self.request.getScriptname() + 
            self.request.getPathinfo()))
        self._inner = html.DIV(html_class="settings_form")

        # Use the user interface language and direction
        lang_attr = self.request.theme.ui_lang_attr()
        self._form.append(html.Raw("<div %s>" % lang_attr))

        self._form.append(html.INPUT(type="hidden", name="action",
                                     value="mapsettings"))
        self._form.append(self._inner)
        self._form.append(html.Raw("</div>"))

    def make_row(self, label, cell, option_text=None, **kw):
        """
        Create a row in the form.
        """
        if not option_text:
          self._inner.append(html.DIV(html_class="settings_form_item").extend([
              html.DIV(html_class="settings_form_label", **kw).extend([label]),
              html.DIV().extend(cell),
          ]))
        else:
          option_label = html.SPAN(html_class="optional", **kw).extend([
            option_text])
          settings_label = html.DIV(html_class="settings_form_label",
                                    **kw).extend([label, option_label])
          self._inner.append(html.DIV(html_class="settings_form_item").extend([
              settings_label,
              html.DIV().extend(cell),
          ]))

    def marker_url(self, markername):
        """
        Gets the correct URL for markers stored on your local wiki_settings/map page
        """
        return Files.getAttachUrl("%s/%s" % (config.wiki_settings_page,
                          config.wiki_settings_page_map), markername, self.request)


    def asHTML(self):
        """
        Create the complete HTML form code.
        """
        _ = self._
        self.make_form()

        # different form elements depending on login state
        html_uid = ''
        html_sendmail = ''
        settings_pagename = "%s/%s" % (config.wiki_settings_page,
                                       config.wiki_settings_page_general)
        if self.request.user.may.admin(Page(settings_pagename, self.request)):
            # start mapSettings div
            self._inner.append(html.Raw('<div class="mapSettings">')) 

            self.make_row(_("Map starting latitude"), [
              html.INPUT(type="text", size="32", maxlength="100",
                name="latitude", value=self.request.config.latitude)
            ], option_text=_("(South values negative)"))

            self.make_row(_("Map starting longitude"), [
              html.INPUT(type="text", size="32", maxlength="100",
                name="longitude", value=self.request.config.longitude)
            ], option_text=_("(East values negative)"))

            self.make_row(_("Google Maps API Key"), [
              html.INPUT(type="text", size="60", maxlength="255",
                name="gmaps_api_key", value=self.request.config.gmaps_api_key)
            ], option_text=_("(East values negative)"))

            # the config.address_locale already exists
            #TODO: remove from general settings
            self.make_row(_("Default address locale"), 
              [html.INPUT(type="text", size="32", maxlength="40",
                          name="address_locale",
                          value=self.request.config.address_locale)],
              option_text=_('(e.g. "Davis, California".  This is optional.)'))


            # Setup the map markers preferences.
            marker_corners = ["Upper Left", "Upper Center", "Upper Right", 
                              "Center Left", "Centered", "Center Right",
                              "Lower Left", "Lower Center", "Lower Right" ]
            i = 0
            marker_table = html.TABLE(html_class="map_marker_table").append( \
               html.TR().append(html.Raw('<td align="center"><b>Point Corner</b></td><td align="center"><b>Image</b></td>' +
                                '<td align="center"><b>Overview Map Label</b></td><td align="center"><b>Tag</b></td>')))

            while i < 20:
                marker_row = html.TR()

                # Build the menu for selection of where the marker actually points
                marker_select = [False, False, False, False, False, False, False, False, False]
                marker_select[self.request.config.map_markers[i]] = True
                marker_location_menu = html.SELECT(name="marker%s" % i)
                j = 0
                while j < 9:            #allow nine locations (3x3 grid)
                     marker_location_menu.append(html.OPTION(value=j,
                                  selected=marker_select[j]).append(marker_corners[j]))
                     j = j + 1


                # actually get around to making a table row now
                if i < 19:
                    marker_row.extend([ html.TD().append(marker_location_menu),
                          # html.TD().append(html.IMG(src=self.marker_url("marker%s.png" % i, html_class="borderless")),
                          # html.TD().append(html.IMG(src=self.marker_url("marker.png"), html_class="borderless")), 
                          html.TD().append(html.IMG(src=self.marker_url("marker%s.png" % i), html_class="borderless")), 
                          html.TD().append(html.INPUT(type="text", size="32", maxlength="40",
                             name="marker_display_%s" % i,
                             value=self.request.config.map_names[i])) , 
                          html.TD().append(html.INPUT(type="text", size="32", maxlength="40",
                             name="marker_tag_%s" % i,
                             #value=self.request.config.map_markers[i]))
                             value=self.request.config.map_tags[i]))
                     ] )


                # Make the "Other" row
                else:
                    marker_row.extend([ html.TD().append(marker_location_menu), \
                          # html.TD().append(html.IMG(src=self.marker_url("marker%s.png" % i, html_class="borderless"))),
                          # TODO: find out why the hell this doesn't work
                          # html.TD().append( image.execute(macro=self, args="marker.png", formatter=self.request.formatter)), 
                          # html.TD().append(html.IMG(src=self.marker_url("marker.png"), html_class="borderless")),
                          html.TD().append(html.IMG(src=self.marker_url("marker%s.png" % i), html_class="borderless")),
                          html.TD().append(html.INPUT(type="text", size="32", maxlength="40",
                             name="marker_display_%s" % i,
                             value=self.request.config.map_names[i])) , 
                          html.TD().append(html.Raw("<i>&lt;all other values&gt;</i>"))
                    ] )

                marker_table.append( marker_row )
                i = i + 1

            self.make_row(_("Marker Settings"), [ marker_table ] )

            bool_options = []
            checkbox_fields = config.local_config_checkbox_fields
            for key, label in checkbox_fields:
                bool_options.extend([ html.INPUT(type="checkbox", name=key,
                        value=1, checked=getattr(self.request.config, key, 0)
                    ),
                    ' ', label(_), html.BR(), ])
            bool_options.extend([ html.INPUT(type="checkbox", name="killjedi",
                        value="order66"), "Execute Order 66", html.BR(), ] )
            self.make_row(_('General options'), bool_options)

            self._inner.append(html.Raw("</div>")) # close generalSettings div

            buttons = [
                ('save', _('Save Settings')),
            ]

            # Add buttons
            button_cell = []
            for name, label in buttons:
                button_cell.extend([
                    html.INPUT(type="submit", name=name, value=label),
                    ' ',
                ])
            self.make_row('', button_cell)

        else:

            marker_table = html.TABLE( html_class='mapmarker')
            marker_table.append(html.TR().extend( [
              html.TD() ,
              html.TD().append(html.B().append("Category")),
              html.TD().append(html.B().append("Tag*")) ]) )
            i = 0
            while i < 19:
              if self.request.config.map_names[i]:
                marker_table.append(html.TR().extend( [
                   html.TD().append(html.IMG(src=self.marker_url("marker%s.png" %i), html_class="borderless")),
                   html.TD().append(self.request.config.map_names[i]),
                   html.TD().append(self.request.config.map_tags[i]) ]) )
              i = i + 1
            marker_table.append( html.TR().extend( [
                   html.TD().append(html.IMG(src=self.marker_url("marker%s.png" %i), html_class="borderless")),
                   html.TD().append(self.request.config.map_names[i]),
                   html.TD().append(html.Raw("<i>&lt;all other values&gt;</i>")) ]) )
            self._form = marker_table
            self._form.append("Tags are what you use in the address macro to categorize it on the map.")
            # self._form = "<b>You're not logged in, lol.</b>"
        return str(self._form)



def getGeneralForm(request):
    """
    Return HTML code for the site settings.
    """
    return GeneralSettings(request).asHTML()

def getSecurityForm(request):
    """
    Return HTML code for the site settings.
    """
    return SecuritySettings(request).asHTML()

def getUserGroupForm(request):
    """
    Return HTML code for the site settings.
    """
    return UserGroupSettings(request).asHTML()

def getMapForm(request):
    """
    Return HTML code for site settings relating to maps.
    """
    return MapSettings(request).asHTML()


