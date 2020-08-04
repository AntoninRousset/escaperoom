import {SyncedContainer} from './container.mjs'

toggle_row_expand = () ->

  row = this.closest('.lrow')

  if 'opened' in row.classList
    row.classList.remove('opened')
  else
    row.classList.add('opened')


export class SyncedTree extends SyncedContainer

  constructor: () ->
    super()
    @classList.add('list')

    Object.defineProperty(this, 'lbody',
      get: () =>
        @querySelector('*.lbody')
    )

  connectedCallback: () =>
    @src = @getAttribute('src')
    super.connectedCallback()

  onadditem: (id, data) =>

    template = @lbody.querySelector('template')

    item = @apply_template(template, @lbody)
    item.setAttribute('item_id', id)

    if 'expandable' in item.classList
      for expand in item.querySelectorAll('.expand')
        expand.addEventListener('click', toggle_row_expand)

    @update_item(item, data)

  onupdateitem: (id, data) =>
    item = @lbody.querySelector("*[item_id='#{id}']")
    @update_item(item, data)

  onremoveitem: (id, data) =>
    item = @lbody.querySelector("*[item_id='#{id}']")
    item.remove()


customElements.define('synced-list', SyncedList)
