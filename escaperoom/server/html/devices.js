// Generated by CoffeeScript 2.3.2
var DeviceAttributes, DeviceInfo, DevicesBox, DevicesList;

import {
  Subscriber,
  Container
} from './monitor.js';

import {
  is_empty
} from './monitor.js';

DevicesBox = class DevicesBox extends Subscriber {
  constructor() {
    super();
    this.apply_template();
    this.devices_list = this.shadowRoot.querySelector('devices-list');
    this.subscribe();
  }

  update(datas) {
    this.update_plugs(datas);
    this.devices_list.read_items(datas.devices);
    if (is_empty(datas.devices)) {
      return this.set_screen('empty');
    } else {
      return this.set_screen('main');
    }
  }

};

customElements.define('devices-box', DevicesBox);

DevicesList = class DevicesList extends Container {
  add_item(id, data) {
    var item;
    item = this.create_item(id);
    item.onclick = function(event) {
      var device_info, devices_box;
      devices_box = document.querySelector('devices-box');
      device_info = devices_box.shadowRoot.querySelector('device-info');
      return device_info.select(id);
    };
    return this.appendChild(item);
  }

  update_item(id, data) {
    var item, src;
    item = this.get_item(id);
    this.update_plugs(data, item);
    return src = 'ressources/' + data.type + '_logo.svg';
  }

  create_plug(slot) {
    var node;
    if (slot === 'type') {
      node = document.createElement('img');
    } else {
      node = document.createElement('span');
    }
    node.setAttribute('slot', slot);
    return node;
  }

  update_plug(slot, data, node) {
    node = node.querySelector('[slot=' + slot + ']');
    if (slot === 'type') {
      node.setAttribute('src', 'ressources/' + data[slot] + '_logo.svg');
      return node.setAttribute('alt', data[slot]);
    } else {
      return node.textContent = data[slot];
    }
  }

};

customElements.define('devices-list', DevicesList);

DeviceInfo = class DeviceInfo extends Subscriber {
  constructor() {
    super();
    this.apply_template();
    this.set_screen('empty');
    this.attrs_list = this.shadowRoot.querySelector('device-attributes');
  }

  select(id) {
    return this.subscribe('?id=' + id);
  }

  update(datas) {
    this.update_plugs(datas);
    this.attrs_list.read_items(datas.attrs);
    return this.set_screen('info');
  }

};

customElements.define('device-info', DeviceInfo);

DeviceAttributes = class DeviceAttributes extends Container {
  add_item(id, data) {
    var item;
    item = this.create_item(id);
    return this.appendChild(item);
  }

};

customElements.define('device-attributes', DeviceAttributes);
