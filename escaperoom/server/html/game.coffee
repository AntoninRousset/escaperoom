import {Subscriber, Container} from './monitor.js'
import {is_empty, post_control} from './monitor.js'

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

    # listen to all changes on game options
    for e in @query_all_options_elements()
      e.onchange = (event) => @post_input_element(event.target)
      e.onkeyup = (event) =>
        if event.key == "Escape"
          @sync()
          event.target.blur()
      
    #@querySelector('#game-option-reset').onclick = (event) =>
    #  @read_options(@options)
    #@querySelector('#new-game').onclick = @new_game
    #@querySelector('#back-to-game').onclick = @back_to_game
    #@querySelector('#stop-game').onclick = @stop_game
  
  query_all_options_elements: () ->
    selector = '.game-option > input:not([type=button]), .game-option > select'
    all = @querySelectorAll(selector)
    console.log(selector)
    console.log(all)
    return all

  post_input_element: (e) ->

    e.setCustomValidity('Invalid')

    await post_control(@getAttribute('src'), {
      action: 'update_options',
      options: {[e.name]: e.value}
    })

  sync: () ->
    document.querySelector('game-box').sync()

  update: (data) ->

    @update_options(data.game.options, data.gamemasters)

    if data.game.running
      @querySelector('#new-game').setAttribute('hidden', '')
      @querySelector('#back-to-game').removeAttribute('hidden')
      @querySelector('#stop-game').disabled = false
      @querySelector('#game-creation').disabled = true
    else
      @querySelector('#new-game').removeAttribute('hidden')
      @querySelector('#back-to-game').setAttribute('hidden', '')
      @querySelector('#stop-game').disabled = true
      @querySelector('#game-creation').disabled = false

  update_options: (options, gamemasters) ->


    # set gamemasters list
    gmselect = @querySelector('#game-option-gamemaster')
    gmselect.innerHTML = ''
    for email, gm of gamemasters
      opt = document.createElement('option')
      opt.value = email
      opt.innerHTML = gm.firstname + ' ' + gm.lastname
      gmselect.appendChild(opt)


    # set fields values
    for k, v of options
      e = @querySelector('#game-option-' + k)
      e.value = v
      e.setCustomValidity('')

  new_game: () =>
    @querySelector('#game-creation').disabled = true
    await post_control(@getAttribute('src'), {
      action: 'new_game',
      options: {
        n_player: @querySelector('#game-option-number-player').value,
        children_mode: @querySelector('#game-option-children').checked,
        timeout_enabled: @querySelector('#game-option-timeout-enabled').value,
        timeout: '00:'+@querySelector('#game-option-timeout-h').value.padStart(2, '0')+':'+@querySelector('#game-option-timeout-m').value.padStart(2, '0')
      }
    })
    document.querySelector('game-box').current_screen = 'puzzles'

  back_to_game: () =>
    game_box = document.querySelector('game-box')
    game_box.current_screen = 'puzzles'
    game_box.set_screen(game_box.current_screen)

  stop_game: () =>
    post_control(@getAttribute('src'), {action: 'stop_game'})

customElements.define('game-menu', GameMenu)
