import {SyncedElement} from './sync.mjs'
import {is_empty} from './utils.mjs'
import './libs/morphdom.js'

export class SyncedContainer extends SyncedElement

  constructor: () ->

    super()

    Object.defineProperty(this, 'body',
      get: () =>
        return @get_body()
      set: (newbody) =>
        morphdom(@body, newbody,

          getNodeKey: (node) =>
            try
              return node.getAttribute('item_id')

          onBeforeElUpdated: (from_element, to_element) =>
            if @onBeforeElementUpdated?
              @onBeforeElementUpdated(from_element, to_element)
        )
    )

  get_body: () =>
    return @querySelector('*.body')
