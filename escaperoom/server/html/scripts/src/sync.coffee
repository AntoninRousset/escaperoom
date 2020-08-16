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
        subscriber.onsyncevent(event)

  Object.defineProperty(SyncedElement, 'observedAttributes', {
    get: () =>
      return FetchedElement.observedAttributes.concat(['eventsrc', 'eventtype', 'paused'])
  })

  constructor: (data_type, emul_slow) ->
    super(data_type, emul_slow)
    @postponed_syncevents = []

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

  onsyncevent: (event) =>

    # if paused, add event to be retriggered once not paused anymore
    if @hasAttribute('paused')
      return @postponed_syncevents.push(event)

    # load new content
    if @src?
      @load_from(@src)
    else
      @set_screen('empty')

  onnewdata: (data) =>
    @fill_slots(this, data)
    @set_screen('main')

  attributeChangedCallback: (name, old_value, new_value) =>
    
    super.attributeChangedCallback(name, old_value, new_value)

    # change in the event subscription
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

    # paused
    if name == 'paused'

      # if not paused anymore, trigger buffered syncevent
      if not new_value?

        # postponed_syncevents array is copied to allow @onsyncevent
        # to modify it
        postponed_syncevents = @postponed_syncevents.slice()
        @postponed_syncevents = []
        for event in postponed_syncevents
          @onsyncevent(event)


customElements.define('synced-element', SyncedElement)
