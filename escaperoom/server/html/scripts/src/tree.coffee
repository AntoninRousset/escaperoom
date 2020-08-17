import {SyncedContainer} from './container.mjs'
import {is_empty} from './utils.mjs'


collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'})


export class SyncedTree extends SyncedContainer

  constructor: () ->
    super()
    @classList.add('tree')

  connectedCallback: () =>
    @src = @getAttribute('src')
    super.connectedCallback()

    # add create item action
    for btn in @querySelectorAll('.foot stamp-button.create')
      console.log('-->', btn)
      btn.action = @foot_button_create_action

  onnewdata: (data) =>

    newbody = document.createElement('div')
    newbody.classList.add('body')

    # copy templates
    for template in @body.querySelectorAll('template')
      newbody.appendChild(template.cloneNode(true))

    for key in @sort_data(data.children)
      item = @create_item(data.children[key])
      newbody.appendChild(item)

    @body = newbody

  sort_data: (data) =>
    return Object.keys(data).sort(collator.compare)

  create_item: (data) =>

    template = @body.querySelector('template.normalrow')

    item = @instantiate_template(template)
    item.setAttribute('item_id', data.key)

    @fill_slots(item, data)
    @setup_row_selection(item)

    # add foldswitch action
    for btn in item.querySelectorAll('stamp-switch.foldswitch')
      btn.onstatechange = @foldswitch_onstatechange

    # add create item action
    for btn in item.querySelectorAll('stamp-button.create')
      btn.action = @button_create_action

    # add create item action
    for btn in item.querySelectorAll('stamp-button.delete')
      btn.action = @button_delete_action

    extra = item.querySelector('*.children')
    for key in @sort_data(data.children)
      extra.appendChild(@create_item(data.children[key]))

    if not is_empty(data.children)
      item.classList.add('foldable')

    if @custom_item_modification?
      item = @custom_item_modification(item, data)

    return item

  onbeforeelementupdated: (from_element, to_element) =>

    # skip if customElement
    if from_element.classList.contains('stamp')
      return false

    if from_element.classList.contains('row')

      # keep row open
      if from_element.hasAttribute('open')
        to_element.setAttribute('open', '')

      # keep row selected
      if from_element.hasAttribute('selected')
        to_element.setAttribute('selected', '')

  setup_row_selection: (row) =>

    # add selection action (on the row itself not the children)
    rowcontent = row.querySelector(':scope > div:not(.children)')
    rowcontent.addEventListener('click', (event) =>

      if 'selectable' not in row.classList
        return

      for r in @body.querySelectorAll('.row')

        if r is row
          if not r.hasAttribute('selected')
            @onrowselect? and @onrowselect(r)
            r.setAttribute('selected', '')

        else
          if r.hasAttribute('selected')
            @onrowunselect? and @onrowunselect(r)
            r.removeAttribute('selected')

      event.stopPropagation()
    )

  foldswitch_onstatechange: () ->

    row = @closest('.row')
    if @getAttribute('state') == 'on'
      row.setAttribute('open', '')
    else
      row.removeAttribute('open')

  button_create_action: () ->

    row = this.closest('.row')
    tree = row.closest('synced-tree')
    children = row.querySelector('.children')
    template = tree.body.querySelector('template.creationrow')

    creationrow = tree.instantiate_template(template)
    children.appendChild(creationrow)

    row.classList.add('foldable')
    row.querySelector('stamp-switch.foldswitch').setAttribute('state', 'on')

    input = row.querySelector('*[contenteditable]')
    input.addEventListener('keydown', (event) =>

      # prevent illegal characters
      if event.key in ['*', ',']
        event.preventDefault()

      if event.key == 'Escape'
        input.blur()

      if event.key == 'Enter'
        event.preventDefault()

        content = input.innerText.trim()
        if not content
          return
        
        item_id = row.getAttribute('item_id')
        etcd_key = "#{item_id}/#{content}"

        response = await fetch('etcd' + etcd_key, {
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(null)
          method: 'PUT'
        })

      tree.removeAttribute('paused')
    )

    input.addEventListener('focus', (event) =>
      tree.setAttribute('paused', '')
    )

    input.addEventListener('blur', (event) =>
      tree.onnewdata(tree.data)
      tree.removeAttribute('paused')
    )
    
    input.focus()

  foot_button_create_action: () ->

    row = @closest('.row')
    tree = row.closest('synced-tree')
    input = row.querySelector('*[contenteditable]')
    input.addEventListener('keydown', (event) =>

      # prevent illegal characters
      if event.key in ['*', ',']
        event.preventDefault()

      if event.key == 'Escape'
        input.blur()

      if event.key == 'Enter'
        event.preventDefault()

        content = input.innerText.trim()
        if not content
          return
        
        etcd_key = "/#{content}"

        response = await fetch('etcd' + etcd_key, {
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(null)
          method: 'PUT'
        })

        input.blur()
    )

    input.addEventListener('blur', (event) =>
      row.set_screen('button')
    )

    input.innerText = ''
    row.set_screen('creation')
    input.focus()

  button_delete_action: (event) ->

    console.log('DELETE')

    row = @closest('.row')
    item_id = row.getAttribute('item_id')
    etcd_key = "#{item_id}/**"

    response = await fetch('etcd' + etcd_key, {
      headers: {'Content-Type': 'application/json'},
      method: 'DELETE'
    })

    console.log('DELETE', response)


customElements.define('synced-tree', SyncedTree)
