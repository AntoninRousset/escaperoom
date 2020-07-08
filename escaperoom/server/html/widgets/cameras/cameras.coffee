import {Widget} from '/ressources/modules/panel.js'
import {post_control} from '/ressources/modules/communication.js'


class CamerasWidget extends Widget

  constructor: () ->
    super('cameras', 'Cameras')
    @subscribe('/cameras')


  connectedCallback: () =>
    super()
    @querySelector('.content').classList.add('darkbox')

  update: (data) =>

    content = @querySelector('.content')
    content.innerHTML = ''
    for id, d of data.cameras
      video = new CameraVideo()
      video.start('/camera', '?id=' + id)
      content.appendChild(video)

    @removeAttribute('loading')


customElements.define('widget-cameras', CamerasWidget)


class CameraVideo extends HTMLElement
  constructor: () ->
    super()
    @video = @create_video()
    @pc = @create_pc()

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

  start: (path, query_str=null) ->
    if query_str?
      @query_str = query_str
    else
      query_str = @query_str
    #@loc = @getAttribute('src') + query_str
    @loc = path + query_str
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
