import {Widget} from '/ressources/modules/panel.js'


class TimerWidget extends Widget

  constructor: () ->
    super('timer', 'Timer')

customElements.define('widget-timer', TimerWidget)
