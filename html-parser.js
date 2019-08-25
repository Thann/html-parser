#!/usr/bin/env node
'use strict';

// Takes in something and returns a parsed object!
class BaseParser {
	constructor(doc, initialValues, extras) {
		// Stores values during parsing
		const values = initialValues || {};

		// Memoize all functions
		for (const prop of EveryPropIn(this, BaseParser)) {
			const ogFn = this[prop];
			this[prop] = function(x) {
				if (!Object.prototype.hasOwnProperty.call(values, prop)) {
					values[prop] = ogFn.call(this, doc, extras);
				}
				return values[prop];
			};
		}

		// Call all functions
		for (const prop of EveryPropIn(this, BaseParser)) {
			if (!Object.prototype.hasOwnProperty.call(values, prop))
				this[prop]();
		}

		// Assign all values
		for (const [prop, value] of Object.entries(values)) {
			this[prop] = value;
		}
	}
	// If you use async functions, await this!
	async promises() {
		const p = [];
		for (const prop of Object.getOwnPropertyNames(this)) {
			if (this[prop] instanceof Promise)
				p.push(this[prop].then((value) => {
					this[prop] = value;
				}));
		}
		await Promise.all(p);
		return this;
	}
}

// Takes in html and returns a parsed object!
class HTMLParser extends BaseParser {
	constructor(doc, initialValues, extras) {
		super(require('cheerio').load(doc), initialValues, extras);
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
		extras(doc, extras) {
			return extras;
		}
		doc(doc, extras) {
			return doc;
		}
	}

	const output = new MyParser(
			'<div class="dumb">ddd</div>',
			{init: 'something'},
			{extra: 'else'},
	);
	console.log(output);
	assert.deepEqual(output, {
		dumb: 'lame',
		extras: {
			extra: 'else',
		},
		init: 'something',
		doc: '<div class="dumb">ddd</div>',
	});

	class MySecondParser extends MyParser {
		weasel(doc, extras) {
			return `${this.dumb()}-bagel`;
		}
		dumb() {
			return 'dumber';
		}
	}

	const second = new MySecondParser(
		'<div class="dumb">second</div>',
		{init: 'something2'},
		{extra: 'else2'},
	);

	console.log(second);
	assert.deepEqual(second, {
		dumb: 'dumber',
		extras: {
			extra: 'else2',
		},
		weasel: 'dumber-bagel',
		init: 'something2',
		doc: '<div class="dumb">second</div>',
	});

	// async tests
	(async function() {
		class MyAsyncParser extends MySecondParser {
			async cat() {
				return 'cheshire';
			}
			async dog() {
				// NOTE: dont invoke non-async functions after awaiting!
				return `${await this.cat()}-${this.weasel}-dog`;
			}
		}

		const asyncP = new MyAsyncParser(
			'<div class="dumb">second</div>',
			{init: 'something3'},
			{extra: 'else3'},
		);

		console.log('before:', asyncP);
		const after = await asyncP.promises();
		assert( after === asyncP );
		console.log('after:', asyncP);
		assert.deepEqual(asyncP, {
			cat: 'cheshire',
			dog: 'cheshire-dumber-bagel-dog',
			dumb: 'dumber',
			extras: {
				extra: 'else3',
			},
			weasel: 'dumber-bagel',
			init: 'something3',
			doc: '<div class="dumb">second</div>',
		});
	})();
}
