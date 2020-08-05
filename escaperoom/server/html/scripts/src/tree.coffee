import {SyncedContainer} from './container.mjs'


export class SyncedTable extends SyncedContainer

  constructor: () ->
    super()
    @classList.add('table')

    Object.defineProperty(this, 'tbody',
      get: () =>
        @querySelector('*.tbody')
    )

  connectedCallback: () =>
    @src = @getAttribute('src')
    super.connectedCallback()

  onadditem: (id, data) =>

    template = @tbody.querySelector('template')

    item = @apply_template(template, @tbody)
    item.setAttribute('item_id', id)
    @ugpdate_item(item, data, use_shadow=false)

  onupdateitem: (id, data) =>
    item = @tbody.querySelector("*[item_id='#{id}']")
    @update_item(item, data, use_shadow=false)

  onremoveitem: (id, data) =>
    item = @tbody.querySelector("*[item_id='#{id}']")
    item.remove()


customElements.define('synced-table', SyncedTable)
