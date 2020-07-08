import {Subscriber, fetch_html} from './communication.js'

Function::property = (prop, desc) ->
  Object.defineProperty @prototype, prop, desc


class Panel extends Subscriber

  constructor: (@name, @title) ->
    super()

    # set default class
    @classList.add('panel')

    # loading mode by default
    @setAttribute('loading', '')

  connectedCallback: () =>

    # create header, loading screen and content screen
    header = document.querySelector('#template-panel-header')
    header = header.content.cloneNode(true)
    header.querySelector('header > h1').textContent = @title
    header.querySelector('header > svg').onclick = @toggleFold
    @innerHTML = ''
    @appendChild(header)
    

  fetch_html: (url) =>
    # fetch html
    url = 'ressources/widgets/' + @name + '/' + @name + '.html'
    fetch_html(url, slow=true).then(@htmlLoadedCallback)


  # listen to the following attributes
  @property 'observedAttributes',
    get: -> ['folded']

  # callback if specified attributes are modified
  attributeChangedCallback: (name, old_value, new_value) ->
    console.log(name, ' - ', old_value, ' - ', new_value)

  # callback once the html document is loaded
  htmlLoadedCallback: (html) =>
    content = html.querySelector('template').content.cloneNode(true)
    @querySelector('.content').attachShadow({mode: 'open'}).appendChild(content)
    @removeAttribute('loading')

  toggleFold: () =>
    if @hasAttribute('folded')
      @unfold()
    else
      @fold()

  fold: () =>
    @setAttribute('folded', '')

  unfold: () =>
    @removeAttribute('folded')


export class Widget extends Panel

  constructor: (name, title) ->
    super(name, title)


class Dashboard extends HTMLElement

  constructor: () ->
    super()


