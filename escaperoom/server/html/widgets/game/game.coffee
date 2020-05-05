import {Widget} from '/ressources/modules/panel.js'


class GameWidget extends Widget

  constructor: () ->
    super('game', 'Game')

customElements.define('widget-game', GameWidget)
