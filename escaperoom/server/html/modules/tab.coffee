import {fetch_html} from './communication.js'

Function::property = (prop, desc) ->
  Object.defineProperty @prototype, prop, desc


class TabsNav extends HTMLElement

  constructor: () ->
    super()

    # set default class
    @classList.add('loadable')

    # set loading mode by default
    @setAttribute('loading', '')

    window.addEventListener('hashchange', @select_from_hash)
    window.addEventListener('load', @update)

  connectedCallback: () =>

    # create loading screen
    cls = customElements.get('loading-animation')
    @appendChild(new cls())

    # create content screen
    content = document.createElement('div')
    content.classList.add('content')
    @appendChild(content)

  update: (data) =>

    tabs = [
      {
      name: 'dashboard',
      title: 'Dashboard',
      },
      {
      name: 'story',
      title: 'Story',
      },
      {
      name: 'cameras',
      title: 'Cameras',
      },
      {
      name: 'room',
      title: 'Room',
      },

    ]

    content = @querySelector('.content')

    for tab in tabs

      a = document.createElement('a')
      a.href = '#' + tab.name

      # add svg icon
      svg = await fetch_html('/ressources/tabs/' + tab.name + '/tab.svg')
      svg = svg.querySelector('svg')
      a.appendChild(svg)

      # add title
      p = document.createElement('p')
      p.textContent = tab.title
      a.appendChild(p)

      content.appendChild(a)

    @select_from_hash()
    @removeAttribute('loading')

  select_from_hash: () =>
    @select(location.hash.substr(1))

  select: (tab) =>

    # remove all selected
    for a in @querySelectorAll('a')
      a.removeAttribute('selected')

    a = @querySelector('a[href="#' + tab + '"]')
    if not a
      a = @querySelector('a')
      # remove hash
      history.pushState('', document.title, location.pathname + location.search)

    # select
    name = a.getAttribute('href').substr(1)
    a.setAttribute('selected', '')
    target = a.getAttribute('target')
    container = document.getElementById(@getAttribute('for'))
    container.innerHTML = ''
    cls = customElements.get('tab-' + name)
    e = new cls()
    container.appendChild(e)


class Tab extends HTMLElement

  constructor: () ->
    super()

    # set default class
    @classList.add('tab')


class DashboardTab extends Tab

  constructor: () ->
    super('dashboard', 'Dashboard')
    @classList.add('columns')

  connectedCallback: () =>
    for w in ['timer', 'game', 'story', 'clues', 'cameras']
      cls = customElements.get('widget-' + w)
      e = new cls()
      @appendChild(e)


class StoryTab extends Tab

  constructor: () ->
    super('story', 'Story')


class CamerasTab extends Tab

  constructor: () ->
    super('cameras', 'Cameras')


class CluesTab extends Tab

  constructor: () ->
    super('clues', 'Clues')


class RoomTab extends Tab

  constructor: () ->
    super('room', 'Room')


customElements.define('tabs-nav', TabsNav)
customElements.define('tab-dashboard', DashboardTab)
customElements.define('tab-story', StoryTab)
customElements.define('tab-cameras', CamerasTab)
customElements.define('tab-clues', CluesTab)
customElements.define('tab-room', RoomTab)
