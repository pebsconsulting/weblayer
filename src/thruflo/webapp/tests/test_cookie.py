#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

from datetime import timedelta
import time

import unittest
from mock import Mock

from thruflo.webapp.cookie import SecureCookieWrapper
from thruflo.webapp.cookie import _generate_cookie_signature

class TestInitCookie(unittest.TestCase):
    """ Test the logic of initialising a SecureCookieWrapper.
    """
    
    def setUp(self):
        self.context = Mock()
        self.context.settings = dict()
        self.context.settings['cookie_secret'] = ''
        self.cookie_wrapper = SecureCookieWrapper(self.context)
        
    
    
    def test_init_context(self):
        """ `self.context` is available as `self.context` within
          the `SecureCookieWrapper` instance.
        """
        
        self.assertTrue(self.cookie_wrapper.context == self.context)
        
    
    
    def test_init_context(self):
        """ `cookie_secret` is available as `self._cookie_secret` within
          the `SecureCookieWrapper` instance.
        """
        
        cs = self.context.settings['cookie_secret']
        self.assertTrue(self.cookie_wrapper._cookie_secret == cs)
        
    
    

class TestSetCookie(unittest.TestCase):
    """ Test the logic of setting a secure cookie.
    """
    
    def setUp(self):
        self.context = Mock()
        self.context.response = Mock()
        self.context.settings = dict()
        self.context.settings['cookie_secret'] = ''
        self.cookie_wrapper = SecureCookieWrapper(self.context)
        
    
    def test_name(self):
        """ Setting the cookie calls `self.context.response.set_cookie`
          with the 'name' as the first argument.
        """
        
        self.cookie_wrapper.set('name', 'value')
        args = self.context.response.set_cookie.call_args[0]
        self.assertTrue(args[0] == 'name')
        
    
    def test_name_is_basestring(self):
        """ The cookie name must be a basestring.
        """
        
        errs = (ValueError, TypeError)
        self.assertRaises(errs, self.cookie_wrapper.set, 0, 'value')
        
    
    def test_value(self):
        """ Setting the cookie runs the value through 
          `base64.b64encode` and puts into a '|' delimited string 
          with timestamp and hmac signature.
        """
        
        self.cookie_wrapper.set('name', 'value', timestamp='1')
        kwargs = self.context.response.set_cookie.call_args[1]
        value = 'dmFsdWU=|1|7bcc09ebef2f6c967201709ed3cbeac3e4cb2872'
        self.assertTrue(kwargs['value'] == value)
        
    
    def test_value_is_basestring(self):
        """ The cookie value must be a basestring.
        """
        
        errs = (ValueError, TypeError)
        self.assertRaises(errs, self.cookie_wrapper.set, 'name', 0)
        
    
    def test_expires_days(self):
        """ `expires_days` gets converted from days into seconds 
          and passed through as the `max_age`.
        """
        
        self.cookie_wrapper.set('name', 'value', expires_days=5)
        kwargs = self.context.response.set_cookie.call_args[1]
        five_days_as_seconds = 5 * 24 * 60 * 60
        self.assertTrue(kwargs['max_age'] == five_days_as_seconds)
        
    
    def test_expires_days_is_none(self):
        """ If the `expires_days` keyword argument is `None`,
          `max_age` is `None`.
        """
        
        self.cookie_wrapper.set('name', 'value', expires_days=None)
        kwargs = self.context.response.set_cookie.call_args[1]
        self.assertTrue(kwargs['max_age'] == None)
        
    
    def test_expires_days_is_int(self):
        """ If the `expires_days` keyword argument isn't `None` it
          must be an `int`.
        """
        
        self.cookie_wrapper.set('name', 'value', expires_days=None)
        kwargs = self.context.response.set_cookie.call_args[1]
        self.assertTrue(kwargs['max_age'] == None)
        self.assertRaises(
            TypeError,
            self.cookie_wrapper.set, 
            'name',
            'value',
            expires_days='30'
        )
        
    
    def test_kwargs(self):
        """ Other kwargs are passed through to 
          `self.context.response.set_cookie`,
        """
        
        self.cookie_wrapper.set('name', 'value', foo='bar')
        kwargs = self.context.response.set_cookie.call_args[1]
        self.assertTrue(kwargs['foo'] == 'bar')
        
    
    

