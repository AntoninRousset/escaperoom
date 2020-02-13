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

	update: (datas) ->
		@update_plugs(datas)
		@attrs_list.read_items(datas.attrs)
		@set_screen('info')

customElements.define('device-info', DeviceInfo)


class DeviceAttributes extends Container
	constructor: () ->
		super()
		@focus_input = null

	add_item: (id, data) ->
		item = @create_item(id)
		input = item.shadowRoot.querySelector('input')
		input.onfocus = (event) =>
			@focus_input = input
		input.onchange = (event) =>
			if not input.disabled
				input.value = input.placeholder
		input.onkeydown = (event) =>
			if event.key == 'Enter'
				event.target.disabled = true
				event.target.blur()
				@focus_input = null
				@set_value(event)
		@appendChild(item)

	set_value: (event) ->
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
			input = node.shadowRoot.querySelector('input')
			input.placeholder = data[slot]
			if not (input is @focus_input)
				input.disabled = false
				input.value = input.placeholder
		else
			node = node.querySelector('[slot='+slot+']')
			node.textContent = data[slot]

customElements.define('device-attributes', DeviceAttributes)
