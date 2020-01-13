// Generated by CoffeeScript 2.3.2
var CluesBox,
  boundMethodCheck = function(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new Error('Bound instance method accessed before binding'); } };

import {
  Subscriber,
  Container
} from './monitor.js';

import {
  is_empty
} from './monitor.js';

CluesBox = class CluesBox extends HTMLElement {
  constructor() {
    super();
    this.send_clue = this.send_clue.bind(this);
    this.querySelector('button').onclick = this.send_clue;
  }

  async send_clue(event) {
    var reponse, text;
    boundMethodCheck(this, CluesBox);
    text = this.parentNode.querySelector('input[type="text"]').value;
    return reponse = (await fetch('/time/display?name=clues', {
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        type: 'msg',
        msg: text
      }),
      method: 'POST'
    }));
  }

};

customElements.define('clues-box', CluesBox);
