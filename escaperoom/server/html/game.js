// Generated by CoffeeScript 2.3.2
var GameBox, GameIssues, GameMenu,
  boundMethodCheck = function(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new Error('Bound instance method accessed before binding'); } };

import {
  Subscriber,
  Container
} from './monitor.js';

import {
  is_empty,
  post_control
} from './monitor.js';

GameBox = class GameBox extends Subscriber {
  constructor() {
    super();
    this.apply_template();
    this.set_screen('game');
    this.subscribe();
  }

  update(datas) {
    this.update_plugs(datas);
    this.shadowRoot.querySelector('game-menu').update(datas);
    if (!datas.running) {
      this.current_screen = 'game';
    } else if (this.current_screen == null) {
      this.current_screen = 'puzzles';
    }
    return this.set_screen(this.current_screen);
  }

};

customElements.define('game-box', GameBox);

GameIssues = class GameIssues extends Container {
  constructor() {
    super();
  }

};

customElements.define('game-issues', GameIssues);

GameMenu = class GameMenu extends HTMLElement {
  constructor() {
    super();
    this.new_game = this.new_game.bind(this);
    this.back_to_game = this.back_to_game.bind(this);
    this.stop_game = this.stop_game.bind(this);
    this.querySelector('#game-option-timeout-enabled').onchange = (event) => {
      return this.timeout_enabled_changed();
    };
    this.querySelector('#game-option-reset').onclick = (event) => {
      return this.read_options(this.options);
    };
    this.querySelector('#new-game').onclick = this.new_game;
    this.querySelector('#back-to-game').onclick = this.back_to_game;
    this.querySelector('#stop-game').onclick = this.stop_game;
  }

  update(datas) {
    if (this.options == null) {
      this.read_options(datas.options);
    }
    this.options = datas.options;
    if (datas.running) {
      this.querySelector('#new-game').setAttribute('hidden', '');
      this.querySelector('#back-to-game').removeAttribute('hidden');
      this.querySelector('#stop-game').disabled = false;
      return this.querySelector('#game-options').disabled = true;
    } else {
      this.querySelector('#new-game').removeAttribute('hidden');
      this.querySelector('#back-to-game').setAttribute('hidden', '');
      this.querySelector('#stop-game').disabled = true;
      return this.querySelector('#game-options').disabled = false;
    }
  }

  timeout_enabled_changed() {
    var i, j, len, len1, node, ref, ref1, timeout_div;
    timeout_div = this.querySelector('#game-option-timeout');
    if (timeout_div.querySelector('#game-option-timeout-enabled').checked) {
      timeout_div.removeAttribute('disabled');
      ref = timeout_div.children;
      for (i = 0, len = ref.length; i < len; i++) {
        node = ref[i];
        node.removeAttribute('disabled');
      }
    } else {
      timeout_div.setAttribute('disabled', true);
      ref1 = timeout_div.children;
      for (j = 0, len1 = ref1.length; j < len1; j++) {
        node = ref1[j];
        node.setAttribute('disabled', true);
      }
    }
    return timeout_div.querySelector('#game-option-timeout-enabled').disabled = false;
  }

  read_options(data) {
    this.querySelector('#game-option-status').value = data.status;
    this.querySelector('#game-option-number-player').value = data.n_player;
    this.querySelector('#game-option-children').value = data.children_mode;
    this.querySelector('#game-option-timeout-enabled').checked = data.timeout_enabled;
    this.querySelector('#game-option-timeout-h').value = data.timeout.split(':')[0];
    this.querySelector('#game-option-timeout-m').value = data.timeout.split(':')[1];
    return this.timeout_enabled_changed();
  }

  async new_game() {
    boundMethodCheck(this, GameMenu);
    this.querySelector('#game-options').disabled = true;
    await post_control(this.getAttribute('src'), {
      action: 'new_game',
      options: {
        status: this.querySelector('#game-option-status').value,
        n_player: this.querySelector('#game-option-number-player').value,
        children_mode: this.querySelector('#game-option-children').checked,
        timeout_enabled: this.querySelector('#game-option-timeout-enabled').value,
        timeout: '00:' + this.querySelector('#game-option-timeout-h').value.padStart(2, '0') + ':' + this.querySelector('#game-option-timeout-m').value.padStart(2, '0')
      }
    });
    return document.querySelector('game-box').current_screen = 'puzzles';
  }

  back_to_game() {
    var game_box;
    boundMethodCheck(this, GameMenu);
    game_box = document.querySelector('game-box');
    game_box.current_screen = 'puzzles';
    return game_box.set_screen(game_box.current_screen);
  }

  stop_game() {
    boundMethodCheck(this, GameMenu);
    return post_control(this.getAttribute('src'), {
      action: 'stop_game'
    });
  }

};

customElements.define('game-menu', GameMenu);
