import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'

class DevicesBox extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@devices_list = @shadowRoot.querySelector('devices-list')
		@subscribe()
		
	update: (datas) ->
		@update_plugs(datas)
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

	update_item: (id, data) ->
		item = @get_item(id)
		@update_plugs(data, item)
		src = 'ressources/'+data.type+'_logo.svg'

	create_plug: (slot) ->
		if slot == 'type'
			node = document.createElement('img')
		else
			node = document.createElement('span')
		node.setAttribute('slot', slot)
		node

	update_plug: (slot, data, node) ->
		node = node.querySelector('[slot='+slot+']')
		if slot == 'type'
			node.setAttribute('src', 'ressources/'+data[slot]+'_logo.svg')
			node.setAttribute('alt', data[slot])
		else
			node.textContent = data[slot]

customElements.define('devices-list', DevicesList)

class DeviceInfo extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@set_screen('empty')
		@attrs_list = @shadowRoot.querySelector('device-attributes')
	
	select: (id) ->
		@subscribe('?id='+id)
		console.log('subscribed')

	update: (datas) ->
		console.log('update')
		@update_plugs(datas)
		@attrs_list.read_items(datas.attrs)
		@set_screen('info')
		console.log('done')

customElements.define('device-info', DeviceInfo)

class DeviceAttributes extends Container
	add_item: (id, data) ->
		item = @create_item(id)
		item.shadowRoot.querySelector('input').onchange = @set_value
		@appendChild(item)

	set_value: (event) =>
		event.target.disabled = true
		attr_name = event.target.parentNode.querySelector('slot[name="name"]').assignedNodes()[0].textContent
		device_info = document.querySelector('devices-box').shadowRoot.querySelector('device-info')
		loc = device_info.loc
		response = await fetch(loc,  {
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				action: 'set_val',
				name: attr_name,
				value: event.target.value
			}),
			method: 'POST'
		})

	update_plug: (slot, data, node) ->
		if slot == 'value'
			node = node.shadowRoot.querySelector('input')
			node.value = data[slot]
			node.disabled = false
		else
			node = node.querySelector('[slot='+slot+']')
			node.textContent = data[slot]



customElements.define('device-attributes', DeviceAttributes)
