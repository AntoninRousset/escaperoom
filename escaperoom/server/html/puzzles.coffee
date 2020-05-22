import {Subscriber, Container} from './monitor.js'
import {is_empty, post_control} from './monitor.js'


class PuzzlesBox extends Subscriber

  constructor: () ->
    super()
    @apply_template()
    @shadowRoot.querySelector('#puzzles-menu').onclick = (event) =>
      game_box = document.querySelector('game-box')
      game_box.current_screen = 'game'
      game_box.set_screen(game_box.current_screen)
    @subscribe()

  update: (datas) ->
    @set_screen('graph')
    @update_plugs(datas)
    @shadowRoot.querySelector('puzzles-graph').read_items(datas.states)

customElements.define('puzzles-box', PuzzlesBox)


svgns = 'http://www.w3.org/2000/svg'
class PuzzlesGraph extends Container
  constructor: () ->
    super()
    @svg = document.createElementNS(svgns, 'svg')
    @svg.setAttributeNS(null, 'style', 'width: 100%;')
    @appendChild(@svg)
    @graph = document.createElementNS(svgns, 'g')
    @graph.setAttributeNS(null, 'style', 'transform: translate(50%, 40px)')
    @svg.appendChild(@graph)

  add_item: (id, data) ->

    # check data completeness
    if not (data.position?)
      console.warn('Incomplete data', data)
      return

    # create svg shape
    if data.stype == 'rect'
      g = @create_rect(id, data)
    else if data.stype == 'circle'
      g = @create_circle(id, data)
    else
      console.warn('Invalid stype', data.stype)
      return
    
    # add onclick event
    g.onclick = (event) =>
      puzzle_info = @parentNode.parentNode.querySelector('puzzle-info')
      puzzle_info.select(id)
      @querySelectorAll(".item").forEach((e) =>
        e.removeAttributeNS(null, 'selected'))
      @querySelector(".item[item_id=\"#{id}\"]").setAttributeNS(null, 'selected', '')

    @graph.appendChild(g)

  create_circle: (id, data) ->
    g = document.createElementNS(svgns, 'g')
    g.setAttributeNS(null, 'class', 'item')
    g.setAttributeNS(null, 'item_id', id)

    circle = document.createElementNS(svgns, 'circle')
    circle.setAttributeNS(null, 'r', 16)
    g.appendChild(circle)

    label = document.createElementNS(svgns, 'text')
    label.classList.add('label')
    label.textContent = 'salut'
    label.setAttributeNS(null, 'text-anchor', 'middle')
    label.setAttributeNS(null, 'x', 0)
    label.setAttributeNS(null, 'y', 32)
    g.appendChild(label)
    return g

  create_rect: (id, data) ->

    [xmin, xmax, ymin, ymax] = data.rect_size
    [mx, my] = data.margin

    x = - 90 * mx - 16
    y = 70 * (ymin - my)
    w = 90 * (xmax - xmin + 2 * mx) + 16 + 32
    h = 70 * (ymax - ymin + 2 * my)

    g = document.createElementNS(svgns, 'g')
    g.setAttributeNS(null, 'class', 'item')
    g.setAttributeNS(null, 'item_id', id)

    rect = document.createElementNS(svgns, 'rect')
    rect.setAttributeNS(null, 'x', y)
    rect.setAttributeNS(null, 'y', x)
    rect.setAttributeNS(null, 'width', h)
    rect.setAttributeNS(null, 'height', w)
    g.appendChild(rect)

    label = document.createElementNS(svgns, 'text')
    label.classList.add('label')
    label.textContent = 'salut'
    label.setAttributeNS(null, 'text-anchor', 'start')
    label.setAttributeNS(null, 'x', y + 10)
    label.setAttributeNS(null, 'y', - 70 * mx - 24)
    g.appendChild(label)
    return g

  update_item: (id, data) ->

    # get group
    g = @get_item(id)
    if not g?
      return

    # get circle and label
    circle = g.querySelector('circle')
    label = g.querySelector('text')

    # set completed
    if data['active']
      g.setAttributeNS(null, 'active', '')
    else
      g.removeAttributeNS(null, 'active')

    # group position
    x = 70 * data['position'][1]
    y = 90 * data['position'][0]
    g.setAttributeNS(null, 'transform', "translate(#{x}, #{y})")

    # set label content
    label.textContent = data.name

  onupdated: (datas) ->
    box = @svg.getBBox()
    @svg.setAttribute('width', box.x + box.width + box.x)
    @svg.setAttribute('height', box.y + box.height + box.y)


