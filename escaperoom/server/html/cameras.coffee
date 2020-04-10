import {Subscriber, Container} from './monitor.js'
import {is_empty, post_control} from './monitor.js'


class CamerasBox extends Subscriber
	constructor: () ->
		super()
		@apply_template()
		@cameras_list = @shadowRoot.querySelector('cameras-list')
		@subscribe()
		@onmouseover = (event) ->
			@cameras_list.setAttribute('visible', 'true')
		@onmouseout = (event) ->
			@cameras_list.setAttribute('visible', 'false')

	update: (datas) ->
		@update_plugs(datas)
		@cameras_list.read_items(datas.cameras)
		if is_empty(datas.cameras)
			@set_screen('empty')
		else
			@set_screen('main')


customElements.define('cameras-box', CamerasBox)


class CamerasList extends Container
	constructor: () ->
		super()

	add_item: (id, data) ->
		item = @create_item(id)
		item.onclick = (event) =>
			camera = item.shadowRoot.querySelector('camera-video')
			bigscreen = document.querySelector('cameras-box').shadowRoot.getElementById('bigscreen')
			bigscreen.srcObject = camera.video.srcObject
			await bigscreen.play()

		@appendChild(item)
		item.shadowRoot.querySelector('camera-video').start(null, '?id='+id)

customElements.define('cameras-list', CamerasList)


class CameraVideo extends HTMLElement
	constructor: () ->
		super()
		@video = @create_video()
		try
			@pc = @create_pc()
		catch error
			@set_screen(error)

	create_pc: () ->
		config = {
			sdpSementics: 'unified-plan'
		}
		pc = new RTCPeerConnection()
		pc.onnegotiationneeded = (event) => @negotiate()
		pc.onicegatheringstatechange = (event) =>
			if pc.iceGatheringState is 'complete'
				@send_offer()
		pc.ontrack = @got_tracks
		pc

	create_video: () ->
		video = document.createElement('video')
		video.muted = true
		video.autoplay = true
		video.textContent = @textContent
		@textContent = null
		@appendChild(video)
		video

	start: (path=null, query_str=null) ->
		if path?
			path = @setAttribute('src', path)
		else
			path = @getAttribute('src')
		if query_str?
			@query_str = query_str
		else
			query_str = @query_str
		@loc = @getAttribute('src')+query_str
		@pc.addTransceiver('video', {direction: 'recvonly'})
		@pc.addTransceiver('audio', {direction: 'recvonly'})

	negotiate: () ->
		offer = await @pc.createOffer()
		await @pc.setLocalDescription(offer)

	send_offer: () ->
		offer = @pc.localDescription
		data = await post_control(@loc, {sdp: offer.sdp, type: offer.type})
		@pc.setRemoteDescription(data)

	got_tracks: (event) =>
		if event.track.kind is 'audio'
			@video.srcObject = event.streams[0]
		else if event.track.kind is 'video'
			@video.srcObject = event.streams[0]


customElements.define('camera-video', CameraVideo)
