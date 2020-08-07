export class TemplatedElement extends HTMLElement

  Object.defineProperty(TemplatedElement, 'observedAttributes', {
    get: () =>
      return []
  })

  instantiate_template: (template, use_shadow=false) ->

    new_element = template.content.cloneNode(true)
    first_child = new_element.firstElementChild

    if not use_shadow
      return first_child

    # create all plugs
    # TODO use '> slot'
    slots = template.content.querySelectorAll('slot')
    slots = (slot.getAttribute('name') for slot in slots)

    for slotname in slots
      first_child.insertBefore(@create_plug(slotname), first_child.childNodes[0])

    return first_child

  create_plug: (slotname) ->
    span = document.createElement('span')
    span.setAttribute('slot', slotname)
    return span

  fill_slots: (item, data, use_shadow=false) ->

    if use_shadow

      for slot in @shadowRoot.querySelectorAll('slot')
        name = slot.getAttribute('name')
        slot = dest.querySelector("*[slot='#{name}']")
        if slot?
          if typeof(data[name]) == 'object'
            slot.textContent = JSON.stringify(data[name], null, ' ')
          else
            slot.textContent = data[name]

    else

      for slot in item.querySelectorAll('slot')
        name = slot.getAttribute('name')
        if typeof(data[name]) == 'object'
          slot.innerText = JSON.stringify(data[name], null, ' ')
        else
          slot.innerText = data[name]

  attributeChangedCallback: (name, old_value, new_value) =>
