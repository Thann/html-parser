# html-parser
Multilang object-oriented parsers.


### Python

`pip install git+git://github.com/thann/html-parser --user`
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

`npm install thann/html-parser cheerio`

```javascript
const { HTMLParser } = require('html-parser');
class MyParser extends HTMLParser {
    some_attribute($, extras) {
      return $('span').text();
    }
}

console.log(new MyParser('<span>cool</span>'))  ;
// MyParser { some_attribute: 'cool' }

```

#### Async / Await
```javascript
class AsyncParser extends MyParser {
    async other_attribute($, extras) {
      return this.some_attribute() + 'er';
    }
}

const ap = new AsyncParser('<span>cool</span>');
console.log(await ap.promises());
// AsyncParser { other_attribute: 'cooler', some_attribute: 'cool' }
```

