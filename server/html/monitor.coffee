export is_empty = (obj) ->
	for key of obj
		return false
	return true

class Templated extends HTMLElement
	constructor: () ->
		super()
		@template = @querySelector('template')
		if @template?
			slots = @template.content.querySelectorAll('slot')
			@slots = (slot.getAttribute('name') for slot in slots)

	apply_template: (node=this) ->
		for slot in @slots
			span = document.createElement('span')
			span.setAttribute('slot', slot)
			node.appendChild(span)
		node.attachShadow({mode: 'open'})
		node.shadowRoot.appendChild(@template.content.cloneNode(true))
		node

	set_screen: (name, node=this) ->
		for screen in node.shadowRoot.querySelectorAll('.screen')
			if screen.getAttribute('name') is name
				screen.removeAttribute('hidden')
			else
				screen.setAttribute('hidden', 'true')

	fill_slots: (data, node=this) ->
		for slot in @slots
			span = node.querySelector('span[slot='+slot+']')
			span.textContent = data[slot]

export class Subscriber extends Templated
	constructor: () ->
		super()
		@subscription = null
		@query_str = ''

	subscribe: (path=null, query_str=null) ->
		if path?
			path = @setAttribute('src', path)
		else
			path = @getAttribute('src')
		if query_str?
			@query_str = query_str
		else
			query_str = @query_str
		loc = @getAttribute('src')+query_str
		@unsubscribe()
		@subscription = new EventSource(loc)
		@subscription.onmessage = (event) =>
			@update(JSON.parse(event.data))

	unsubscribe: () ->
		if @subscription?
			@subscription.close()

	update: (datas) ->
		@fill_slots(datas)

export class Container extends Templated
	constructor: () ->
		super()
		
	create_item: (id, type='div') ->
		item = document.createElement(type)
		item.setAttribute('class', 'item')
		item.setAttribute('item_id', id)
		@apply_template(item)

	update_item: (id, data) ->
		item = @get_item(id)
		@fill_slots(data, item)

	read_items: (datas) ->
		for id in @items_ids()
			if id not of datas
				@remove_item(id)
		for id, data of datas
			if id not in @items_ids()
				@add_item(id, data)
			@update_item(id, data)
		if is_empty(datas) and @onempty?
			@onempty()

	items_ids: () ->
		items = @querySelectorAll('.item:not(template)')
		(item.getAttribute('item_id') for item in items)

	get_item: (id) ->
		selector = '.item[item_id="'+id+'"]:not(template)'
		@querySelector(selector)

	remove_item: (id) ->
		@get_item(id).remove()

