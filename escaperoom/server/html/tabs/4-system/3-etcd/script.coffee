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
