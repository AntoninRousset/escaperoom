import {SyncedContainer} from './container.mjs'
import {is_empty} from './utils.mjs'

toggle_row_expand = () ->

  row = this.closest('.lrow')

  if 'opened' in row.classList
    row.classList.remove('opened')
  else
    row.classList.add('opened')


export class SyncedList extends SyncedContainer

  constructor: () ->
    super()
    @classList.add('list')

  connectedCallback: () =>
    @src = @getAttribute('src')
    super.connectedCallback()

  get_body: () =>
    return @querySelector('*.lbody')

  onnewdata: (data) =>

    if @sortData?
      data = @sortData(data)

    newbody = document.createElement('div')
    newbody.classList.add('lbody')

    for item_id, item_data of data
      item = @create_item(item_id, item_data)
      newbody.appendChild(item)

    @body = newbody

  create_item: (item_id, item_data) =>

    template = @body.querySelector('template')

    item = @instantiate_template(template, @body)
    item.setAttribute('item_id', item_id)

    @fill_slots(item, item_data)

    if 'expandable' in item.classList
      for expand in item.querySelectorAll('.expand')
        expand.addEventListener('click', toggle_row_expand)

    return item

customElements.define('synced-list', SyncedList)
