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
    @shadowRoot.querySelector('puzzles-graph').read_items(datas.conditions)

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
    if not (data.row? or data.col?)
      return
  
    # create group filled with a circle and text
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

    g.onclick = (event) =>
      puzzle_info = @parentNode.parentNode.querySelector('puzzle-info')
      puzzle_info.select(id)
      @querySelectorAll(".item").forEach((e) =>
        e.removeAttributeNS(null, 'selected'))
      @querySelector(".item[item_id=\"#{id}\"]").setAttributeNS(null, 'selected', '')

    @graph.appendChild(g)

  update_item: (id, data) ->

    # get group
    g = @get_item(id)
    if not g?
      return

    # get circle and label
    circle = g.querySelector('circle')
    label = g.querySelector('text')

    # set completed
    if data['state']
      g.setAttributeNS(null, 'completed', '')
    else
      g.removeAttributeNS(null, 'completed')

    # set desactivated
    if data['desactivated']
      g.setAttributeNS(null, 'desactivated', '')
    else
      g.removeAttributeNS(null, 'desactivated')

    # group position
    x = 50 * data['col']
    y = 90 * data['row']
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
    @shadowRoot.querySelector('#puzzle-complete').onclick = (event) =>
      @set_force(true)
    @shadowRoot.querySelector('#puzzle-uncomplete').onclick = (event) =>
      @set_force(false)
    @shadowRoot.querySelector('#puzzle-restore').onclick = @restore
    @shadowRoot.querySelector('#puzzle-activate').onclick = (event) =>
      @set_active(true)
    @shadowRoot.querySelector('#puzzle-desactivate').onclick = (event) =>
      @set_active(false)
    @set_screen('empty')
    @conditions_list = @shadowRoot.querySelector('conditions-list')
    @actions_list = @shadowRoot.querySelector('actions-list')

  select: (id) ->
    @subscribe('?id='+id)

  update: (data) ->
    @update_plugs(data)
    if data['state']
      @shadowRoot.querySelector('#puzzle-complete').hidden = true
      @shadowRoot.querySelector('#puzzle-uncomplete').hidden = false
    else
      @shadowRoot.querySelector('#puzzle-complete').hidden = false
      @shadowRoot.querySelector('#puzzle-uncomplete').hidden = true
    if data['forced']
      @shadowRoot.querySelector('#puzzle-complete').hidden = true
      @shadowRoot.querySelector('#puzzle-uncomplete').hidden = true
      @shadowRoot.querySelector('#puzzle-restore').hidden = false
    else
      @shadowRoot.querySelector('#puzzle-restore').hidden = true
    if data['desactivated']
      @shadowRoot.querySelector('#puzzle-activate').hidden = false
      @shadowRoot.querySelector('#puzzle-desactivate').hidden = true
    else
      @shadowRoot.querySelector('#puzzle-activate').hidden = true
      @shadowRoot.querySelector('#puzzle-desactivate').hidden = false
    @conditions_list.read_items(data.siblings)
    @actions_list.read_items(data.actions)
    @set_screen('info')

  set_force: (state) =>
    post_control(@loc, {action: 'force', state: state})

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


