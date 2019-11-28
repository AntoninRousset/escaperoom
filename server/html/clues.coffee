import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'

class CluesBox extends HTMLElement
	constructor: () ->
		super()
		@querySelector('button').onclick = @send_clue

	send_clue: (event) =>
		text = @parentNode.querySelector('input[type="text"]').value
		reponse = await fetch('/time/display', {
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				text: text
			}),
			method: 'POST'
		})

customElements.define('clues-box', CluesBox)

