// Generated by CoffeeScript 2.3.2
var Dashboard, Panel,
  boundMethodCheck = function(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new Error('Bound instance method accessed before binding'); } };

import {
  fetch_html
} from './communication.js';

Function.prototype.property = function(prop, desc) {
  return Object.defineProperty(this.prototype, prop, desc);
};

Panel = (function() {
  class Panel extends HTMLElement {
    constructor(name1, title1) {
      super();
      this.connectedCallback = this.connectedCallback.bind(this);
      // callback once the html document is loaded
      this.htmlLoadedCallback = this.htmlLoadedCallback.bind(this);
      this.toggleFold = this.toggleFold.bind(this);
      this.fold = this.fold.bind(this);
      this.unfold = this.unfold.bind(this);
      this.onload = this.onload.bind(this);
      this.name = name1;
      this.title = title1;
      // set default class
      this.classList.add('panel');
      this.classList.add('loadable');
      // loading mode by default
      this.setAttribute('loading', '');
    }

    connectedCallback() {
      var header, slow, url;
      boundMethodCheck(this, Panel);
      // create header, loading screen and content screen
      header = document.querySelector('#template-panel-header');
      header = header.content.cloneNode(true);
      header.querySelector('header > h1').textContent = this.title;
      header.querySelector('header > svg').onclick = this.toggleFold;
      this.innerHTML = '';
      this.appendChild(header);
      //shadowRoot = @attachShadow({mode: 'open'}).appendChild(template.cloneNode(true))

      // fetch html
      url = 'ressources/widgets/' + this.name + '/' + this.name + '.html';
      return fetch_html(url, slow = true).then(this.htmlLoadedCallback);
    }

    // callback if specified attributes are modified
    attributeChangedCallback(name, old_value, new_value) {
      return console.log(name, ' - ', old_value, ' - ', new_value);
    }

    htmlLoadedCallback(html) {
      var content;
      boundMethodCheck(this, Panel);
      content = html.querySelector('template').content.cloneNode(true);
      this.querySelector('.content').attachShadow({
        mode: 'open'
      }).appendChild(content);
      return this.removeAttribute('loading');
    }

    toggleFold() {
      boundMethodCheck(this, Panel);
      if (this.hasAttribute('folded')) {
        return this.unfold();
      } else {
        return this.fold();
      }
    }

    fold() {
      boundMethodCheck(this, Panel);
      return this.setAttribute('folded', '');
    }

    unfold() {
      boundMethodCheck(this, Panel);
      return this.removeAttribute('folded');
    }

    onload() {
      boundMethodCheck(this, Panel);
      return console.log('************');
    }

  };

  // listen to the following attributes
  Panel.property('observedAttributes', {
    get: function() {
      return ['folded'];
    }
  });

  return Panel;

}).call(this);

export var Widget = class Widget extends Panel {
  constructor(name, title) {
    super(name, title);
  }

};

Dashboard = class Dashboard extends HTMLElement {
  constructor() {
    super();
  }

};