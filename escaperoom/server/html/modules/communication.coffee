dom_parser = new DOMParser()

sleep = (ms) ->
  new Promise((resolve) -> setTimeout(resolve, ms))

export fetch_html = (url, slow=false) ->

  resp = await fetch(url, {mehtod: 'GET'})

  if slow
    await sleep(Math.floor(Math.random() * 3000))

  if not resp.ok
    console.warn('Failed to fetch', url)
    return null

  return dom_parser.parseFromString(await resp.text(), 'text/html')
 
