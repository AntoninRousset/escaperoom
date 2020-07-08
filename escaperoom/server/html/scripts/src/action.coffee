import {MultiScreenElement} from './screen.mjs'


class ActionElement extends MultiScreenElement

  constructor: (default_screen) ->

    super(default_screen)
    @addEventListener('click', @onclick)

  onclick: () =>
    console.log('click', this)

customElements.define('action-btn', class extends ActionElement
  
  constructor: () ->
    super('loading')

)
