import {Subscriber, Container} from './monitor.js'
import {is_empty, post_control} from './monitor.js'

class GameBox extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@set_screen('game')
		@shadowRoot.querySelector('#restart-button').onclick = @end_game
		@subscribe()

	update: (datas) ->
		@update_plugs(datas)
		@shadowRoot.querySelector('game-menu').update(datas)
		if not datas.running
			@current_screen = 'game'
		else if not @current_screen?
			@current_screen = 'puzzles'
		@set_screen(@current_screen)

	end_game: () =>
		post_control(@getAttribute('src'), {action: 'end_game'})

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

    @querySelector('#new-game').onclick = @new_game
    @querySelector('#back-to-game').onclick = @back_to_game
    @querySelector('#stop-game').onclick = @stop_game

    # fill planned_date-time
    time = @querySelector('#game-option-planned_date-time')
    time.innerHTML = ''
    for h in [0..23]
      hh = h.toString().padStart(2, "0")
      for m in [0, 15, 30, 45]
        mm = m.toString().padStart(2, "0")
        opt = document.createElement('option')
        opt.value = hh + ':' + mm
        opt.innerHTML = opt.value
        time.appendChild(opt)

  query_all_options_elements: () ->
    selector = '.game-option > input:not([type=button]),'
    selector += ' .game-option > select, '
    selector += ' .game-option > textarea'
    all = @querySelectorAll(selector)
    return all

  post_input_element: (e) ->

    value = e.value

    if e.name == "planned_date"
      date = @querySelector('#game-option-planned_date-date').value
      time = @querySelector('#game-option-planned_date-time').value
      value = date + 'T' + time

    e.setCustomValidity('Invalid')

    await post_control(@getAttribute('src'), {
      action: 'update_options',
      options: {[e.name]: value}
    })

  sync: () ->
    document.querySelector('game-box').sync()

  update: (data) ->

    @update_options(data.game.options, data.gamemasters)

    if data.game.running
      @querySelector('#new-game').setAttribute('hidden', '')
      @querySelector('#back-to-game').removeAttribute('hidden')
      @querySelector('#stop-game').disabled = false

      @querySelector('#game-option-gamemaster').disabled = true
      @querySelector('#game-option-test').disabled = true
    else
      @querySelector('#new-game').removeAttribute('hidden')
      @querySelector('#back-to-game').setAttribute('hidden', '')
      @querySelector('#stop-game').disabled = true

      @querySelector('#game-option-gamemaster').disabled = false
      @querySelector('#game-option-test').disabled = false

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

      # set planned_datetime option
      if k == 'planned_date'
        e_date = @querySelector('#game-option-planned_date-date')
        e_time = @querySelector('#game-option-planned_date-time')
        if not v?
          # set planned_datetime-date to today
          today = new Date().toISOString().substr(0, 10)
          e_date.value = today
          e_time.value = null
        else
          e_date.value = v.substr(0, 10)
          e_time.value = v.substr(11, 5)
          e_date.setCustomValidity('')
          e_time.setCustomValidity('')

      # set any other options
      else
        e = @querySelector('#game-option-' + k)
        e.value = v
        e.setCustomValidity('')

  new_game: () =>
    await post_control(@getAttribute('src'), {
      action: 'new_game'
    })
    document.querySelector('game-box').current_screen = 'puzzles'

  back_to_game: () =>
    game_box = document.querySelector('game-box')
    game_box.current_screen = 'puzzles'
    game_box.set_screen(game_box.current_screen)

  stop_game: () =>
    post_control(@getAttribute('src'), {action: 'stop_game'})

customElements.define('game-menu', GameMenu)
