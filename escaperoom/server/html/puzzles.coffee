import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'


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
		colors = {'inactive' : 'red', 'active' : 'orange', 'completed' : 'green'}
		item.setAttributeNS(null, 'style', 'fill: '+colors[data['state']]+';')

	onupdated: (datas) ->
		box = @svg.getBBox()
		@svg.setAttribute('width', box.x + box.width + box.x)
		@svg.setAttribute('height', box.y + box.height + box.y)


customElements.define('puzzles-graph', PuzzlesGraph)


class PuzzleInfo extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@shadowRoot.querySelector('#puzzle-activate').onclick = @activate
		@shadowRoot.querySelector('#puzzle-complete').onclick = @complete
		@shadowRoot.querySelector('#puzzle-restore').onclick = @restore
		@set_screen('empty')
		@conditions_list = @shadowRoot.querySelector('conditions-list')
		@actions_list = @shadowRoot.querySelector('actions-list')

	select: (id) ->
		@subscribe('?id='+id)

	update: (data) ->
		@update_plugs(data)
		if data.state == 'inactive'
			@shadowRoot.querySelector('#puzzle-activate').hidden = false
			@shadowRoot.querySelector('#puzzle-activate').disable = false
			@shadowRoot.querySelector('#puzzle-complete').hidden = true
		else if data.state == 'active'
			@shadowRoot.querySelector('#puzzle-activate').hidden = true
			@shadowRoot.querySelector('#puzzle-complete').hidden = false
			@shadowRoot.querySelector('#puzzle-complete').disabled = false
		else if data.state == 'completed'
			@shadowRoot.querySelector('#puzzle-activate').hidden = true
			@shadowRoot.querySelector('#puzzle-complete').hidden = true
		@conditions_list.read_items(data.siblings)
		@actions_list.read_items(data.actions)
		@set_screen('info')

	activate: () =>
		reponse = await fetch(@loc, {
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				action: 'activate'
			}),
			method: 'POST'
		})

	complete: () =>
		reponse = await fetch(@loc, {
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				action: 'complete'
			}),
			method: 'POST'
		})

	restore: () =>
		reponse = await fetch(@loc, {
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				action: 'restore'
			}),
			method: 'POST'
		})

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

	select: (id) ->
		@subscribe('?id='+id)

	update: (datas) ->
		@update_plugs(datas)
		div = @shadowRoot.querySelector('div')
		if datas['state'] == 'completed'
			div.style.backgroundColor = 'green'
		else if datas['state'] == 'active'
			div.style.backgroundColor = 'orange'
		else
			div.style.backgroundColor = 'red'
		if datas['desactivated']
			div.disabled = true
			div.style.backgroundColor = 'gray'
		else
			div.disabled = false

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


