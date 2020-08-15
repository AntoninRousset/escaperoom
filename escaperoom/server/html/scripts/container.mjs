// Generated by CoffeeScript 2.3.2
var boundMethodCheck = function(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new Error('Bound instance method accessed before binding'); } };

import {
  SyncedElement
} from './sync.mjs';

import {
  is_empty
} from './utils.mjs';

import './libs/morphdom.js';

export var SyncedContainer = class SyncedContainer extends SyncedElement {
  constructor() {
    super();
    this.get_body = this.get_body.bind(this);
    Object.defineProperty(this, 'body', {
      get: () => {
        return this.get_body();
      },
      set: (newbody) => {
        return morphdom(this.body, newbody, {
          getNodeKey: (node) => {
            try {
              return node.getAttribute('item_id');
            } catch (error) {}
          },
          onBeforeElUpdated: (from_element, to_element) => {
            if (this.onBeforeElementUpdated != null) {
              return this.onBeforeElementUpdated(from_element, to_element);
            }
          },
          childrenOnly: true
        });
      }
    });
  }

  get_body() {
    boundMethodCheck(this, SyncedContainer);
    return this.querySelector('*.body');
  }

};
