# -*- coding: utf-8 -*-
"""
    Sycamore - HTML Widgets

    @copyright: 2003 by J�rgen Hermann <jh@web.de>
    @license: GNU GPL, see COPYING for details.
"""

# Imports
from Sycamore import wikiutil
from Sycamore import config

from Sycamore.widget.base import Widget

# sort attributes or not? (set to 1 by unit tests)
_SORT_ATTRS = 0

#############################################################################
### Base Classes
#############################################################################

class Text:
    """
    A text node which will be escaped.
    """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return wikiutil.escape(self.text)
        
class Raw:
    """
    Raw HTML code.
    """
    def __init__(self, markup):
        self.markup = markup

    def __str__(self):
        return self.markup
        
class Element:
    """
    Abstract base class for HTML elements.
    """
    _ATTRS = {
    }
    _DEFAULT_ATTRS = {
    }
    _BOOL_ATTRS = {
        'checked': None,
        'compact': None,
        'defer': None,
        'disabled': None,
        'ismap': None,
        'multiple': None,
        'nohref': None,
        'noshade': None,
        'nowrap': None,
        'readonly': None,
        'selected': None,
    }

    def __init__(self, **kw):
        for key in kw.keys():
            if key == 'html_class':
                key = 'class'
            key = key.lower()
            if not self._ATTRS.has_key(key):
                raise AttributeError(
                    "Invalid HTML attribute %r for tag <%s>" % (
                        key, self.tagname()))

        self.attrs = self._DEFAULT_ATTRS.copy()
        self.attrs.update(kw)
        if self.attrs.has_key('html_class'):  # class=".." is illegal python
            self.attrs['class'] = self.attrs['html_class']
            del self.attrs['html_class']

    def tagname(self):
        return self.__class__.__name__.lower()

    def _openingtag(self):
        result = [self.tagname()]
        attrs = self.attrs.items()
        if _SORT_ATTRS:
            attrs.sort()
        for key, val in attrs:
            key = key.lower()
            if type(val) == unicode:
                val = val.encode(config.charset)
            if self._BOOL_ATTRS.has_key(key):
                if val: result.append(key)
            else:
                result.append('%s="%s"' % (key, wikiutil.escape(str(val), 1)))
        return ' '.join(result)

    def __str__(self):
        raise NotImplementedError 

        
class EmptyElement(Element):
    """
    HTML elements with an empty content model.
    """
    def __str__(self):
        return "<%s>" % self._openingtag()

class CompositeElement(Element):
    """
    HTML elements with content.
    """
    def __init__(self, **kw):
        Element.__init__(self, **kw)
        self.children = []

    def append(self, child):
        if isinstance(child, type('')):
            child = wikiutil.escape(child)
        self.children.append(child)
        return self

    def extend(self, children):
        for child in children:
            self.append(child)
        return self

    def __str__(self):
        def _to_string(c):
            if type(c) == unicode:
                return c.encode(config.charset)
            return str(c)
        return "<%s>%s</%s>" % (
            self._openingtag(),
            ''.join([_to_string(c) for c in self.children]),
            self.tagname(),
        )


#############################################################################
### HTML Elements
#############################################################################


class A(CompositeElement):
    "anchor"
    _ATTRS = {
        'accesskey': None,
        'charset': None,
        'class': None,
        'coords': None,
        'href': None,
        'hreflang': None,
        'name': None,
        'onblur': None,
        'onfocus': None,
        'rel': None,
        'rev': None,
        'shape': None,
        'tabindex': None,
        'type': None,
    }

class ABBR(CompositeElement):
    "abbreviated form (e.g., WWW, HTTP, etc.)"
    _ATTRS = {
        'class': None,
    }

class ACRONYM(CompositeElement):
    "acronyms"
    _ATTRS = {
        'class': None,
    }

class ADDRESS(CompositeElement):
    "information on author"
    _ATTRS = {
        'class': None,
    }

class AREA(EmptyElement):
    "client-side image map area"
    _ATTRS = {
        'alt': None,
        'class': None,
        'href': None,
        'shape': None,
    }

class B(CompositeElement):
    "bold text style"
    _ATTRS = {
        'class': None,
    }

class BASE(EmptyElement):
    "document base URI"
    _ATTRS = {
    }

class BDO(CompositeElement):
    "I18N BiDi over-ride"
    _ATTRS = {
        'class': None,
    }

