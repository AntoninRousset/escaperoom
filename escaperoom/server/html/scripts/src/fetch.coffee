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

  constructor: (@src=null, @data_type='json', @emul_slow=false) ->

    super()
    @_data = null

    Object.defineProperty(this, 'data',
      get: () ->
        return @_data
      set: (data) ->
        @onnewdata(data)
        @_data = data
    )

  onloading: () =>
    @set_screen('loading')

  onnewdata: (data) =>
    console.warn('Unused data', data)

  load_from_src: () =>
    await @load_from(@src)

  load_from: (url) =>

    now = new Date()
    @now = now

    loading_timeout = setTimeout(@onloading, 1000)
    data = await fetch_data(url, @data_type, @emul_slow)
    clearTimeout(loading_timeout)

    if now is @now
      @data = data
