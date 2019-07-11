#!/usr/bin/env node

// Takes in something and returns a parsed object!
class BaseParser {
  constructor(doc, initialValues, extras) {
    // Stores values during parsing
    const values = initialValues || {};

    // Memoize all functions
    for (const prop of EveryPropIn(this, BaseParser)) {
      const ogFn = this[prop];
      this[prop] = function(x) {
        if (!values.hasOwnProperty(prop)) {
          values[prop] = ogFn(doc, extras);
        }
        return values[prop];
      };
    }

    // Call all functions
    for (const prop of EveryPropIn(this, BaseParser)) {
      if (!values.hasOwnProperty(prop))
        this[prop]();
    }

    // Assign all values
    for (const [prop, value] of Object.entries(values)) {
      this[prop] = value;
    }
  }
}

// Takes in html and returns a parsed object!
const cheerio = require('cheerio');
class HTMLParser extends BaseParser {
  constructor(doc, initialValues, extras) {
    super(cheerio(doc), initialValues, extras);
  }
}

// Find every property name (including subclasses)
function EveryPropIn(klass, max=Object) {
  const props = new Set();
  do {
    for (const prop of Object.getOwnPropertyNames( klass )) {
      if (prop !== 'constructor')
        props.add(prop);
    }
  } while ((klass = Object.getPrototypeOf(klass)) && klass instanceof max);
  return props.keys();
}

module.exports = { BaseParser, HTMLParser, EveryPropIn };

// ==== TESTS ==== //
if (require.main === module) {
  const assert = require('assert');
  class MyParser extends BaseParser {
    dumb(doc, extras) {
      return 'lame';
    }
    extras( doc, extras ) {
      return extras;
    }
    doc( doc, extras ) {
      return doc;
    }
  }

  const output = new MyParser(
      '<div class="dumb">ddd</div>',
      {init: 'something'},
      {extra: 'else'}
  );
  console.log(output);
  assert.deepEqual(output, {
    dumb: 'lame',
    extras: {
      extra: 'else'
    },
    init: 'something',
    doc: '<div class="dumb">ddd</div>'
  });

  class MySecondParser extends MyParser {
    weasel(doc, extras) {
      return 'bagel';
    }
    dumb() {
      return 'dumber';
    }
  }

  const second = new MySecondParser(
      '<div class="dumb">second</div>',
      {init: 'something2'},
      {extra: 'else2'}
  );

  console.log(second);
  assert.deepEqual(second, {
    dumb: 'dumber',
    extras: {
      extra: 'else2'
    },
    weasel: 'bagel',
    init: 'something2',
    doc: '<div class="dumb">second</div>'
  });
}
