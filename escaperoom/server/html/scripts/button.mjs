// Generated by CoffeeScript 2.3.2
var ButtonElement;

import {
  MultiScreenElement
} from './screen.mjs';

ButtonElement = class ButtonElement extends MultiScreenElement {
  constructor(default_screen) {
    super(default_screen);
  }

};

//@addEventListener('click', @onclick)
customElements.define('btn-checkbox', class extends ButtonElement {
  constructor() {
    super('loading');
  }

});