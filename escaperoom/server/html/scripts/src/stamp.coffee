import {MultiScreenElement} from './screen.mjs'
import {stamp_svg} from './stamp_elements.mjs'


class StampElement extends MultiScreenElement

  Object.defineProperty(StampElement, 'observedAttributes', {
    get: () =>
      return MultiScreenElement.observedAttributes.concat(['type', 'class'])
  })

  constructor: (default_screen) ->
    super(default_screen)

  connectedCallback: () =>
    super.connectedCallback()
    @classList.add('stamp')
    

  attributeChangedCallback: (name, old_value, new_value) =>

    super.attributeChangedCallback(name, old_value, new_value)

    if name == 'type' and @set_stamp_type?
      @set_stamp_type(new_value)

    if name == 'class' and @set_stamp_type?
      # if class "small" is removed or added
      if not old_value? or not new_value? or ('small' in old_value.split(' ')) != ('small' in new_value.split(' '))
        @set_stamp_type(@getAttribute('type'))


  set_stamp_type: (type) =>

    @innerHTML = ''
    
    size = if @classList.contains('small') then 'small'  else 'big'

    if type == 'ghost'
      @appendChild(stamp_svg.small.ghost.cloneNode(true))

    else if type == 'loading'
      @appendChild(stamp_svg[size].loading.cloneNode(true))

customElements.define('stamp-icon', StampElement)


class StampButtonElement extends StampElement

  connectedCallback: () =>

    super.connectedCallback()

    @addEventListener('click', (event) =>
      if not @hasAttribute('disabled') and @action?
        @action(event)
        event.stopPropagation()
    )

  set_stamp_type: (type) =>

    @innerHTML = ''
    
    size = if @classList.contains('small') then 'small' else 'big'

    if type == 'plus'
      @appendChild(stamp_svg[size].plus.cloneNode(true))

    else if type == 'plus-circle'
      @appendChild(stamp_svg[size].plus_circle.cloneNode(true))

    else if type == 'chevron'
      @appendChild(stamp_svg[size].chevron_up.cloneNode(true))

    else if type == 'check'
      @appendChild(stamp_svg[size].check.cloneNode(true))

    else if type == 'x'
      @appendChild(stamp_svg[size].x.cloneNode(true))



customElements.define('stamp-button', StampButtonElement)


class StampSwitchElement extends StampButtonElement

  Object.defineProperty(StampSwitchElement, 'observedAttributes', {
    get: () =>
      return StampButtonElement.observedAttributes.concat(['state'])
  })

  connectedCallback: () =>

    super.connectedCallback()

    if not @hasAttribute('state')
      @setAttribute('state', 'off')

  action: (event) =>
    if not @hasAttribute('state') or @getAttribute('state') == 'off'
      @setAttribute('state', 'on')
    else
      @setAttribute('state', 'off')

  attributeChangedCallback: (name, old_value, new_value) =>

    super.attributeChangedCallback(name, old_value, new_value)

    if name == 'state' and @onstatechange?
      @onstatechange(new_value)

  set_stamp_type: (type) =>

    @innerHTML = ''
    
    size = if @classList.contains('small') then 'small'  else 'big'

    if type == 'triangle'
      @appendChild(stamp_svg[size].triangle_right.cloneNode(true))

    else if type == 'chevron'
      @appendChild(stamp_svg[size].chevron_up.cloneNode(true))


customElements.define('stamp-switch', StampSwitchElement)