class TestGetCookie(unittest.TestCase):
    """ Test the logic of getting a secure cookie.
    """
    
    def setUp(self):
        self.context = Mock()
        self.context.settings = dict()
        self.context.settings['cookie_secret'] = ''
        self.cookie_wrapper = SecureCookieWrapper(self.context)
        
    
    def test_get_name(self):
        """ Calling `get('name')` tries to get the value from
          `self.context.request.cookies`.
        """
        
        self.context.request.cookies = Mock()
        self.context.request.cookies.get.return_value = None
        self.cookie_wrapper.get('name')
        self.context.request.cookies.get.assert_called_with('name', None)
        
    
    def test_not_present(self):
        """ If the cookie doesn't exist, returns `None`.
        """
        
        self.context.request.cookies.get.return_value = None
        self.assertTrue(self.cookie_wrapper.get('name') is None)
        
    
    def test_split_value(self):
        """ If the cookie value doesn't split into three parts,
          delimited by '|' returns `None`.
        """
        
        value = Mock()
        value.__len__ = Mock()
        value.split.return_value = ['a', 'b']
        result = self.cookie_wrapper.get('name', value=value)
        value.split.assert_called_with("|")
        self.assertTrue(result is None)
        
    
    def test_timestamp_expired(self):
        """ If the timestamp is more than 31 days old, returns `None`.
        """
        
        t = time.time()
        too_old = str(int(t - 32 * 24 * 60 * 60))
        
        cs = self.context.settings['cookie_secret']
        sig = _generate_cookie_signature(cs, 'name', 'dmFsdWU=', too_old)
        value = 'dmFsdWU=|{}|{}'.format(too_old, sig)
        
        result = self.cookie_wrapper.get('name', value=value)
        self.assertTrue(result is None)
        
    
    
    def test_signature_doesnt_match(self):
        """ If the signature doesn't match, returns `None`.
        """
        
        t = time.time()
        ts = str(int(t))
        
        value = 'dmFsdWU=|{}|{}'.format(ts, 'not the right sig')
        
        result = self.cookie_wrapper.get('name', value=value)
        self.assertTrue(result is None)
        
    
    def test_value_is_base64_decodable(self):
        """ If the signature matches, the value comes back
          run through `base64.b64decode`.  If it can't be
          decoded, it raises a TypeError.
        """
        
        t = time.time()
        ts = str(int(t))
        
        cs = self.context.settings['cookie_secret']
        sig = _generate_cookie_signature(cs, 'name', 'a', ts)
        value = 'a|{}|{}'.format(ts, sig)
        
        result = self.cookie_wrapper.get('name', value=value)
        self.assertTrue(result is None)
        
    
    def test_get_value(self):
        """ If the signature matches, the value comes back
          run through `base64.b64decode`.
        """
        
        t = time.time()
        ts = str(int(t))
        
        cs = self.context.settings['cookie_secret']
        sig = _generate_cookie_signature(cs, 'name', 'dmFsdWU=', ts)
        value = 'dmFsdWU=|{}|{}'.format(ts, sig)
        
        result = self.cookie_wrapper.get('name', value=value)
        self.assertTrue(result == 'value')
        
    
    def test_delete(self):
        """ Calls `self.context.response.set_cookie` with
          `expires=datetime.timedelta(days=-5)`.
        """
        
        self.cookie_wrapper.delete('name')
        args = self.context.response.set_cookie.call_args[0]
        kwargs = self.context.response.set_cookie.call_args[1]
        self.assertTrue(args[0] == 'name')
        self.assertTrue(kwargs['expires'] == timedelta(days=-5))
        
    
    def test_delete_path_domain_defaults(self):
        """ `path` defaults to '/' and domain defaults to `None`.
        """
        
        self.cookie_wrapper.delete('name')
        kwargs = self.context.response.set_cookie.call_args[1]
        self.assertTrue(kwargs['path'] == '/')
        self.assertTrue(kwargs['domain'] is None)
        
        self.cookie_wrapper.delete('name', path='/foo', domain='bar')
        kwargs = self.context.response.set_cookie.call_args[1]
        self.assertTrue(kwargs['path'] == '/foo')
        self.assertTrue(kwargs['domain'] == 'bar')
        
    
    

class TestDeleteCookie(unittest.TestCase):
    """ Test the logic of deleting a cookie.
    """
    
    def setUp(self):
        self.context = Mock()
        self.context.settings = dict()
        self.context.settings['cookie_secret'] = ''
        self.cookie_wrapper = SecureCookieWrapper(self.context)
        
    
    
    def test_delete(self):
        """ Calls `self.context.response.set_cookie` with
          `expires=datetime.timedelta(days=-5)`.
        """
        
        self.cookie_wrapper.delete('name')
        args = self.context.response.set_cookie.call_args[0]
        kwargs = self.context.response.set_cookie.call_args[1]
        self.assertTrue(args[0] == 'name')
        self.assertTrue(kwargs['expires'] == timedelta(days=-5))
        
    
    
    def test_delete_defaults(self):
        """ `path` defaults to '/' and domain defaults to `None`.
        """
        
        self.cookie_wrapper.delete('name')
        kwargs = self.context.response.set_cookie.call_args[1]
        self.assertTrue(kwargs['path'] == '/')
        self.assertTrue(kwargs['domain'] is None)
        
        self.cookie_wrapper.delete('name', path='/foo', domain='bar')
        kwargs = self.context.response.set_cookie.call_args[1]
        self.assertTrue(kwargs['path'] == '/foo')
        self.assertTrue(kwargs['domain'] == 'bar')
        
    
    

