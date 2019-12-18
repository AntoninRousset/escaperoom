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
		if @template.hasAttribute('class')
			node.setAttribute('class', @template.getAttribute('class'))
		for slot in @slots
			node.appendChild(@create_plug(slot))
		node.attachShadow({mode: 'open'})
		node.shadowRoot.appendChild(@template.content.cloneNode(true))
		node

	create_plug: (slot) ->
		span = document.createElement('span')
		span.setAttribute('slot', slot)
		span

	update_plugs: (data, node=this) ->
		for slot in @slots
			@update_plug(slot, data, node)

	update_plug: (slot, data, node) ->
		node = node.querySelector('[slot='+slot+']')
		node.textContent = data[slot]

	set_screen: (name, node=this) ->
		for screen in node.shadowRoot.querySelectorAll('.screen')
			if screen.getAttribute('name') is name
				screen.removeAttribute('hidden')
			else
				screen.setAttribute('hidden', '')

	has_screen: (name, node=this) ->
		if not node.shadowRoot?
			return false
		node.shadowRoot.querySelector('.screen[name="'+name+'"]')?

	get_screen: (node=this) ->
		@shadowRoot.querySelector('.screen:not([hidden])')

export class Subscriber extends Templated
	event_source = null
	subscribers = []

	constructor: () ->
		super()
		@loc = ''
				
	event_handler = (event) ->
		data = JSON.parse(event.data)
		for subscriber in subscribers
			if data['type'] == 'update' and data['loc'] == subscriber.loc
				await subscriber.sync()

	subscribe: (query_str='', path=null) ->
		if path?
			path = @setAttribute('src', path)
		else
			path = @getAttribute('src')
		@unsubscribe()
		@loc = path+query_str
		event_path = path.substring(0, path.lastIndexOf('/'))+'/events'
		if not event_source?
			event_source = new EventSource(event_path)
		subscribers.push(this)
		event_source.onmessage = event_handler
		@sync()

	sync: () =>
		now = new Date()
		@now = now
		loading_timeout = setTimeout(@onloading, 1000)
		response = await fetch(@loc)
		data = await response.json()
		clearTimeout(loading_timeout)
		if now is @now
			@update(data)

	onloading: (promise) =>
		if @has_screen('loading')
			@set_screen('loading')

	onerror: () =>
		if @has_screen('error')
			@set_screen('error')

	unsubscribe: () ->
		for i, subscriber of subscribers
			if this is subscriber
				subscribers.splice(i, 1)

	update: (datas) ->
		@update_plugs(datas)

export class Container extends Templated
	constructor: () ->
		super()
		
	create_item: (id, type='div') ->
		item = document.createElement(type)
		item.setAttribute('item_id', id)
		@apply_template(item)

	update_item: (id, data) ->
		item = @get_item(id)
		@update_plugs(data, item)

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

