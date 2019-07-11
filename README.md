# html-parser
Multilang object-oriented parsers.


### Python

`pip install git+git://github.com/thann/html_parser --user`
```python
from html_parser import HTMLParser, attr_name

class MyParser(HTMLParser):
    def some_attribute(self, doc):
        try:
            return doc.cssselect('span')[0].text
        except:  pass

    @attr_name()
    def hidden(self, obj):
        # call memoized function
        return self.some_attribute()
    # hidden.name = None

print(MyParser('<span>cool</span>'))
# ==> {'some_attribute': 'cool'}
```

### Javascript

`npm install thann/html_parser`

```javascript
const { HTMLParser } = require('html_parser');
class MyParser extends HTMLParser {
    some_attribute($, extras) {
      return $('span').text;
    }
}

console.log(MyParser('<span>cool</span>'))  ;
# ==> {'some_attribute': 'cool'}
```
