import '/interface/scripts/tree.mjs'
import '/interface/scripts/stamp.mjs'


export onload = (root) ->

  tree = root.querySelector('*.etcdtree')
  tree.custom_item_modification = (item, data) =>

    # if node doesn't exist in the etcd tree, mark it as ghost
    if not data.node?
      item.classList.add('ghost')
      item.classList.remove('selectable')

    return item

  inspector = tree.closest('.etcdnav').querySelector('.etcdinspector')
  tree.onrowselect = (row) =>
    # set etcd inspector
    src = 'etcd' + row.getAttribute('item_id') + '?with_values'
    inspector.src = src

  # double click on node value to modify it
  inspector.querySelector('.nodevalue').addEventListener('click', (event) =>

    # accept double-click only
    if event.detail != 2
      return

    input = event.target.closest('.nodevalue').querySelector('td:last-child')
    inspector = input.closest('.etcdinspector')

    input.addEventListener('keydown', (event) =>

      # prevent illegal characters
      if event.key in ['*', ',']
        event.preventDefault()

      if event.key == 'Escape'
        input.blur()

      if event.key == 'Enter'
        event.preventDefault()

        content = input.innerText.trim()
        if not content
          return
        
        etcd_key = inspector.querySelector('.nodekey td:last-child').innerText

        response = await fetch('etcd' + etcd_key, {
          headers: {'Content-Type': 'application/json'},
          body: input.innerText.trim()
          method: 'PUT'
        })
        
        input.removeAttribute('contentEditable')

      tree.removeAttribute('paused')
    )

    input.addEventListener('focus', (event) =>
      inspector.setAttribute('paused', '')
    )

    input.addEventListener('blur', (event) =>
      console.log('blur', inspector.data)
      inspector.onnewdata(inspector.data)
      inspector.removeAttribute('paused')
    )

    input.setAttribute('contentEditable', '')
    input.focus()
    
  )
