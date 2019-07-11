#!/bin/env python

import re
import lxml.html
import lxml.etree
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    from inspect import getfullargspec as getargspec
except ImportError:
    from inspect import getargspec as getargspec


class HTMLParser(dict):
    """
    Turns HTML into a dict.
    Each function is passed an lxml.html parsing of the document,
    and returns a value for the dict.
    """

    def __init__(self, content, initial_data=None, **kwargs):
        # Uses the internal dict to remember values,
        # and the functions are always only called with the "document".
        def memoize(fn):
            extras = getargspec(fn).args[2:]
            extras = {k:v for k,v in kwargs.items() if k in extras}
            def memr(*args, **kwargs_):
                # setting the "name" attribute of a function will override the dict key.
                # if "name" is None, memoize value as hidden.
                fn_name = getattr(fn, 'name', fn.__name__) or fn.__name__
                container = fn.__self__ if getattr(fn, 'name', True) else hidden_values
                if fn_name not in container:
                    # ignore fn arguments, and always call with doc,
                    # and any expected kwargs from __init__
                    container[fn_name] = fn(self._doc__, **extras)
                return container[fn_name]
            return memr

        super(HTMLParser, self).__init__(initial_data or {});
        self._doc__ = self._parse__(content)
        hidden_values = {}
        methods = []

        # memoize each function
        for class_ in self.__class__.mro():
            if class_ == HTMLParser:  break  # only do it for subclasses
            for attr in class_.__dict__:
                # ignore builtin functions
                if not re.match(r'^_.+__$', attr):
                    fn = getattr(self, attr)
                    if fn and hasattr(fn, '__self__'):
                        public = getattr(fn, 'name', True)
                        fn = memoize(fn)
                        setattr(self, attr, fn)
                        if public:  methods.append(fn)

        # run each public function
        for fn in methods:  fn()

    @staticmethod
    def _parse__(content):
        return lxml.html.document_fromstring(content)


class XMLParser(HTMLParser):
    """
    Turns XML into a dict.
    Each function is passed an ElementTree of the document,
    and returns a value for the dict.
    """

    @staticmethod
    def _parse__(content):
        return ElementTree(lxml.etree.parse(
            StringIO(content), parser=lxml.etree.XMLParser(ns_clean=True)))


class ElementTree(object):
    """
    Wraps an XML tree or subtree.
    Each element can use css-selectors to list children or view their text.
    """
    def __init__(self, tree, parent=None):
        self.tree = tree
        self.parent = parent
        self.text = tree.text if parent else ''

    # Get text of a child node
    def __getitem__(self, item):
        path = '{}'.format('/'.join('{*}' + tag for tag in item.split('.')))
        node = self.tree.find(path)
        return node is not None and node.text or None

    # list children that match path
    def list(self, item):
        path = '{}'.format('/'.join('{*}' + tag for tag in item.split('.')))
        nodes = self.tree.findall(path)
        return [self.__class__(node, self) for node in nodes or []]

    def pretty_print(self):
        return lxml.etree.tostring(self.tree, pretty_print=True)


# decorator
def attr_name(name=None):
    def func(f):
        f.name = name
        return f
    return func


# Example usage
# class MyParser(HTMLParser):
#     def some_attribute(self, doc):
#         try:
#             return doc.cssselect('span')[0].text
#         except:  pass
#
#     @attr_name()
#     def hidden(self, obj):
#         # call memoized function
#         return self.some_attribute()
#     # hidden.name = None
#
# print(MyParser('<span>cool</span>'))  # ==> {'some_attribute': 'cool'}


# class MyXMLParser(XMLParser):
#     def some_attribute(self, doc, anything_extra=None):
#         return doc['span'] + anything_extra
#         # return doc.list('span')[0].text + anything_extra
#
# print(MyXMLParser('<xml><span>cool</span></xml>', anything_extra=' thing'))
# # ==> {'some_attribute': 'cool thing'}


