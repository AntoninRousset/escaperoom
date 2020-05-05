import {Widget} from '/ressources/modules/panel.js'


class CamerasWidget extends Widget

  constructor: () ->
    super('cameras', 'Cameras')

customElements.define('widget-cameras', CamerasWidget)
