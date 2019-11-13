import Subscriber from './monitor.js'

class DevicesList extends Subscriber
	constructor: () ->
		super()
		@subscribe()

	add_item: (id, data) ->
		item = document.createElement('div')
		item.setAttribute('class', 'item')
		item.setAttribute('item_id', id)
		for key of data
			span = document.createElement('span')
			span.setAttribute('slot', key)
			item.appendChild(span)
		@items_container.appendChild(item)
		item.attachShadow({mode: 'open'}).appendChild(@template_item.content.cloneNode(true))
		info = item.shadowRoot.querySelector('device-info')
		info.query_str = '?id='+id
		details = item.shadowRoot.querySelector('details')
		details.addEventListener('toggle', (event) =>
			if (details.open)
				info.subscribe()
			else
				info.unsubscribe()
		)

	update_item: (id, data) ->
		item = @get_item(id)
		for key, value of data
			item.querySelector('span[slot='+key+']').textContent = value

class DeviceInfo extends Subscriber
	constructor: () ->
		super(slots=['name', 'msg', 'addr'])

	add_item: (id, data) ->
		item = document.createElement('div')
		item.setAttribute('class', 'item')
		item.setAttribute('item_id', id)
		for key of data
			span = document.createElement('span')
			span.setAttribute('slot', key)
			item.appendChild(span)
		@shadowRoot.appendChild(item)
		item.attachShadow( {mode:'open'} )
		item.shadowRoot.appendChild(@template_item.content.cloneNode(true))

	update: (datas) ->
		@read_slots(datas)
		@read_items(datas['attrs'])

	update_item: (id, data) ->
		item = @get_item(id)
		for key, value of data
			item.querySelector('span[slot='+key+']').textContent = value

	remove_item: (id) ->
		@item_node(uid).remove()
		@infos[uid] = null

customElements.define('devices-list', DevicesList)
customElements.define('device-info', DeviceInfo)
