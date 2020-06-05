import {Subscriber, Container} from './monitor.js'
import {is_empty, post_control} from './monitor.js'


class CluesBox extends Subscriber

  constructor: () ->
    super()
    @apply_template()
    @shadowRoot.querySelector('button').onclick = @send_clue
    @clues_list = @shadowRoot.querySelector('ul')
    @subscribe()
    @textarea = @shadowRoot.querySelector('textarea')
    @length_warning = 6
    @textarea.oninput = (event) =>
      if @length_warning > 0 and @textarea.value.length >= @length_warning
        @textarea.classList.add('length-warning')
      else
        @textarea.classList.remove('length-warning')

  update: (datas) ->
    @update_plugs(datas)
    @clues_list.read_items(datas.messages)
    @length_warning = datas.length_warning

  send_clue: (event) =>
    text = event.target.parentNode.querySelector('textarea').value
    post_control('/display', {action: 'clue', text: text})

customElements.define('clues-box', CluesBox)


class CluesList extends Container

  read_items: (datas) ->
    @innerHTML = ''
    @textarea = @parentNode.querySelector('textarea')
    for id, msg of datas
      @add_item(id, msg)

  add_item: (id, msg) ->
    li = document.createElement('li')
    li.innerText = msg
    li.onclick = (event) =>
      @textarea.value = event.originalTarget.innerText
    @appendChild(li)

customElements.define('clues-list', CluesList)