customElements.define('puzzles-graph', PuzzlesGraph)


class PuzzleInfo extends Subscriber
  constructor: () ->
    super()
    @apply_template()
    @state = null
    @set_screen('empty')
    @transitions_list = @shadowRoot.querySelector('#state-transitions')
    @activate_button = @shadowRoot.querySelector('#state-activate')

  select: (id) ->
    @subscribe('?id='+id)

  update: (data) ->
    @update_plugs(data)

    @activate_button.onclick = (event) =>
      @activate_state(data.id)

    @transitions_list.innerHTML = ''
    for name, transition of data.transitions
      div = document.createElement('div')

      # set target
      target_name = document.createElement('span')
      target_name.innerText = transition.target.name
      div.appendChild(target_name)

      # set transition name
      trans_name = document.createElement('span')
      trans_name.innerText = transition.name
      div.appendChild(trans_name)

      # set onclick (hack)
      set_onclick = (trans_id) =>
        div.onclick = (event) =>
          console.log(trans_id)
          @force_transition(trans_id)
      set_onclick(transition.id)

      @transitions_list.appendChild(div)

    @set_screen('info')

  activate_state: (state) =>
    post_control(@loc, {action: 'activate', id: state})
  
  force_transition: (transition) =>
    post_control(@loc, {action: 'force_transition', id: transition})

  restore: () =>
    post_control(@loc, {action: 'restore'})

  set_active: (state) =>
    post_control(@loc, {action: 'set_active', state: state})


customElements.define('puzzle-info', PuzzleInfo)


class ConditionsList extends Container
  constructor: () ->
    super()

  add_item: (id, data) ->
    item = @create_item(id)
    @appendChild(item)
    item.shadowRoot.querySelector('condition-item').select(id)

customElements.define('conditions-list', ConditionsList)


class ConditionItem extends Subscriber
  constructor: () ->
    super()
    @apply_template()
    @state = null
    @shadowRoot.querySelector('div').querySelector('div').onclick = (event) =>
      @force(not @state)
    @shadowRoot.querySelector('div').querySelector('button').onclick = (event) =>
      @restore()

  select: (id) ->
    @subscribe('?id='+id)

  update: (datas) ->
    @update_plugs(datas)
    div = @shadowRoot.querySelector('div')
    button = @shadowRoot.querySelector('div').querySelector('button')
    @state = datas['state']
    if not datas.state?
      div.style.borderColor = 'orange'
    else if datas['state']
      div.style.borderColor = 'green'
    else
      div.style.borderColor = 'red'
    if datas['forced']
      button.disabled = false
    else
      button.disabled = true
    if datas['desactivated']
      div.disabled = true
      div.style.borderColor = 'gray'
    else
      div.disabled = false

  force: (state) =>
    post_control(@loc, {action: 'force', state: state})

  restore: () =>
    post_control(@loc, {action: 'restore'})


customElements.define('condition-item', ConditionItem)


class ActionsList extends Container
  constructor: () ->
    super()

  add_item: (id, data) ->
    item = @create_item(id)
    @appendChild(item)
    item.shadowRoot.querySelector('action-item').select(id)


customElements.define('actions-list', ActionsList)


class ActionItem extends Subscriber
  constructor: () ->
    super()
    @apply_template()
    @shadowRoot.querySelector('div').querySelector('div').onclick = (event) =>
      @call()
    @shadowRoot.querySelector('div').querySelector('button').onclick = (event) =>
      @abort()

  select: (id) ->
    @subscribe('?id='+id)

  update: (datas) ->
    @update_plugs(datas)
    div = @shadowRoot.querySelector('div')
    if datas['running']
      div.style.borderColor = 'green'
    else if datas['failed']
      div.style.borderColor = 'red'
    else
      div.style.borderColor = 'orange'
    if datas['desactivated']
      div.disabled = true
      div.style.borderColor = 'gray'
    else
      div.disabled = false

  call: () =>
    post_control(@loc, {action: 'call'})

  abort: () =>
    post_control(@loc, {action: 'abort'})


customElements.define('action-item', ActionItem)


