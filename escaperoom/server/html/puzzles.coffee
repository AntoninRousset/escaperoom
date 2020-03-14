import {Subscriber, Container} from './monitor.js'
import {is_empty, post_control} from './monitor.js'


class PuzzlesBox extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@shadowRoot.querySelector('#puzzles-menu').onclick = (event) =>
			game_box = document.querySelector('game-box')
			game_box.current_screen = 'game'
			game_box.set_screen(game_box.current_screen)
		@subscribe()

	update: (datas) ->
		@set_screen('graph')
		@update_plugs(datas)
		@shadowRoot.querySelector('puzzles-graph').read_items(datas.conditions)

customElements.define('puzzles-box', PuzzlesBox)


svgns = 'http://www.w3.org/2000/svg'
class PuzzlesGraph extends Container
	constructor: () ->
		super()
		@svg = document.createElementNS(svgns, 'svg')
		@svg.setAttributeNS(null, 'style', 'width: 100%;')
		@appendChild(@svg)
		@graph = document.createElementNS(svgns, 'g')
		@graph.setAttributeNS(null, 'style', 'transform: translate(50%, 40px)')
		@svg.appendChild(@graph)

	add_item: (id, data) ->
		if not (data.row? or data.col?)
			return
		item = document.createElementNS(svgns, 'circle')
		item.setAttributeNS(null, 'class', 'item')
		item.setAttributeNS(null, 'item_id', id)
		item.setAttributeNS(null, 'r', 20)
		item.onclick = (event) =>
			puzzle_info = @parentNode.parentNode.querySelector('puzzle-info')
			puzzle_info.select(id)
		@graph.appendChild(item)

	update_item: (id, data) ->
		item = @get_item(id)
		if not item?
			return
		item.setAttributeNS(null, 'cx', 70*data['col'])
		item.setAttributeNS(null, 'cy', 100*data['row'])
		if data['state']
			color = 'green'
		else
			color = 'red'
		if data['desactivated']
			color = 'gray'
		item.setAttributeNS(null, 'style', 'fill: '+color+';')

	onupdated: (datas) ->
		box = @svg.getBBox()
		@svg.setAttribute('width', box.x + box.width + box.x)
		@svg.setAttribute('height', box.y + box.height + box.y)


customElements.define('puzzles-graph', PuzzlesGraph)


class PuzzleInfo extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@state = null
		@shadowRoot.querySelector('#puzzle-complete').onclick = (event) =>
			@set_force(true)
		@shadowRoot.querySelector('#puzzle-uncomplete').onclick = (event) =>
			@set_force(false)
		@shadowRoot.querySelector('#puzzle-restore').onclick = @restore
		@shadowRoot.querySelector('#puzzle-activate').onclick = (event) =>
			@set_active(true)
		@shadowRoot.querySelector('#puzzle-desactivate').onclick = (event) =>
			@set_active(false)
		@set_screen('empty')
		@conditions_list = @shadowRoot.querySelector('conditions-list')
		@actions_list = @shadowRoot.querySelector('actions-list')

	select: (id) ->
		@subscribe('?id='+id)

	update: (data) ->
		@update_plugs(data)
		if data['state']
			@shadowRoot.querySelector('#puzzle-complete').hidden = true
			@shadowRoot.querySelector('#puzzle-uncomplete').hidden = false
		else
			@shadowRoot.querySelector('#puzzle-complete').hidden = false
			@shadowRoot.querySelector('#puzzle-uncomplete').hidden = true
		if data['forced']
			@shadowRoot.querySelector('#puzzle-complete').hidden = true
			@shadowRoot.querySelector('#puzzle-uncomplete').hidden = true
			@shadowRoot.querySelector('#puzzle-restore').hidden = false
		else
			@shadowRoot.querySelector('#puzzle-restore').hidden = true
		if data['desactivated']
			@shadowRoot.querySelector('#puzzle-activate').hidden = false
			@shadowRoot.querySelector('#puzzle-desactivate').hidden = true
		else
			@shadowRoot.querySelector('#puzzle-activate').hidden = true
			@shadowRoot.querySelector('#puzzle-desactivate').hidden = false
		@conditions_list.read_items(data.siblings)
		@actions_list.read_items(data.actions)
		@set_screen('info')

	set_force: (state) =>
		post_control(@loc, {action: 'force', state: state})

	restore: () =>
		post_control(@loc, {action: 'restore'})

	set_active: (state) =>
		post_control(@loc, {action: 'set_active', state: state})


customElements.define('puzzle-info', PuzzleInfo)


class ConditionsList extends Container
	constructor: () ->
		super()

	add_item: (id, data) ->
		item = @create_item(id)
		@appendChild(item)
		item.shadowRoot.querySelector('condition-item').select(id)

customElements.define('conditions-list', ConditionsList)


class ConditionItem extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@state = null
		@shadowRoot.querySelector('div').querySelector('div').onclick = (event) =>
			@force(not @state)
		@shadowRoot.querySelector('div').querySelector('button').onclick = (event) =>
			@restore()

	select: (id) ->
		@subscribe('?id='+id)

	update: (datas) ->
		@update_plugs(datas)
		div = @shadowRoot.querySelector('div')
		button = @shadowRoot.querySelector('div').querySelector('button')
		@state = datas['state']
		console.log(datas.state)
		if not datas.state?
			div.style.backgroundColor = 'orange'
		else if datas['state']
			div.style.backgroundColor = 'green'
		else
			div.style.backgroundColor = 'red'
		if datas['forced']
			button.disabled = false
		else
			button.disabled = true
		if datas['desactivated']
			div.disabled = true
			div.style.backgroundColor = 'gray'
		else
			div.disabled = false

	force: (state) =>
		post_control(@loc, {action: 'force', state: state})

	restore: () =>
		post_control(@loc, {action: 'restore'})


customElements.define('condition-item', ConditionItem)


class ActionsList extends Container
	constructor: () ->
		super()

	add_item: (id, data) ->
		item = @create_item(id)
		@appendChild(item)
		item.shadowRoot.querySelector('action-item').select(id)

customElements.define('actions-list', ActionsList)


class ActionItem extends Subscriber
	constructor: () ->
		super()
		@apply_template()

	select: (id) ->
		@subscribe('?id='+id)

	update: (datas) ->
		@update_plugs(datas)
		div = @shadowRoot.querySelector('div')
		if datas['running']
			div.style.backgroundColor = 'green'
		else if datas['failed']
			div.style.backgroundColor = 'red'
		else
			div.style.backgroundColor = 'orange'
		if datas['desactivated']
			div.disabled = true
			div.style.backgroundColor = 'gray'
		else
			div.disabled = false

customElements.define('action-item', ActionItem)


