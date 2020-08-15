import {FetchedElement} from './fetch.mjs'

export class SyncedElement extends FetchedElement

  subscriptions = []
  event_source = new EventSource('events')
  event_source.onmessage = (event) ->

    data = JSON.parse(event.data)

    if data['type'] == 'update'
      event_src = data['src']

    for sub in subscriptions
      subscriber = sub[0]
      filter = sub[1]
      if filter(data)
        subscriber.load_from(subscriber.src)

  Object.defineProperty(SyncedElement, 'observedAttributes', {
    get: () =>
      return FetchedElement.observedAttributes.concat(['eventsrc', 'eventtype'])
  })

  disconnectedCallback: () =>
    @unsubscribe()

  subscribe: (filter) ->

    if typeof(filter) == 'string'
      subscriptions.push([this, (event) =>
        event.src == filter
      ])

    else if typeof(filter) == 'function'
      subscriptions.push([this, filter])

    else
      log.error('Invalid filter', filter)

  unsubscribe: () ->
    subscriptions = subscriptions.filter((x) => x[0] is not this)

  onnewdata: (data) =>
    @fill_slots(this, data)
    @set_screen('main')

  attributeChangedCallback: (name, old_value, new_value) =>
    
    super.attributeChangedCallback(name, old_value, new_value)

    if name in ['src', 'eventsrc', 'eventtype']

      if not @hasAttribute('eventsrc') and not @hasAttribute('eventtype')
        @subscribe(@src)
      else
        @subscribe((event) =>

          if @hasAttribute('eventsrc') and event.src != @getAttribute('eventsrc')
            return false

          if @hasAttribute('eventtype') and not event.type.join('.').startsWith(@getAttribute('eventtype'))
            return false
     
          return true
        )

customElements.define('synced-element', SyncedElement)
