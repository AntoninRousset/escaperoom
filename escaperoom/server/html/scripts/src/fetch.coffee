import {MultiScreenElement} from './screen.mjs'
import {sleep} from './utils.mjs'


dom_parser = new DOMParser()


export fetch_data = (url, data_type, emul_slow=false) ->

    resp = await fetch(url, {method: 'GET'})

    if emul_slow
      await sleep(Math.floor(Math.random() * 3000))

    if not resp.ok
      console.error('Failed to fetch', url)
      return null

    if data_type == 'json'
      return JSON.parse(await resp.text())

    else if data_type == 'text'
      return await resp.text()

    else if data_type == 'html'
      return resp.text().then(
        (text) -> dom_parser.parseFromString(text, 'text/html')
      )

    else
      console.error("Invalid data_type #{data_type} during fetching")


export class FetchedElement extends MultiScreenElement

  Object.defineProperty(FetchedElement, 'observedAttributes', {
    get: () =>
      return MultiScreenElement.observedAttributes.concat(['src'])
  })

  constructor: (@data_type='json', @emul_slow=false) ->

    super()
    @_data = null

    Object.defineProperty(this, 'data',
      get: () ->
        return @_data
      set: (data) ->
        @onnewdata(data)
        @_data = data
    )

    Object.defineProperty(this, 'src',
      get: () ->
        return @getAttribute('src')
      set: (src) ->
        return @setAttribute('src', src)
    )

  onloading: () =>
    @set_screen('loading')

  onnewdata: (data) =>
    console.warn('Unused data', data)

  load_from_src: () =>
    @load_from(@src)

  load_from: (src) =>

    loading_timeout = setTimeout(@onloading, 3000)

    try
      now = new Date()
      @now = now

      data = await fetch_data(src, @data_type, @emul_slow)

      if now is @now
        @data = data

    finally
      clearTimeout(loading_timeout)
      @set_screen('main')

  attributeChangedCallback: (name, old_value, new_value) =>
    
    super.attributeChangedCallback(name, old_value, new_value)

    if name == 'src'
      @load_from(new_value)
