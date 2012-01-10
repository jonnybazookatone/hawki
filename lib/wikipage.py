
# Copyright (c) Max Planck Institute for Extraterrestrial Physics
# Beatriz Sanchez <bas@mpe.mpg.de>
# Abdullah Yoldas <yoldas@mpe.mpg.de>

import calendar
import os
import re
import sys
import time
import urllib
import urllib2
import urlparse
import mimetools
import mimetypes
import logging

from HTMLParser import HTMLParser

def get_opener():
    return urllib2.build_opener(urllib2.HTTPSHandler(),
                                urllib2.HTTPCookieProcessor())

try:
    opener
except NameError:
    opener = get_opener()

"""Wiki Page Base."""

def multipart(params):
    """Encode a multipart HTML form. See: RFC2388."""
    boundary = mimetools.choose_boundary()
    if hasattr(params, 'items'):
        params = params.items()
    L = []
    for key, value in params:
        L.append('--'+boundary)
        if hasattr(value, 'read'):
            if hasattr(value, 'name'):
                filename = os.path.basename(value.name)
            else:
                filename = 'file'
            L.append('Content-Disposition: form-data; '
                     'name="%s"; filename="%s"' % (key, filename))
            typ, enc = mimetypes.guess_type(filename)
            if not typ:
                typ = 'application/octet-stream'
            L.append('Content-Type: %s' % typ)
            if enc:
                L.append('Content-Encoding: %s' % enc)
            value = value.read()
        else:
            L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    L.append('--'+boundary+'--')
    L.append('')
    body = '\r\n'.join(L)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    content_length = len(body)
    return content_type, content_length, body

class EditorFormParser(HTMLParser):
    """Parser for the wiki page editor form."""
    
    def __init__(self):
        """Initialize the parser."""
        HTMLParser.__init__(self)
        self.in_form_tag = 0
        self.in_textarea = 0
        self.parser_done = 0
        self.editor_form = {}   # We are filling this.

    def handle_starttag(self, tag, attrs):
        """Look for the textarea element of the form."""
        if self.parser_done:
            return
        if self.in_form_tag:
            if tag == 'input':
                easy = dict(attrs)
                item = easy.get('name')
                if item:
                    self.editor_form[item] = easy.get('value', '')
            elif tag == 'textarea':
                self.in_textarea = 1
                self.editor_form['savetext'] = ''
        else:
            if tag == 'form':
                self.in_form_tag = 1

    def handle_data(self, data):
        """Collect the text."""
        if self.parser_done:
            return
        if self.in_form_tag:
            if self.in_textarea:
                self.editor_form['savetext'] += data

    def handle_entityref(self, name):
        """Handle entity references."""
        if self.parser_done:
            return
        if self.in_form_tag:
            if self.in_textarea:
                data = '&' + name + ';'
                self.editor_form['savetext'] += self.unescape(data)

    def handle_endtag(self, tag):
        """Look for the closing of the textarea."""
        if self.parser_done:
            return
        if self.in_form_tag:
            if tag == 'textarea':
                self.in_textarea = 0
            elif tag == 'form':
                self.in_form_tag = 0
                self.parser_done = 1

class StatusTextParser(HTMLParser):
    """Parser for the status text from the HTML. This is used after
    opening a page for editing."""

    def __init__(self):
        """Initialize the parser."""
        HTMLParser.__init__(self)
        self.in_message_div = 0
        self.in_status_p = 0
        self.parser_done = 0
        self.status_text = ''   # We are looking for this.

    def handle_starttag(self, tag, attrs):
        """Look for the status div."""
        if self.parser_done:
            return
        if self.in_message_div:
            if tag == 'p':
                easy = dict(attrs)
                if easy.get('class') == 'status':
                    self.in_status_p = 1
        else:
            if tag == 'div':
                easy = dict(attrs)
                if easy.get('id') == 'message':
                    self.in_message_div = 1

    def handle_data(self, data):
        """Collect the status text."""
        if self.parser_done:
            return
        if self.in_message_div:
            if self.in_status_p:
                self.status_text += data

    def handle_endtag(self, tag):
        """Look for the closing of the status text."""
        if self.parser_done:
            return
        if self.in_message_div:
            if tag == 'p':
                self.in_status_p = 0
            elif tag == 'div':
                self.in_message_div = 0
                self.parser_done = 1

