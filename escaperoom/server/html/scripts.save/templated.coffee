class Templated extends HTMLElement

  constructor: (@template=null) ->
    super()

    # query template 
    @template = @template ? @querySelector('template')
    if not @template?
      console.warn('No template given')
      return

    # query slots
    read_slot = (slot) ->
      return {
        name: slot.getAttribute('name'),
        type: slot.getAttribute('type') || 'span'
      }
    slots = @template.content.querySelectorAll('slot')
    @slots = (read_slot(slot) for slot in slots)

  # copy template class and create plugs
  apply_template: (node=this) ->

    # copy template class
    if @template.hasAttribute('class')
      node.setAttribute('class', @template.getAttribute('class'))

    # create plugs
    for slot in @slots
      node.appendChild(@create_plug(slot))
    node.attachShadow({mode: 'open'})
    node.shadowRoot.appendChild(@template.content.cloneNode(true))
    node

  # return an element base on the slot type and name
  create_plug: (slot) ->
    plug = document.createElement(slot.type)
    plug.setAttribute('slot', slot.name)
    plug

  # update all plugs
  update_plugs: (data, node=this) ->
    for slot in @slots
      @update_plug(slot.name, data, node)

  # update plug content
  update_plug: (slot_name, data, node) ->
    plug = node.querySelector('[slot=' + slot_name + ']')
    plug.textContent = data[slot]

  set_screen: (name, node=this) ->
    for screen in node.shadowRoot.querySelectorAll('.screen')
      if screen.getAttribute('name') is name
        screen.removeAttribute('hidden')
      else
        screen.setAttribute('hidden', '')

  has_screen: (name, node=this) ->
    if not node.shadowRoot?
      return false
    node.shadowRoot.querySelector('.screen[name="'+name+'"]')?

  get_screen: (node=this) ->
    @shadowRoot.querySelector('.screen:not([hidden])')



