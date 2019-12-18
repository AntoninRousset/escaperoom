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
		@running = data['running']
		@tick()
		if @running
			@clock = setInterval(@tick, @tick_period)
		else if @clock?
			clearInterval(@clock)

	tick: () =>
		if @time?
			if @running
				@textContent = @time_to_string(@time + Date.now() - @sync_time)
			else
				@textContent = @time_to_string(@time)
		else
			@textContent = @time_to_string(0)

	time_to_string: (time) ->
		h = String(Math.floor(time / 3600000))
		m = String(Math.floor(time / 60000) % 60)
		s = String(Math.floor(time / 1000) % 60)
		h.padStart(2, '0')+':'+m.padStart(2, '0')+':'+s.padStart(2, '0')

customElements.define('chronometer-dial', ChronometerDial)

