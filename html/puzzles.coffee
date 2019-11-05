import Subscriber from './monitor.js'

svgns = 'http://www.w3.org/2000/svg'

class PuzzlesGraph extends Subscriber
	constructor: () ->
		super()
		@svg = document.createElementNS(svgns, 'svg')
		@svg.setAttributeNS(null, 'style', 'width: 100%')
		@items_container.appendChild(@svg)
		@graph = document.createElementNS(svgns, 'g')
		@graph.setAttributeNS(null, 'style', 'transform: translate(50%, 40px)')
		@svg.appendChild(@graph)
		@subscribe()

	add_item: (id, data) ->
		item = document.createElementNS(svgns, 'circle')
		item.setAttributeNS(null, 'class', 'item')
		item.setAttributeNS(null, 'item_id', id)
		item.setAttributeNS(null, 'r', 20)
		@graph.appendChild(item)

	update_item: (id, data) ->
		item = @get_item(id)
		item.setAttributeNS(null, 'cx', 80*data['col'])
		item.setAttributeNS(null, 'cy', 80*data['row'])
		colors = {'inactive' : 'red', 'active' : 'orange', 'completed' : 'green'}
		item.setAttributeNS(null, 'style', 'fill: '+colors[data['state']]+';')

class PuzzleInfo extends Subscriber
	constructor: () ->
		super(['id', 'name', 'msg', 'addr'])

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
		for key in ['id', 'name', 'msg', 'addr']
			span = @querySelector('span[slot='+key+']')
			span.textContent = datas[key]
		@read_items(datas['attrs'])

	update_item: (id, data) ->
		item = @get_item(id)
		for key, value of data
			item.querySelector('span[slot='+key+']').textContent = value

customElements.define('puzzles-graph', PuzzlesGraph)
customElements.define('puzzle-info', PuzzleInfo)
