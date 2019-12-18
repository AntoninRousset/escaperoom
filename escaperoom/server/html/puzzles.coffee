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
		@shadowRoot.querySelector('puzzles-graph').read_items(datas.puzzles)

customElements.define('puzzles-box', PuzzlesBox)

svgns = 'http://www.w3.org/2000/svg'

class PuzzlesGraph extends Container
	constructor: () ->
		super()
		svg = document.createElementNS(svgns, 'svg')
		svg.setAttributeNS(null, 'style', 'width: 100%;')
		@appendChild(svg)
		@graph = document.createElementNS(svgns, 'g')
		@graph.setAttributeNS(null, 'style', 'transform: translate(50%, 40px)')
		svg.appendChild(@graph)

	add_item: (id, data) ->
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
		item.setAttributeNS(null, 'cx', 80*data['col'])
		item.setAttributeNS(null, 'cy', 80*data['row'])
		colors = {'inactive' : 'red', 'active' : 'orange', 'completed' : 'green'}
		item.setAttributeNS(null, 'style', 'fill: '+colors[data['state']]+';')

customElements.define('puzzles-graph', PuzzlesGraph)

class PuzzleInfo extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@set_screen('empty')

	select: (id) ->
		@subscribe('?id='+id)

	update: (data) ->
		@update_plugs(data)
		if data.state == 'active'
			@shadowRoot.querySelector('#puzzle-activate').hidden = true
			@shadowRoot.querySelector('#puzzle-complete').hidden = false
			@shadowRoot.querySelector('#puzzle-complete').disabled = false
		@set_screen('info')

customElements.define('puzzle-info', PuzzleInfo)
