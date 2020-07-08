import {SyncedElement} from './sync.mjs'
import {is_empty} from './utils.mjs'

export class SyncedContainer extends SyncedElement

  onnewdata: (data) =>

    # remove items
    if @data?
      for id, _ of @data

        if id not of data
          try
            @onremoveitem(id)
          catch e
            console.warn('Failed to remove item', id, e)

    if is_empty(data) and @onempty?
      return @onempty()

    # update and add items
    for id, item_data of data

      if not @data? or id not of @data
        try
          @onadditem(id, item_data)
        catch e
          console.warn('Failed to add item', id, e)

      else
        try
          @onupdateitem(id, item_data)
        catch e
          console.warn('Failed to update item', id, e)


  onadditem: (id, data) =>
    console.warn('onadditem not implemented ')

  onupdateitem: (id) =>
    console.warn('onupdateitem not implemented ')

  onremoveitem: (id, data) =>
    console.warn('onremoveitem not implemented ')
