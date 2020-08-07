import {FetchedElement} from './fetch.mjs'

export class SyncedElement extends FetchedElement

  subscriptions = []
  event_source = new EventSource('events')
  event_source.onmessage = (event) ->

    data = JSON.parse(event.data)

    if data['type'] == 'update'
      event_src = data['src']

    for subscriber, filter of subscriptions
      if filter(data)
        subscriber.load_from_src()

  disconnectedCallback: () =>
    @unsubscribe()

  subscribe: (filter) ->

    if typeof(filter) == 'string'
      subscriptions[this] = (event) =>
        event.src == filter

    else if typeof(filter) == 'function'
      subscriptions[this] = filter

    else
      log.error('Invalid filter', filter)

  unsubscribe: () ->
    delete subscriptions[this]

  onnewdata: (data) =>
    console.log('new data:', data)
    @fill_slots(this, data)

  attributeChangedCallback: (name, old_value, new_value) =>
    
    super.attributeChangedCallback(name, old_value, new_value)

    if name == 'src'
      @subscribe(@src)

customElements.define('synced-element', SyncedElement)