class BIG(CompositeElement):
    "large text style"
    _ATTRS = {
        'class': None,
    }

class BLOCKQUOTE(CompositeElement):
    "long quotation"
    _ATTRS = {
        'class': None,
    }

class BODY(CompositeElement):
    "document body"
    _ATTRS = {
        'alink': None,
        'background': None,
        'bgcolor': None,
        'class': None,
        'link': None,
        'onload': None,
        'onunload': None,
        'text': None,
        'vlink': None,
    }

class BR(EmptyElement):
    "forced line break"
    _ATTRS = {
        'class': None,
    }

class BUTTON(CompositeElement):
    "push button"
    _ATTRS = {
        'class': None,
    }

class CAPTION(CompositeElement):
    "table caption"
    _ATTRS = {
        'class': None,
    }

class CITE(CompositeElement):
    "citation"
    _ATTRS = {
        'class': None,
    }

class CODE(CompositeElement):
    "computer code fragment"
    _ATTRS = {
        'class': None,
    }

class DD(CompositeElement):
    "definition description"
    _ATTRS = {
        'class': None,
    }

class DEL(CompositeElement):
    "deleted text"
    _ATTRS = {
        'class': None,
    }

class DFN(CompositeElement):
    "instance definition"
    _ATTRS = {
        'class': None,
    }

class DIV(CompositeElement):
    "generic language/style container"
    _ATTRS = {
        'class': None,
    }

class DL(CompositeElement):
    "definition list"
    _ATTRS = {
        'class': None,
    }

class DT(CompositeElement):
    "definition term"
    _ATTRS = {
        'class': None,
    }

class EM(CompositeElement):
    "emphasis"
    _ATTRS = {
        'class': None,
    }

class FORM(CompositeElement):
    "interactive form"
    _ATTRS = {
        'accept': None,
        'action': None,
        'charset': None,
        'class': None,
        'enctype': None,
        'method': None,
        'name': None,
        'onreset': None,
        'onsubmit': None,
        'target': None,
    }
    _DEFAULT_ATTRS = {
        'method': 'POST',
    }

class H1(CompositeElement):
    "heading"
    _ATTRS = {
        'class': None,
    }

class H2(CompositeElement):
    "heading"
    _ATTRS = {
        'class': None,
    }

class H3(CompositeElement):
    "heading"
    _ATTRS = {
        'class': None,
    }

class H4(CompositeElement):
    "heading"
    _ATTRS = {
        'class': None,
    }

class H5(CompositeElement):
    "heading"
    _ATTRS = {
        'class': None,
    }

class H6(CompositeElement):
    "heading"
    _ATTRS = {
        'class': None,
    }

class HEAD(CompositeElement):
    "document head"
    _ATTRS = {
    }

class HR(EmptyElement):
    "horizontal rule"
    _ATTRS = {
        'class': None,
    }

class HTML(CompositeElement):
    "document root element"
    _ATTRS = {
        'version': None,
    }

class I(CompositeElement):
    "italic text style"
    _ATTRS = {
        'class': None,
    }

class IFRAME(CompositeElement):
    "inline subwindow"
    _ATTRS = {
        'class': None,
    }

class IMG(EmptyElement):
    "embedded image"
    _ATTRS = {
        'align': None,
        'alt': None,
        'border': None,
        'class': None,
        'vspace': None,
    }

class INPUT(EmptyElement):
    "form control"
    _ATTRS = {
        'accesskey': None,
        'align': None,
        'alt': None,
        'accept': None,
        'checked': None,
        'class': None,
        'disabled': None,
        'ismap': None,
        'maxlength': None,
        'name': None,
        'onblur': None,
        'onchange': None,
        'onfocus': None,
        'onselect': None,
        'readonly': None,
        'size': None,
        'src': None,
        'tabindex': None,
        'type': None,
        'usemap': None,
        'value': None,
    }

class INS(CompositeElement):
    "inserted text"
    _ATTRS = {
        'class': None,
    }

class KBD(CompositeElement):
    "text to be entered by the user"
    _ATTRS = {
        'class': None,
    }

class LABEL(CompositeElement):
    "form field label text"
    _ATTRS = {
        'class': None,
    }

class LI(CompositeElement):
    "list item"
    _ATTRS = {
        'class': None,
    }

