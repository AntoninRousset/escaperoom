import {TemplatedElement} from './template.mjs'


export class MultiScreenElement extends TemplatedElement

  Object.defineProperty(MultiScreenElement, 'observedAttributes', {
    get: () =>
      return TemplatedElement.observedAttributes.concat(['screen'])
  })

  constructor: (@default_screen='') ->
    super()

  @get_observed_attributes: () =>
    return ['screen']

  connectedCallback: () =>

    if not @hasAttribute('screen')
      @set_screen(@default_screen)

  attributeChangedCallback: (name, old_value, new_value) =>

    if name == 'screen'
      for screen in @querySelectorAll('.screen')

        if screen.getAttribute('name') == new_value
          screen.removeAttribute('hidden')
        else
          screen.setAttribute('hidden', '')

  set_screen: (name) =>
    if name?
      return @setAttribute('screen', name)
    @removeAttribute('screen')

  get_screen: (name) =>
    return @querySelector(".screen[name='#{name}']")
