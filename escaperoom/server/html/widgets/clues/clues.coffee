import {Widget} from '/ressources/modules/panel.js'


class CluesWidget extends Widget

  constructor: () ->
    super('clues', 'Clues')

customElements.define('widget-clues', CluesWidget)
