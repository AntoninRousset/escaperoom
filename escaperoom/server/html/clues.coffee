import {Subscriber, Container} from './monitor.js'
import {is_empty, post_control} from './monitor.js'

class CluesBox extends HTMLElement
	constructor: () ->
		super()
		@querySelector('button').onclick = @send_clue

	send_clue: (event) =>
		text = event.target.parentNode.querySelector('textarea').value
		post_control('/display', {action: 'clue', text: text})


customElements.define('clues-box', CluesBox)

