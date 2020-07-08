import {TemplatedElement} from './template.mjs'


export class MultiScreenElement extends TemplatedElement

  constructor: (@default_screen) ->
    super()

  Object.defineProperty(MultiScreenElement, 'observedAttributes',
                        {get: -> ['screen']})

  connectedCallback: () =>

    if not @hasAttribute('screen')
      @set_screen(@default_screen)

  attributeChangedCallback: (name, oldValue, newValue) =>

    for screen in @querySelectorAll('.screen')

      if screen.getAttribute('name') == newValue
        screen.removeAttribute('hidden')
      else
        screen.setAttribute('hidden', '')

  set_screen: (name) =>
    @setAttribute('screen', name)

  get_screen: (name) =>
    return @querySelector(".screen[name='#{name}']")
