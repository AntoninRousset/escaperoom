// Generated by CoffeeScript 2.3.2
var ActionItem, ActionsList, ConditionItem, ConditionsList, PuzzleInfo, PuzzlesBox, PuzzlesGraph, svgns,
  boundMethodCheck = function(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new Error('Bound instance method accessed before binding'); } };

import {
  Subscriber,
  Container
} from './monitor.js';

import {
  is_empty,
  post_control
} from './monitor.js';

PuzzlesBox = class PuzzlesBox extends Subscriber {
  constructor() {
    super();
    this.apply_template();
    this.shadowRoot.querySelector('#puzzles-menu').onclick = (event) => {
      var game_box;
      game_box = document.querySelector('game-box');
      game_box.current_screen = 'game';
      return game_box.set_screen(game_box.current_screen);
    };
    this.subscribe();
  }

  update(datas) {
    this.set_screen('graph');
    this.update_plugs(datas);
    return this.shadowRoot.querySelector('puzzles-graph').read_items(datas.conditions);
  }

};

customElements.define('puzzles-box', PuzzlesBox);

svgns = 'http://www.w3.org/2000/svg';

PuzzlesGraph = class PuzzlesGraph extends Container {
  constructor() {
    super();
    this.svg = document.createElementNS(svgns, 'svg');
    this.svg.setAttributeNS(null, 'style', 'width: 100%;');
    this.appendChild(this.svg);
    this.graph = document.createElementNS(svgns, 'g');
    this.graph.setAttributeNS(null, 'style', 'transform: translate(50%, 40px)');
    this.svg.appendChild(this.graph);
  }

  add_item(id, data) {
    var item;
    if (!((data.row != null) || (data.col != null))) {
      return;
    }
    item = document.createElementNS(svgns, 'circle');
    item.setAttributeNS(null, 'class', 'item');
    item.setAttributeNS(null, 'item_id', id);
    item.setAttributeNS(null, 'r', 20);
    item.onclick = (event) => {
      var puzzle_info;
      puzzle_info = this.parentNode.parentNode.querySelector('puzzle-info');
      return puzzle_info.select(id);
    };
    return this.graph.appendChild(item);
  }

  update_item(id, data) {
    var color, item;
    item = this.get_item(id);
    if (item == null) {
      return;
    }
    item.setAttributeNS(null, 'cx', 70 * data['col']);
    item.setAttributeNS(null, 'cy', 100 * data['row']);
    if (data['state']) {
      color = 'green';
    } else {
      color = 'red';
    }
    if (data['desactivated']) {
      color = 'gray';
    }
    return item.setAttributeNS(null, 'style', 'fill: ' + color + ';');
  }

  onupdated(datas) {
    var box;
    box = this.svg.getBBox();
    this.svg.setAttribute('width', box.x + box.width + box.x);
    return this.svg.setAttribute('height', box.y + box.height + box.y);
  }

};

customElements.define('puzzles-graph', PuzzlesGraph);

PuzzleInfo = class PuzzleInfo extends Subscriber {
  constructor() {
    super();
    this.set_force = this.set_force.bind(this);
    this.restore = this.restore.bind(this);
    this.set_active = this.set_active.bind(this);
    this.apply_template();
    this.state = null;
    this.shadowRoot.querySelector('#puzzle-complete').onclick = (event) => {
      return this.set_force(true);
    };
    this.shadowRoot.querySelector('#puzzle-uncomplete').onclick = (event) => {
      return this.set_force(false);
    };
    this.shadowRoot.querySelector('#puzzle-restore').onclick = this.restore;
    this.shadowRoot.querySelector('#puzzle-activate').onclick = (event) => {
      return this.set_active(true);
    };
    this.shadowRoot.querySelector('#puzzle-desactivate').onclick = (event) => {
      return this.set_active(false);
    };
    this.set_screen('empty');
    this.conditions_list = this.shadowRoot.querySelector('conditions-list');
    this.actions_list = this.shadowRoot.querySelector('actions-list');
  }

  select(id) {
    return this.subscribe('?id=' + id);
  }

  update(data) {
    this.update_plugs(data);
    if (data['state']) {
      this.shadowRoot.querySelector('#puzzle-complete').hidden = true;
      this.shadowRoot.querySelector('#puzzle-uncomplete').hidden = false;
    } else {
      this.shadowRoot.querySelector('#puzzle-complete').hidden = false;
      this.shadowRoot.querySelector('#puzzle-uncomplete').hidden = true;
    }
    if (data['forced']) {
      this.shadowRoot.querySelector('#puzzle-complete').hidden = true;
      this.shadowRoot.querySelector('#puzzle-uncomplete').hidden = true;
      this.shadowRoot.querySelector('#puzzle-restore').hidden = false;
    } else {
      this.shadowRoot.querySelector('#puzzle-restore').hidden = true;
    }
    if (data['desactivated']) {
      this.shadowRoot.querySelector('#puzzle-activate').hidden = false;
      this.shadowRoot.querySelector('#puzzle-desactivate').hidden = true;
    } else {
      this.shadowRoot.querySelector('#puzzle-activate').hidden = true;
      this.shadowRoot.querySelector('#puzzle-desactivate').hidden = false;
    }
    this.conditions_list.read_items(data.siblings);
    this.actions_list.read_items(data.actions);
    return this.set_screen('info');
  }

  set_force(state) {
    boundMethodCheck(this, PuzzleInfo);
    return post_control(this.loc, {
      action: 'force',
      state: state
    });
  }

  restore() {
    boundMethodCheck(this, PuzzleInfo);
    return post_control(this.loc, {
      action: 'restore'
    });
  }

  set_active(state) {
    boundMethodCheck(this, PuzzleInfo);
    return post_control(this.loc, {
      action: 'set_active',
      state: state
    });
  }

};

