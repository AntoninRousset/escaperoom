import '/interface/scripts/tree.mjs'
import '/interface/scripts/stamp.mjs'


export onload = (root) ->

  tree = root.querySelector('*.etcdtree')
  tree.custom_item_modification = (item, data) =>

    if not data.node?
      item.classList.add('ghost')
      return item

    item.classList.add('selectable')
    item.addEventListener('click', (event) =>
      for row in tree.querySelectorAll('.row')
        row.removeAttribute('selected')
      row = event.target.closest('.row')
      row.setAttribute('selected', '')

      # set etcd inspector
      src = 'etcd' + row.getAttribute('item_id') + '?with_values'
      tree.closest('.etcdnav').querySelector('.etcdinspector').src = src
    )

    return item