class LINK(EmptyElement):
    "a media-independent link"
    _ATTRS = {
        'charset': None,
        'class': None,
        'href': None,
        'hreflang': None,
        'media': None,
        'rel': None,
        'rev': None,
        'target': None,
        'type': None,
    }

class MAP(CompositeElement):
    "client-side image map"
    _ATTRS = {
        'class': None,
    }

class META(EmptyElement):
    "generic metainformation"
    _ATTRS = {
    }

class NOSCRIPT(CompositeElement):
    "alternate content container for non script-based rendering"
    _ATTRS = {
        'class': None,
    }

class OL(CompositeElement):
    "ordered list"
    _ATTRS = {
        'class': None,
    }

class OPTGROUP(CompositeElement):
    "option group"
    _ATTRS = {
        'class': None,
    }

class OPTION(CompositeElement):
    "selectable choice"
    _ATTRS = {
        'class': None,
        'disabled': None,
        'label': None,
        'selected': None,
        'value': None,
    }

class P(CompositeElement):
    "paragraph"
    _ATTRS = {
        'class': None,
    }

class PRE(CompositeElement):
    "preformatted text"
    _ATTRS = {
        'class': None,
    }

class Q(CompositeElement):
    "short inline quotation"
    _ATTRS = {
        'class': None,
    }

class SAMP(CompositeElement):
    "sample program output, scripts, etc."
    _ATTRS = {
        'class': None,
    }

class SCRIPT(CompositeElement):
    "script statements"
    _ATTRS = {
    }

class SELECT(CompositeElement):
    "option selector"
    _ATTRS = {
        'class': None,
        'disabled': None,
        'multiple': None,
        'name': None,
        'onblur': None,
        'onchange': None,
        'onfocus': None,
        'size': None,
        'tabindex': None,
    }

class SMALL(CompositeElement):
    "small text style"
    _ATTRS = {
        'class': None,
    }

class SPAN(CompositeElement):
    "generic language/style container"
    _ATTRS = {
        'class': None,
    }

class STRONG(CompositeElement):
    "strong emphasis"
    _ATTRS = {
        'class': None,
    }

class STYLE(CompositeElement):
    "style info"
    _ATTRS = {
    }

class SUB(CompositeElement):
    "subscript"
    _ATTRS = {
        'class': None,
    }

class SUP(CompositeElement):
    "superscript"
    _ATTRS = {
        'class': None,
    }

class TABLE(CompositeElement):
    "table"
    _ATTRS = {
        'align': None,
        'bgcolor': None,
        'border': None,
        'cellpadding': None,
        'cellspacing': None,
        'class': None,
        'frame': None,
        'rules': None,
        'summary': None,
        'width': None,
    }

class TBODY(CompositeElement):
    "table body"
    _ATTRS = {
        'align': None,
        'class': None,
    }

class TD(CompositeElement):
    "table data cell"
    _ATTRS = {
        'abbr': None,
        'align': None,
        'class': None,
        'valign': None,
    }

class TEXTAREA(CompositeElement):
    "multi-line text field"
    _ATTRS = {
        'class': None,
        'cols': None,
        'name': None,
        'rows': None,
        'id': None,
    }

class TFOOT(CompositeElement):
    "table footer"
    _ATTRS = {
        'align': None,
        'class': None,
    }

class TH(CompositeElement):
    "table header cell"
    _ATTRS = {
        'abbr': None,
        'align': None,
        'class': None,
    }

class THEAD(CompositeElement):
    "table header"
    _ATTRS = {
        'align': None,
        'class': None,
    }

class TITLE(CompositeElement):
    "document title"
    _ATTRS = {
    }

class TR(CompositeElement):
    "table row"
    _ATTRS = {
        'align': None,
        'class': None,
    }

class TT(CompositeElement):
    "teletype or monospaced text style"
    _ATTRS = {
        'class': None,
    }

class UL(CompositeElement):
    "unordered list"
    _ATTRS = {
        'class': None,
    }

class VAR(CompositeElement):
    "instance of a variable or program argument"
    _ATTRS = {
        'class': None,
    }


#############################################################################
### Widgets
#############################################################################

class FormWidget(Widget):
    """ Widget to display data as an HTML form.

        TODO: write code to combine the labels, data and HTML DOM to a
        complete form.

        INCOMPLETE!!!
    """
    def __init__(self, request, **kw):
        Widget.__init__(self, request)
        # FIXME     vvvv
        self.form = form(**kw)

    def render(self):
        self.request.write(str(self.form))

