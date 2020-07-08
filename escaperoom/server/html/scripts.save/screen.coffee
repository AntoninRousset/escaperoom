export class MultiScreenElement extends HTMLElement

  constructor: (@default_screen) ->

    super()

  Object.defineProperty(MultiScreenElement, 'observedAttributes',
                        {get: -> ['screen']})

  connectedCallback: () =>
    @setAttribute('screen', @default_screen)


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
