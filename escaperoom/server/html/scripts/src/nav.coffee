import {FetchedElement, fetch_data} from './fetch.mjs'


class TabNav extends FetchedElement

  constructor: () ->

    super('interface/tabs', 'json')

    # set default class
    @classList.add('loadable')

    # set loading mode by default
    @setAttribute('loading', '')

  connectedCallback: () =>

    super.connectedCallback()

    ## create loading screen
    #cls = customElements.get('loading-animation')
    #@appendChild(new cls())

    ## create content screen
    content = document.createElement('div')
    content.classList.add('content')
    @appendChild(content)

    @load_from_src()

  onnewdata: (data) =>

    main_screen = @get_screen('main')
    main_screen.innerHTML = ''

    for group in data

      group_div = document.createElement('div')
      group_h1 = document.createElement('h1')
      group_h1.innerText = group.name
      group_div.appendChild(group_h1)

      # TODO all svg could be fetched in parallel
      # TODO add svg data_type in fetch_data

      for tab in group.tabs

        a = document.createElement('a')
        a.href = '#' + tab.id

        # add svg icon
        svg = await fetch_data("/interface/tabs/#{tab.id}/icon", 'html')
        svg = svg.querySelector('svg')
        a.appendChild(svg)

        # add title
        p = document.createElement('p')
        p.textContent = tab.name
        a.appendChild(p)

        group_div.appendChild(a)

      main_screen.appendChild(group_div)

    @set_screen('main')

    window.addEventListener('hashchange', @select_from_hash)
    @select_from_hash()

  select_from_hash: () =>
    @select(location.hash.substr(1))

  select: (tab_id) =>

    # remove all selected
    for a in @querySelectorAll('a')
      a.removeAttribute('selected')

    a = @querySelector('a[href="#' + tab_id + '"]')
    if not a
      tab_id = @querySelector('a').getAttribute('href').substr(1)
      location.hash = tab_id
    else
      a.setAttribute('selected', '')


class TabContent extends FetchedElement

  constructor: () ->

    super()

    window.addEventListener('hashchange', @select_from_hash)
    window.addEventListener('load', @select_from_hash)

    @get_screen('main').attachShadow({mode: 'open'})

  select_from_hash: () =>
    @select(location.hash.substr(1))

  select: (tab_id) =>

    if not tab_id
      return

    # coffeescript dynamic import doesn't seem mature, using pure JS instead
    module_url = "/interface/tabs/#{tab_id}/script"
    `let m = await import(module_url)`

    html = await fetch_data("interface/tabs/#{tab_id}/content", 'text')

    main_screen = @get_screen('main')
    main_screen.shadowRoot.innerHTML = html

    if m.onload?
      m.onload(main_screen.shadowRoot)

    @set_screen('main')



customElements.define('tab-nav', TabNav)
customElements.define('tab-content', TabContent)
