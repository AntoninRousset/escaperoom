is_empty = (obj) ->
	for key of obj
		return false
	return true

export default class Subscriber extends HTMLElement
	constructor: (keys=null) ->
		super()
		@subscription = null
		@loading_screen = this.querySelector('.loading')
		@empty_screen = this.querySelector('.empty')
		@error_screen = this.querySelector('.error')
		@template_header = @querySelector('template.header')
		@template_item = @querySelector('template.item')
		if keys? and @template_header?
			for key in keys
				span = document.createElement('span')
				span.setAttribute('slot', key)
				@appendChild(span)
			@attachShadow({mode: 'open'})
			@items_container = @shadowRoot
			@items_container.appendChild(@template_header.content.cloneNode(true))
		else
			@items_container = this

	subscribe: (path = null) ->
		if not path?
			path = @getAttribute('src')
		@unsubscribe()
		@subscription = new EventSource(path)
		@subscription.onmessage = (event) =>
			@set_state('good')
			@update(JSON.parse(event.data))
		@subscription.onerror = (error) =>
			#console.log(error)
			@set_state('error')

	unsubscribe: () ->
		if @subscription?
			@subscription.close()

	set_state: (state) ->
		if state is 'good'
			for node in @children
				node.style.display = 'inline'
			if @loading_screen?
				@loading_screen.style.display = 'none'
			if @empty_screen?
				@empty_screen.style.display = 'none'
			if @error_screen?
				@error_screen.style.display = 'none'
		else
			for node in @children
				node.style.display = 'none'
			if state is 'loading' and @loading_screen?
				@loading_screen.style.display = 'inline'
			if state is 'empty' and @empty_screen?
				@empty_screen.style.display = 'inline'
			if state is 'error' and @error_screen?
				@error_screen.style.display = 'inline'
	
	update: (datas) ->
		@read_items(datas)

	read_items: (items) ->
		if is_empty(items)
			@set_state('empty')
		for id in @items_ids()
			if id not of items
				@remove_item(id)
		for id, item of items
			if id not in @items_ids()
				@add_item(id, item)
			@update_item(id, item)

	items_ids: () ->
		items = @items_container.querySelectorAll('.item:not(template)')
		(item.getAttribute('item_id') for item in items)

	get_item: (id) ->
		selector = '.item[item_id="'+id+'"]:not(template)'
		@items_container.querySelector(selector)

	remove_item: (id) ->
		@get_item(id).remove()

