import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'

class DevicesBox extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@set_screen('loading')
		@devices_list = @shadowRoot.querySelector('devices-list')
		@subscribe()
		
	update: (datas) ->
		@fill_slots(datas)
		@devices_list.read_items(datas.devices)
		if is_empty(datas.devices)
			@set_screen('empty')
		else
			@set_screen('main')

customElements.define('devices-box', DevicesBox)

class DevicesList extends Container
	add_item: (id, data) ->
		item = @create_item(id)
		item.onclick = (event) ->
			devices_box = document.querySelector('devices-box')
			device_info = devices_box.shadowRoot.querySelector('device-info')
			device_info.select(id)
		@appendChild(item)

customElements.define('devices-list', DevicesList)

class DeviceInfo extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@set_screen('empty')
		@attrs_list = @shadowRoot.querySelector('attrs-list')
	
	select: (id) ->
		@set_screen('loading')
		@subscribe(null, '?id='+id)

	update: (datas) ->
		@fill_slots(datas)
		@attrs_list.read_items(datas.attrs)
		@set_screen('main')

customElements.define('device-info', DeviceInfo)

class AttrsList extends Container
	add_item: (id, data) ->
		item = @create_item(id)
		@appendChild(item)

customElements.define('attrs-list', AttrsList)
