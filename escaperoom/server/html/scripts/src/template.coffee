export class TemplatedElement extends HTMLElement

  apply_template: (template, dest, use_shadow=false) ->

    new_element = template.content.cloneNode(true)
    first_child = new_element.firstElementChild

    if not use_shadow
      dest.appendChild(new_element)
      return first_child

    dest.attachShadow({mode: 'open'})
    dest.shadowRoot.appendChild(new_element)

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

  update_item: (item, data, use_shadow=false) ->

    data = @custom_update(item, data)

    if use_shadow

      for slot in @shadowRoot.querySelectorAll('slot')
        name = slot.getAttribute('name')
        slot = dest.querySelector("*[slot='#{name}']")
        if slot?
          slot.textContent = data[name]

    else

      for slot in item.querySelectorAll('slot')
        name = slot.getAttribute('name')
        slot.innerText = data[name]

  # Used for custom item updating. The returned data is used for slot filling.
  # If null is returned, no extra item update is performed.
  custom_update: (item, data) ->
    return data