class MessageTextParser(HTMLParser):
    """Parser for the message text from the HTML. This is used after
    saving a page."""

    def __init__(self):
        """Initialize the parser."""
        HTMLParser.__init__(self)
        self.in_message_div = 0
        self.in_text_div = 0
        self.parser_done = 0
        self.message_text = ''  # We are looking for this.

    def handle_starttag(self, tag, attrs):
        """Look for the message text."""""
        if self.parser_done:
            return
        if self.in_message_div:
            if tag == 'div':
                easy = dict(attrs)
                if easy.get('class'):
                    self.in_text_div = 1
        else:
            if tag == 'div':
                easy = dict(attrs)
                if easy.get('id') == 'message':
                    self.in_message_div = 1

    def handle_data(self, data):
        """Collect the message text."""
        if self.parser_done:
            return
        if self.in_message_div:
            if self.in_text_div:
                self.message_text += data

    def handle_endtag(self, tag):
        """Look for the closing of the div."""
        if self.parser_done:
            return
        if self.in_message_div:
            if tag == 'div':
                if self.in_text_div:    
                    self.in_text_div = 0
                else:
                    self.in_message_div = 0
                    self.parser_done = 1

class PageError(Exception):
    """Represents a generic page error."""
    pass

class PageIsLocked(PageError):
    """Represents an error when another user has the lock on a page."""
    pass

