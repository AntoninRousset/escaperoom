import '/interface/scripts/list.mjs'
import '/interface/scripts/action.mjs'


export onload = (root) ->

  list = root.querySelector("synced-list")
  list.custom_update = (item, data) ->

    if data.active
      item.removeAttribute('disabled')
    else
      item.setAttribute('disabled', '')

    btn = item.querySelector('action-btn')
    if data.registered
      btn.set_screen('checked')
    else
      btn.set_screen('unchecked')

    return data

