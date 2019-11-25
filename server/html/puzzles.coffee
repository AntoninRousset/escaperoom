import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'

svgns = 'http://www.w3.org/2000/svg'

class PuzzlesBox extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@set_screen('loading')
		@puzzles_graph = @shadowRoot.querySelector('puzzles-graph')
		@subscribe()

	update: (datas) ->
		@fill_slots(datas)
		@puzzles_graph.read_items(datas.puzzles)
		if is_empty(datas.puzzles)
			@set_screen('empty')
		else
			@set_screen('graph')

customElements.define('puzzles-box', PuzzlesBox)

class PuzzlesGraph extends Container
	constructor: () ->
		super()
		svg = document.createElementNS(svgns, 'svg')
		svg.setAttributeNS(null, 'style', 'width: 100%')
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
			puzzles_box = document.querySelector('puzzles-box')
			puzzle_info = puzzles_box.shadowRoot.querySelector('puzzle-info')
			puzzle_info.select(id)
		@graph.appendChild(item)

	update_item: (id, data) ->
		item = @get_item(id)
		item.setAttributeNS(null, 'cx', 80*data['col'])
		item.setAttributeNS(null, 'cy', 80*data['row'])
		colors = {'inactive' : 'red', 'active' : 'orange', 'completed' : 'green'}
		item.setAttributeNS(null, 'style', 'fill: '+colors[data['state']]+';')

class PuzzleInfo extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@set_screen('empty')

	select: (id) ->
		@set_screen('loading')
		@subscribe(null, '?id='+id)

	update: (datas) ->
		@fill_slots(datas)
		@set_screen('main')

customElements.define('puzzles-graph', PuzzlesGraph)
customElements.define('puzzle-info', PuzzleInfo)
