// Generated by CoffeeScript 2.3.2
var boundMethodCheck = function(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new Error('Bound instance method accessed before binding'); } };

import {
  FetchedElement
} from './fetch.mjs';

export var SyncedElement = (function() {
  var event_source, subscribers;

  class SyncedElement extends FetchedElement {
    constructor() {
      super(...arguments);
      this.connectedCallback = this.connectedCallback.bind(this);
      this.disconnectedCallback = this.disconnectedCallback.bind(this);
    }

    connectedCallback() {
      boundMethodCheck(this, SyncedElement);
      super.connectedCallback();
      if (this.src != null) {
        this.subscribe(this.src);
        return this.load_from_src();
      }
    }

    disconnectedCallback() {
      boundMethodCheck(this, SyncedElement);
      return this.unsubscribe();
    }

    subscribe() {
      // avoid subscribing twice
      this.unsubscribe();
      return subscribers.push(this);
    }

    unsubscribe() {
      var index;
      index = subscribers.indexOf(this);
      if (index > -1) {
        return subscribers.splice(index, 1);
      }
    }

  };

  subscribers = [];

  event_source = new EventSource('events');

  event_source.onmessage = function(event) {
    var data, i, len, results, src, subscriber;
    data = JSON.parse(event.data);
    if (data['type'] === 'update') {
      src = data['url'];
    }
    console.log('>', data);
    results = [];
    for (i = 0, len = subscribers.length; i < len; i++) {
      subscriber = subscribers[i];
      if (subscriber.src === src) {
        results.push(subscriber.load_from_src());
      } else {
        results.push(void 0);
      }
    }
    return results;
  };

  return SyncedElement;

}).call(this);