import Subscriber from './monitor.js'

class CamerasList extends Subscriber
	constructor: () ->
		super()
		@cameras = {}
		@subscribe()

	add_item: (id, data) ->
		item = document.createElement('div')
		item.setAttribute('class', 'item')
		item.setAttribute('item_id', id)
		for key of data
			span = document.createElement('span')
			span.setAttribute('slot', key)
			item.appendChild(span)
		@items_container.appendChild(item)
		item.attachShadow({mode: 'open'})
		item.shadowRoot.appendChild(@template_item.content.cloneNode(true))
		camera = item.shadowRoot.querySelector('camera-stream')
		camera.setAttribute('src', camera.getAttribute('src')+'?id='+id)
		@cameras[id] = camera
		camera.start()

	update_item: (id, data) ->
		item = @get_item(id)
		for key, value of data
			item.querySelector('span[slot='+key+']').textContent = value

	remove_item: (id) ->
		@cameras[id].stop()
		@cameras[id] = null
		@get_item(id).remove()

customElements.define('cameras-list', CamerasList)

class CameraStream extends HTMLElement
	constructor: () ->
		super()
		@video = @querySelector('video')
		@video.onclick = () =>
			@video.mozRequestFullScreen()
		@pc = new RTCPeerConnection()
		@pc.onnegotiationneeded = (event) => @negotiate()
		@pc.onicegatheringstatechange = (event) =>
			if @pc.iceGatheringState is 'complete'
				@send_offer()
		@pc.ontrack = (event) => @got_tracks(event.streams)

	start: () ->
		@pc.addTransceiver('video', {direction: 'recvonly'})

	negotiate: () ->
		offer = await @pc.createOffer()
		await @pc.setLocalDescription(offer)

	send_offer: () ->
		offer = @pc.localDescription
		response = await fetch(@getAttribute('src'), {
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
		@video.srcObject = streams[0]

customElements.define('camera-stream', CameraStream)
