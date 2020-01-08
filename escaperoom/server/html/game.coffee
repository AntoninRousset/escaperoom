import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'

class GameBox extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@set_screen('game')
		@subscribe()

	update: (datas) ->
		@update_plugs(datas)
		@shadowRoot.querySelector('game-menu').update(datas)
		if not datas.running
			@current_screen = 'game'
		else if not @current_screen?
			@current_screen = 'puzzles'
		@set_screen(@current_screen)

customElements.define('game-box', GameBox)

class GameIssues extends Container
	constructor: () ->
		super()

customElements.define('game-issues', GameIssues)

class GameMenu extends HTMLElement
	constructor: () ->
		super()
		@querySelector('#game-option-timeout-enabled').onchange = (event) =>
			@timeout_enabled_changed()
		@querySelector('#game-option-reset').onclick = (event) =>
			@read_options(@default_options)
		@querySelector('#new-game').onclick = @new_game
		@querySelector('#back-to-game').onclick = @back_to_game
		@querySelector('#stop-game').onclick = @stop_game

	update: (datas) ->
		if not default_options?
			@read_options(datas.default_options)
		@default_options = datas.default_options
		if datas.running
			@querySelector('#new-game').setAttribute('hidden', '')
			@querySelector('#back-to-game').removeAttribute('hidden')
			@querySelector('#stop-game').disabled = false
			@querySelector('#game-options').disabled = true
		else
			@querySelector('#new-game').removeAttribute('hidden')
			@querySelector('#back-to-game').setAttribute('hidden', '')
			@querySelector('#stop-game').disabled = true
			@querySelector('#game-options').disabled = false

	timeout_enabled_changed: () ->
		timeout_div = @querySelector('#game-option-timeout')
		if timeout_div.querySelector('#game-option-timeout-enabled').checked
			timeout_div.removeAttribute('disabled')
			for node in timeout_div.children
				node.removeAttribute('disabled')
		else
			timeout_div.setAttribute('disabled', true)
			for node in timeout_div.children
				node.setAttribute('disabled', true)
		timeout_div.querySelector('#game-option-timeout-enabled').disabled = false

	read_options: (data) ->
		@querySelector('#game-option-status').value = data.status
		@querySelector('#game-option-number-player').value = data.n_player
		@querySelector('#game-option-children').value = data.children_mode
		@querySelector('#game-option-timeout-enabled').checked = data.timeout_enabled
		@querySelector('#game-option-timeout-h').value = data.timeout.split(':')[0]
		@querySelector('#game-option-timeout-m').value = data.timeout.split(':')[1]
		@timeout_enabled_changed()

	new_game: () =>
		@querySelector('#game-options').disabled = true
		reponse = await fetch(@getAttribute('src'), {
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				action: 'new_game',
				options: {
					status: @querySelector('#game-option-status').value,
					n_player: @querySelector('#game-option-number-player').value,
					children_mode: @querySelector('#game-option-children').checked,
					timeout_enabled: @querySelector('#game-option-timeout-enabled').value,
					timeout: '00:'+@querySelector('#game-option-timeout-h').value.padStart(2, '0')+':'+@querySelector('#game-option-timeout-m').value.padStart(2, '0')
				}
			}),
			method: 'POST'
		})
		document.querySelector('game-box').current_screen = 'puzzles'

	back_to_game: () =>
		game_box = document.querySelector('game-box')
		game_box.current_screen = 'puzzles'
		game_box.set_screen(game_box.current_screen)

	stop_game: () =>
		reponse = await fetch(@getAttribute('src'), {
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				action: 'stop_game'
			}),
			method: 'POST'
		})

customElements.define('game-menu', GameMenu)