customElements.define('puzzle-info', PuzzleInfo);

ConditionsList = class ConditionsList extends Container {
  constructor() {
    super();
  }

  add_item(id, data) {
    var item;
    item = this.create_item(id);
    this.appendChild(item);
    return item.shadowRoot.querySelector('condition-item').select(id);
  }

};

customElements.define('conditions-list', ConditionsList);

ConditionItem = class ConditionItem extends Subscriber {
  constructor() {
    super();
    this.force = this.force.bind(this);
    this.restore = this.restore.bind(this);
    this.apply_template();
    this.state = null;
    this.shadowRoot.querySelector('div').querySelector('div').onclick = (event) => {
      return this.force(!this.state);
    };
    this.shadowRoot.querySelector('div').querySelector('button').onclick = (event) => {
      return this.restore();
    };
  }

  select(id) {
    return this.subscribe('?id=' + id);
  }

  update(datas) {
    var button, div;
    this.update_plugs(datas);
    div = this.shadowRoot.querySelector('div');
    button = this.shadowRoot.querySelector('div').querySelector('button');
    this.state = datas['state'];
    console.log(datas.state);
    if (datas.state == null) {
      div.style.borderColor = 'orange';
    } else if (datas['state']) {
      div.style.borderColor = 'green';
    } else {
      div.style.borderColor = 'red';
    }
    if (datas['forced']) {
      button.disabled = false;
    } else {
      button.disabled = true;
    }
    if (datas['desactivated']) {
      div.disabled = true;
      return div.style.borderColor = 'gray';
    } else {
      return div.disabled = false;
    }
  }

  force(state) {
    boundMethodCheck(this, ConditionItem);
    return post_control(this.loc, {
      action: 'force',
      state: state
    });
  }

  restore() {
    boundMethodCheck(this, ConditionItem);
    return post_control(this.loc, {
      action: 'restore'
    });
  }

};

customElements.define('condition-item', ConditionItem);

ActionsList = class ActionsList extends Container {
  constructor() {
    super();
  }

  add_item(id, data) {
    var item;
    item = this.create_item(id);
    this.appendChild(item);
    return item.shadowRoot.querySelector('action-item').select(id);
  }

};

customElements.define('actions-list', ActionsList);

ActionItem = class ActionItem extends Subscriber {
  constructor() {
    super();
    this.call = this.call.bind(this);
    this.abort = this.abort.bind(this);
    this.apply_template();
    this.shadowRoot.querySelector('div').querySelector('div').onclick = (event) => {
      return this.call();
    };
    this.shadowRoot.querySelector('div').querySelector('button').onclick = (event) => {
      return this.abort();
    };
  }

  select(id) {
    return this.subscribe('?id=' + id);
  }

  update(datas) {
    var div;
    this.update_plugs(datas);
    div = this.shadowRoot.querySelector('div');
    if (datas['running']) {
      div.style.borderColor = 'green';
    } else if (datas['failed']) {
      div.style.borderColor = 'red';
    } else {
      div.style.borderColor = 'orange';
    }
    if (datas['desactivated']) {
      div.disabled = true;
      return div.style.borderColor = 'gray';
    } else {
      return div.disabled = false;
    }
  }

  call() {
    boundMethodCheck(this, ActionItem);
    return post_control(this.loc, {
      action: 'call'
    });
  }

  abort() {
    boundMethodCheck(this, ActionItem);
    return post_control(this.loc, {
      action: 'abort'
    });
  }

};

customElements.define('action-item', ActionItem);
