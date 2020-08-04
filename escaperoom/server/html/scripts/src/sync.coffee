import {FetchedElement} from './fetch.mjs'

export class SyncedElement extends FetchedElement

  subscribers = []
  event_source = new EventSource('events')
  event_source.onmessage = (event) ->

    data = JSON.parse(event.data)

    if data['type'] == 'update'
      src = data['url']

    console.log('>', data)

    for subscriber in subscribers
      if subscriber.src == src
        subscriber.load_from_src()

  connectedCallback: () =>
    super.connectedCallback()

    if @src?
      @subscribe(@src)
      @load_from_src()

  disconnectedCallback: () =>
    @unsubscribe()

  subscribe: () ->

    # avoid subscribing twice
    @unsubscribe()

    subscribers.push(this)

  unsubscribe: () ->
    index = subscribers.indexOf(this)

    if index > -1
      subscribers.splice(index, 1)
