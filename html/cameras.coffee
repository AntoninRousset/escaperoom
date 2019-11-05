import Subscriber from './monitor.js'

class CamerasList extends Subscriber
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

	update_item: (id, data) ->
		item = @get_item(id)
		for key, value of data
			item.querySelector('span[slot='+key+']').textContent = value

customElements.define('cameras-list', CamerasList)
