// Generated by CoffeeScript 2.3.2
var ChronometerDial,
  boundMethodCheck = function(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new Error('Bound instance method accessed before binding'); } };

import {
  Subscriber,
  Container
} from './monitor.js';

import {
  is_empty
} from './monitor.js';

ChronometerDial = class ChronometerDial extends Subscriber {
  constructor() {
    super();
    this.update = this.update.bind(this);
    this.tick = this.tick.bind(this);
    this.tick_period = 250;
    this.subscribe();
  }

  update(data) {
    boundMethodCheck(this, ChronometerDial);
    this.sync_time = Date.now();
    this.time = data['time'];
    this.running = data['running'];
    this.tick();
    if (this.running) {
      return this.clock = setInterval(this.tick, this.tick_period);
    } else if (this.clock != null) {
      return clearInterval(this.clock);
    }
  }

  tick() {
    boundMethodCheck(this, ChronometerDial);
    if (this.time != null) {
      if (this.running) {
        return this.textContent = this.time_to_string(this.time + Date.now() - this.sync_time);
      } else {
        return this.textContent = this.time_to_string(this.time);
      }
    } else {
      return this.textContent = this.time_to_string(0);
    }
  }

  time_to_string(time) {
    var h, m, s;
    h = String(Math.floor(time / 3600000));
    m = String(Math.floor(time / 60000) % 60);
    s = String(Math.floor(time / 1000) % 60);
    return h.padStart(2, '0') + ':' + m.padStart(2, '0') + ':' + s.padStart(2, '0');
  }

};

customElements.define('chronometer-dial', ChronometerDial);
