class LoadingAnimation extends HTMLElement

  constructor: () ->
    super()

  connectedCallback: () =>
    @innerHTML = ''
    span = document.createElement('span')
    span.classList.add('loading')
    for i in [1..5]
      div = document.createElement('div')
      span.appendChild(div)
    @appendChild(span)


customElements.define('loading-animation', LoadingAnimation)
