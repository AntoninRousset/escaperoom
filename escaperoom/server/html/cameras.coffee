import {Subscriber, Container} from './monitor.js'
import {is_empty} from './monitor.js'

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
			stream = item.shadowRoot.querySelector('camera-video').srcObject
			big_boy = document.querySelector('cameras-box').shadowRoot.getElementById('bigscreen')
			big_boy.srcObject = stream
		@appendChild(item)
		item.shadowRoot.querySelector('camera-video').start(null, '?id='+id)

customElements.define('cameras-list', CamerasList)

#TODO remove the need for a STUN server
class CameraVideo extends HTMLElement
	constructor: () ->
		super()
		try
			@pc = new RTCPeerConnection()
			@pc.onnegotiationneeded = (event) => @negotiate()
			@pc.onicegatheringstatechange = (event) =>
				if @pc.iceGatheringState is 'complete'
					@send_offer()
			@pc.ontrack = (event) => @got_tracks(event.streams)
		catch error
			@set_screen(error)
		@video = @create_video()
	
	create_video: () ->
		video = document.createElement('video')
		video.setAttribute('autoplay', 'true')
		video.setAttribute('muted', 'true')
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

	negotiate: () ->
		offer = await @pc.createOffer()
		await @pc.setLocalDescription(offer)

	send_offer: () ->
		offer = @pc.localDescription
		response = await fetch(@loc, {
			body: JSON.stringify({
				sdp: offer.sdp,
				type: offer.type,
			}),
			headers: {
				'Content-Type': 'application/json'
			},
			method: 'POST'
		})
		@pc.setRemoteDescription(await response.json())

	got_tracks: (streams) ->
		@srcObject = streams[0]
		@video.srcObject = @srcObject

customElements.define('camera-video', CameraVideo)
