dom_parser = new DOMParser()


# TODO to remove, only here to emulate bandwidth limitation
sleep = (ms) ->
  new Promise((resolve) -> setTimeout(resolve, ms))


export post_control = (loc, data) ->
  response = await fetch(loc, {
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data),
    method: 'POST'
  })
  datas = await response.json()
  if datas.state == 'failed'
    if datas.reason?
      throw 'failed to post control: '+datas.reason
    else
      throw 'failed to post control'
  datas.data


export fetch_html = (url, slow=false) ->

  resp = await fetch(url, {mehtod: 'GET'})

  if slow
    await sleep(Math.floor(Math.random() * 3000))

  if not resp.ok
    console.warn('Failed to fetch', url)
    return null

  return dom_parser.parseFromString(await resp.text(), 'text/html')


export class Subscriber extends HTMLElement

  event_source = null
  subscribers = []

  constructor: () ->
    super()
    @loc = ''
    @classList.add('loadable')

  event_handler = (event) ->

    console.log('-- event -->', event)

    data = JSON.parse(event.data)

    # inform all id corresponding subscribers
    for subscriber in subscribers
      if data['type'] == 'update'
        loc = data['url']

        if 'id' of data
          loc = loc + '?id=' + data['id']

        if subscriber.loc == loc
          subscriber.sync()

  subscribe: (@loc) =>

    # be sure to be unsubscribed first
    @unsubscribe()

    event_path = @loc.substring(0, @loc.lastIndexOf('/')) + '/events'
    if not event_source?
      event_source = new EventSource(event_path)
    subscribers.push(this)
    event_source.onmessage = event_handler
    @sync()

  sync: () =>
    now = new Date()
    @now = now
    loading_timeout = setTimeout(@onloading, 1000)
    response = await fetch(@loc)
    data = await response.json()
    clearTimeout(loading_timeout)
    if now is @now
      @update(data)

  unsubscribe: () ->
    for i, subscriber of subscribers
      if this is subscriber
        subscribers.splice(i, 1)

  update: (data) ->
    console.warn('Uncatched update')

  onloading: () =>
    @setAttribute('loading', '')

  onsuccess: () =>
    @removeAttribute('loading')
    @removeAttribute('error')

  onerror: () =>
    @setAttribute('error', '')