####### TESTS #######
if __name__ == '__main__':
    import unittest
    import html_parser as lib
    try:
        import unittest.mock as mock
    except:
        import mock


    class TestHTMLParser(unittest.TestCase):
        class BasicParser(lib.HTMLParser):
            some_called = 0
            def some_attribute(self, doc):
                self.some_called += 1
                try:
                    return doc.cssselect('span')[0].text
                except:
                    return ''

        class FancyParser(BasicParser):
            hidden_called = 0
            unused_called = 0
            blah_called = 0

            @lib.attr_name()
            def hidden(self, doc):
                self.hidden_called += 1
                return self.some_attribute() + ' - hidden'

            @lib.attr_name("3$$$")
            def blah(self, doc):
                self.blah_called += 1
                return self.hidden() + ' - blah'

            @lib.attr_name()
            def unused(self, doc):
                self.unused_called += 1

        class ExtraParser(FancyParser):
            def blah(self, doc, extra=None):
                return self.hidden() + (extra or ' - blah')


        def test_basic(self):
            parser = self.BasicParser('<span>cool</span>');
            self.assertEqual(parser,
                {'some_attribute': 'cool'})
            self.assertEqual(parser.some_called, 1)
            self.assertEqual(parser.some_attribute(), 'cool')
            self.assertEqual(parser.some_called, 1)

        def test_fancy(self):
            parser = self.FancyParser('<span>cool</span>')
            self.assertEqual(parser,
                {'some_attribute': 'cool',
                 '3$$$': 'cool - hidden - blah'})
            self.assertEqual(parser.some_called, 1)
            self.assertEqual(parser.hidden_called, 1)
            self.assertEqual(parser.blah_called, 1)
            self.assertEqual(parser.unused_called, 0)
            self.assertEqual(parser.some_attribute(), 'cool')
            self.assertEqual(parser.hidden(), 'cool - hidden')
            self.assertEqual(parser.blah(), 'cool - hidden - blah')
            self.assertEqual(parser.unused(), None)
            self.assertEqual(parser.some_called, 1)
            self.assertEqual(parser.hidden_called, 1)
            self.assertEqual(parser.blah_called, 1)
            self.assertEqual(parser.unused_called, 1)

        def test_extra(self):
            self.assertEqual(self.ExtraParser('<span>cool</span>', extra=' - more'),
                {'some_attribute': 'cool',
                 'blah': 'cool - hidden - more'})
            self.assertEqual(self.ExtraParser('<span>cool</span>'),
                {'some_attribute': 'cool',
                 'blah': 'cool - hidden - blah'})
            self.assertEqual(self.ExtraParser('<span>cool</span>', lame="true"),
                {'some_attribute': 'cool',
                 'blah': 'cool - hidden - blah'})


    class TestXMLParser(unittest.TestCase):
        class BasicParser(lib.XMLParser):
            some_called = 0
            def some_attribute(self, doc):
                self.some_called += 1
                return doc['span']

        class FancyParser(BasicParser):
            hidden_called = 0
            blah_called = 0

            @lib.attr_name()
            def hidden(self, doc):
                self.hidden_called += 1
                return self.some_attribute() + ' - hidden'

            @lib.attr_name("_$$$")
            def blah(self, doc):
                self.blah_called += 1
                return self.hidden() + ' - blah'

            def list(self, doc):
                return [n.text for n in doc.list('span')]

            def empty_list(self, doc):
                return doc.list('rad')

        def test_basic(self):
            parser = self.BasicParser('<xml><span>cool</span></xml>');
            self.assertEqual(parser,
                {'some_attribute': 'cool'})
            self.assertEqual(parser.some_called, 1)
            self.assertEqual(parser.some_attribute(), 'cool')
            self.assertEqual(parser.some_called, 1)

        def test_fancy(self):
            parser = self.FancyParser('<xml><span>cool</span><span>rad</span></xml>');
            self.assertEqual(parser,
                {'some_attribute': 'cool',
                 '_$$$': 'cool - hidden - blah',
                 'list': ['cool', 'rad'],
                 'empty_list': []})
            self.assertEqual(parser.some_called, 1)
            self.assertEqual(parser.hidden_called, 1)
            self.assertEqual(parser.blah_called, 1)
            self.assertEqual(parser.some_attribute(), 'cool')
            self.assertEqual(parser.hidden(), 'cool - hidden')
            self.assertEqual(parser.blah(), 'cool - hidden - blah')
            self.assertEqual(parser.some_called, 1)
            self.assertEqual(parser.hidden_called, 1)
            self.assertEqual(parser.blah_called, 1)
            self.assertEqual(parser._doc__.list('span')[0].parent, parser._doc__)


    ## run tests ##
    import sys
    print("Python version: {}".format(sys.version))
    unittest.main()
