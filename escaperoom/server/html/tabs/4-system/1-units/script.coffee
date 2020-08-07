import '/interface/scripts/list.mjs'
import '/interface/scripts/stamp.mjs'


export onload = (root) ->

  list = root.querySelector("synced-list")
  list.custom_update = (item, data) ->

    if data.active
      item.removeAttribute('disabled')
    else
      item.setAttribute('disabled', '')

    button = item.querySelector('stamp-button')
    if data.registered
      button.set_screen('checked')
    else
      button.set_screen('unchecked')

    return data

