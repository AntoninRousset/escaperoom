// Generated by CoffeeScript 2.3.2
var dom_parser,
  boundMethodCheck = function(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new Error('Bound instance method accessed before binding'); } };

import {
  MultiScreenElement
} from './screen.mjs';

import {
  sleep
} from './utils.mjs';

dom_parser = new DOMParser();

export var fetch_data = async function(url, data_type, emul_slow = false) {
  var resp;
  resp = (await fetch(url, {
    method: 'GET'
  }));
  if (emul_slow) {
    await sleep(Math.floor(Math.random() * 3000));
  }
  if (!resp.ok) {
    console.error('Failed to fetch', url);
    return null;
  }
  if (data_type === 'json') {
    return JSON.parse((await resp.text()));
  } else if (data_type === 'text') {
    return (await resp.text());
  } else if (data_type === 'html') {
    return resp.text().then(function(text) {
      return dom_parser.parseFromString(text, 'text/html');
    });
  } else {
    return console.error(`Invalid data_type ${data_type} during fetching`);
  }
};

export var FetchedElement = (function() {
  class FetchedElement extends MultiScreenElement {
    constructor(data_type1 = 'json', emul_slow1 = false) {
      super();
      this.onloading = this.onloading.bind(this);
      this.onnewdata = this.onnewdata.bind(this);
      this.load_from_src = this.load_from_src.bind(this);
      this.load_from = this.load_from.bind(this);
      this.attributeChangedCallback = this.attributeChangedCallback.bind(this);
      this.data_type = data_type1;
      this.emul_slow = emul_slow1;
      this._data = null;
      Object.defineProperty(this, 'data', {
        get: function() {
          return this._data;
        },
        set: function(data) {
          this.onnewdata(data);
          return this._data = data;
        }
      });
      Object.defineProperty(this, 'src', {
        get: function() {
          return this.getAttribute('src');
        },
        set: function(src) {
          return this.setAttribute('src', src);
        }
      });
    }

    onloading() {
      boundMethodCheck(this, FetchedElement);
      return this.set_screen('loading');
    }

    onnewdata(data) {
      boundMethodCheck(this, FetchedElement);
      return console.warn('Unused data', data);
    }

    load_from_src() {
      boundMethodCheck(this, FetchedElement);
      return this.load_from(this.src);
    }

    async load_from(src) {
      var data, loading_timeout, now;
      boundMethodCheck(this, FetchedElement);
      now = new Date();
      this.now = now;
      loading_timeout = setTimeout(this.onloading, 1000);
      data = (await fetch_data(src, this.data_type, this.emul_slow));
      clearTimeout(loading_timeout);
      if (now === this.now) {
        return this.data = data;
      }
    }

    attributeChangedCallback(name, old_value, new_value) {
      boundMethodCheck(this, FetchedElement);
      super.attributeChangedCallback(name, old_value, new_value);
      if (name === 'src') {
        return this.load_from(new_value);
      }
    }

  };

  Object.defineProperty(FetchedElement, 'observedAttributes', {
    get: () => {
      return MultiScreenElement.observedAttributes.concat(['src']);
    }
  });

  return FetchedElement;

}).call(this);
