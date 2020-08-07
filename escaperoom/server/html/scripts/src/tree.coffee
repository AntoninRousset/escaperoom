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

  onnewdata: (data) =>

    newbody = document.createElement('div')
    newbody.classList.add('body')

    for key in @sort_data(data.children)
      item = @create_item(data.children[key])
      newbody.appendChild(item)

    @body = newbody

  sort_data: (data) =>
    return Object.keys(data).sort(collator.compare)

  create_item: (data) =>

    template = @body.querySelector('template')

    item = @instantiate_template(template)
    item.setAttribute('item_id', data.key)

    # add foldswitch action
    for btn in item.querySelectorAll('stamp-switch.foldswitch')
      btn.onstatechange = () ->
        row = this.closest('.row')
        if this.getAttribute('state') == 'on'
          row.setAttribute('open', '')
        else
          row.removeAttribute('open')

    @fill_slots(item, data)

    if not is_empty(data.children)
      for expand in item.querySelectorAll('.expand')
        expand.addEventListener('click', toggle_row_expand)

    extra = item.querySelector('*.children')
    for key in @sort_data(data.children)
      extra.appendChild(@create_item(data.children[key]))

    if not is_empty(data.children)
      item.classList.add('foldable')

    if @custom_item_modification?
      item = @custom_item_modification(item, data)

    return item

customElements.define('synced-tree', SyncedTree)
