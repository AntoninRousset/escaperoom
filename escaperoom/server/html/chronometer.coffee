import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'

class ChronometerDial extends Subscriber
	constructor: () ->
		super()
		@tick_period = 250
		@subscribe()

	update: (data) =>
		@sync_time = Date.now()
		@time = data['time']
		@speed = data['speed']
		@tick()
		if @speed != 0
			@clock = setInterval(@tick, @tick_period)
		else if @clock?
			clearInterval(@clock)

	tick: () =>
		if @time?
			elapsed = Date.now() - @sync_time
			@textContent = @time_to_string(@time + @speed*elapsed)
		else
			@textContent = @time_to_string(0)

	time_to_string: (time) ->
		h = String(Math.floor(time / 3600000))
		m = String(Math.floor(time / 60000) % 60)
		s = String(Math.floor(time / 1000) % 60)
		h.padStart(2, '0')+':'+m.padStart(2, '0')+':'+s.padStart(2, '0')

customElements.define('chronometer-dial', ChronometerDial)