class WikiPage:
    """Represents a MoinMoin Wiki Page."""
    
    def __init__(self, wiki_url, pagename='', template='',
                 username='', password=''):
        """Initialize the page. wiki_url is the complete URL of the
        wiki. pagename is the name of the wiki page (unquoted).
        template is the template page to use if the page is a new page
        (unquoted). username is the wiki user name to use in login.
        password is the wiki user password to in login. """
        # Make sure that wiki_url ends with a slash, e.g.,
        # https://gamma-wiki.mpe.mpg.de/GROND/
        if wiki_url[-1] != '/':
            wiki_url += '/'
        self.wiki_url = wiki_url
        self.pagename = pagename    # Page Name, e.g., GRBs
        page_url = self.wiki_url
        if pagename:
            # Escape characters, e.g., space -> %20 as in
            # GRB 100103A -> GRB%20100103A
            page_url += urllib.quote(pagename)
        # The complete URL of the page, e.g.,
        # https://gamma-wiki.mpe.mpg.de/GROND/GRBs
        self.page_url = page_url
        self.template = template
        self.username = username
        self.password = password
        self.pageform = None    # Parsed editor form.
        self.linelist = None    # List of lines being edited.
        self.pagelock = 0       # Whether the page is already locked.

    def login(self):
        """Login to the wiki if necessary."""
        # Prepare the Login form parameters
        params = [('action', 'login'), ('login', 'login'),
            ('name', self.username), ('password', self.password)]
        data = urllib.urlencode(params, 1)  # Encode the post data
        url = self.page_url
        try:
            fp = opener.open(url, data) # post
        except urllib2.HTTPError, err:
            if err.code == 404:
                # HTTP 404 Not Found
                data = err.fp.read()
                if '<strong>This page does not exist yet.' in data:
                    # The page does not exist. This is not an error.
                    pass
                else:
                    # We should see the error and fix it.
                    raise
            else:
                # We should see what HTTP Error happened.
                raise

    def logout(self):
        """Logout of the wiki."""
        # Prepare the Logout form parameters.
        params = [('action', 'logout'), ('logout', 'logout')]
        data = urllib.urlencode(params) # Encode the get data.
        url = self.page_url + '?' + data
        try:
            fp = opener.open(url)       # get
            data = fp.read()    # HTTP 200 OK. We do not use the data.
            fp.close()
        except urllib2.HTTPError, err:
            if err.code == 404:
                # HTTP 404 Not Found
                data = err.fp.read()
                if '<strong>This page does not exist yet.' in data:
                    # This is not crucial. This is not an error.
                    pass
                else:
                    # We should see the error and fix it.
                    raise
            else:
                # We should see what HTTP Error happened.
                raise

    def open_raw(self):
        """Receive the page code as read-only."""
        # Prepare URL parameters.
        params = [('action', 'raw')]
        data = urllib.urlencode(params, 1)  # Encode the get data.
        url = self.page_url + '?' + data
        try:
            fp = opener.open(url)       # get
            data = fp.read()
            fp.close()
        except urllib2.HTTPError, err:
            raise
        # Split the page code into lines.
        self.linelist = data.split('\n')

    def open(self):
        """Open the page for editing."""
        # Prepare the Edit form parameters.
        params = [('action', 'edit'),('editor', 'text')]
        template = self.template
        if template:
            params.append(('template', template))
        data = urllib.urlencode(params, 1)  # Encode the get data.
        url = self.page_url + '?' + data
        try:
            fp = opener.open(url)       # get
            data = fp.read()
            fp.close()
        except urllib2.HTTPError, err:
            # We should see what HTTP Error happened.
            raise
        # Parse the status info from the returned HTML.
        parser = StatusTextParser()
        parser.feed(data)
        text = parser.status_text
        if 'You should refrain from editing this page' in text:
            # The page is locked for editing by someone else.
            self.pagelock = 1
        # Parse the wiki code from the returned HTML.
        parser = EditorFormParser()
        parser.feed(data)
        form = parser.editor_form
        self.pageform = form    # The parsed form parameters.
        text = form['savetext'] # Editable text inside the form.
        if text == 'Describe ' + self.pagename + ' here.':
            # The page is a new empty page.
            self.linelist = []
        else:
            # Split the page code into lines.
            self.linelist = text.split('\n')
            
            
            
            
    def delete_attachment(self,attachment):
        """Delete the attachment (vss 1/12)"""
        url = self.page_url + "?action=AttachFile&do=del&target=%s" % urllib.quote(attachment)
        try:
            fp = opener.open(url)       # get
            data = fp.read()
            fp.close()
        except urllib2.HTTPError, err:
            # We should see what HTTP Error happened.
            raise
       

    def save(self):
        """Save the page."""
        # Join the lines we have edited.
        text = '\n'.join(self.linelist)
        if not text:
            text = 'Describe ' + self.pagename + ' here.'
        # Prepare the post data.
        params = []
        form = self.pageform
        for name, value in form.items():
            if name.startswith('button_'):
                if name != 'button_save':
                    continue
            elif name == 'savetext':
                value = text
            params.append((name, value))
        data = urllib.urlencode(params, 1)  # Encode the post data.
        url = self.page_url
        try:
            fp = opener.open(url, data)  # post
            data = fp.read()
            fp.close()
        except urllib2.HTTPError, err:
            # We should see the error.
            raise
        # Parse the message from the returned HTML.
        parser = MessageTextParser()
        parser.feed(data)
        text = parser.message_text
        if "You can't change ACLs" in text:
            # This is a known error.
            raise PageError(text)
        # TODO: Find out if there are other errors (None so far).

    def undo(self):
        """Cancel editing to release the lock."""
        # Prepare the post data.
        params = []
        form = self.pageform
        if not form:
            # We were not editing it. So, we cannot cancel.
            return
        for name, value in form.items():
            if name.startswith('button_'):
                if name != 'button_cancel':
                    continue
            params.append((name, value))
        data = urllib.urlencode(params, 1)  # Encode the post data.
        url = self.page_url
        try:
            fp = opener.open(url, data)  # post
            data = fp.read()
            fp.close()
        except urllib2.HTTPError, err:
            if err.code == 404:
                # HTTP 404 Not Founf
                data = err.fp.read()
                if '<strong>This page does not exist yet.' in data:
                    # This page is a new empty wiki page.
                    pass
                else:
                    # We should see the error.
                    raise
            else:
                # We should see the HTTP error.
                raise

    def attach(self, file, rename='', overwrite=1):
        """Attach a file to the wiki page."""
        # Prepare the multipart form.
        fp = open(os.path.expanduser(file))
        params = [('file', fp), ('rename', rename),
            ('overwrite', '%s' % overwrite),
            ('action', 'AttachFile'), ('do', 'upload'),
            #('submit', 'Upload')
            ]
        ct, cl, data = multipart(params)
        fp.close()
        url = self.page_url
        headers = {'Content-Type': ct, 'Content-Length': cl}
        request = urllib2.Request(url, data, headers)
        fp = opener.open(request)    # POST multipart form
        fp.read()
        fp.close()
