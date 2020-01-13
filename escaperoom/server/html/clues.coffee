import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'

class CluesBox extends HTMLElement
	constructor: () ->
		super()
		@querySelector('button').onclick = @send_clue

	send_clue: (event) =>
		text = @parentNode.querySelector('input[type="text"]').value
		reponse = await fetch('/time/display?name=clues', {
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				type: 'msg',
				msg: text
			}),
			method: 'POST'
		})

customElements.define('clues-box', CluesBox)

