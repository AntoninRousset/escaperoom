import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'

svgns = 'http://www.w3.org/2000/svg'

class PuzzlesBox extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@set_screen('loading')
		@puzzles_graph = @shadowRoot.querySelector('puzzles-graph')
		@current_screen = 'graph'
		menu = @shadowRoot.querySelector('.screen[name="menu"]')
		menu.querySelector('#game-option-timeout-enabled').onchange = @timeout_enabled
		menu.querySelector('#game-option-reset').onclick = @default_options
		menu.querySelector('#new-game').onclick = @new_game
		menu.querySelector('#back-to-game').onclick = (event) => @set_screen('graph')
		menu.querySelector('#stop-game').onclick = @stop_game
		@default_options = null
		@subscribe()

	update: (datas) ->
		@fill_slots(datas)
		@update_menu(datas)
		@puzzles_graph.read_items(datas.puzzles)
		if @current_screen == 'graph'
			if not datas.running
				@current_screen = 'menu'
			else if is_empty(datas.puzzles)
				@current_screen = 'empty'
		@set_screen(@current_screen)

	update_menu: (datas) ->
		if not default_options?
			@read_options(datas.default_options)
		@default_options = datas.default_options
		menu = @shadowRoot.querySelector('.screen[name="menu"]')
		new_game = menu.querySelector('#new-game')
		back_to_game = menu.querySelector('#back-to-game')
		stop_game = menu.querySelector('#stop-game')
		game_options = menu.querySelector('#game-options')
		if datas.running
			new_game.setAttribute('hidden', '')
			back_to_game.removeAttribute('hidden')
			stop_game.disabled = false
			game_options.disabled = true
		else
			new_game.removeAttribute('hidden')
			back_to_game.setAttribute('hidden', '')
			stop_game.disabled = true
			game_options.disabled = false

	timeout_enabled: (event) ->
		parent = @parentNode
		if @checked
			parent.removeAttribute('disabled')
			for node in parent.children
				node.removeAttribute('disabled')
		else
			parent.setAttribute('disabled', true)
			for node in parent.children
				node.setAttribute('disabled', true)
		@disabled = false

	default_options: () =>
		console.log('default_options')

	new_game: (event) =>
		reponse = await fetch(@getAttribute('src'), {
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				action: 'new_game',
				options: {
					status: 'test'
				}
			}),
			method: 'POST'
		})
		@set_screen('graph')

	stop_game: (event) =>
		console.log('stop game')

customElements.define('puzzles-box', PuzzlesBox)

class PuzzlesIssues extends Container
	constructor: () ->
		super()

customElements.define('puzzles-issues', PuzzlesIssues)

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
