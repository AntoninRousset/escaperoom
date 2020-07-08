import {Widget} from '/ressources/modules/panel.js'


class StoryWidget extends Widget

  constructor: () ->
    super('story', 'Story')

customElements.define('widget-story', StoryWidget)
