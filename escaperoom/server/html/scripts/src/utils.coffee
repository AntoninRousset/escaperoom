export is_empty = (obj) ->
	for key of obj
		return false
	return true


export sleep = (ms) ->
  new Promise((resolve) -> setTimeout(resolve, ms))
