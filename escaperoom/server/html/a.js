



function load() {

  // switch tab given by hash
  select_tab(window.location.hash.substr(1));

  // listen pressed keys
  document.addEventListener('keydown', keypress);

  // add ondragover to all panels
  document.querySelectorAll('.panel > header').forEach(function (panel) {
    panel.setAttribute('draggable', 'true');
  });

  document.querySelectorAll('.panel').forEach(function (panel) {
    panel.parentElement.addEventListener('dragenter', dragenter);

    panel.addEventListener('dragstart', dragstart);
    panel.addEventListener('dragend', dragend);
    panel.addEventListener('drop', console.log);

    // to allow drop
    panel.parentElement.addEventListener('dragover', event => event.preventDefault());
  });
}

function dragstart(event) {

  // prevent anything else thant headers to be drag
  if (event.target.nodeName.toUpperCase() !== "HEADER")
    event.preventDefault();

  // set class dragged
  event.target.setAttribute('dragged', '');

}


function dragstart(event) {

  // prevent anything else thant headers to be drag
  if (event.target.nodeName.toUpperCase() !== "HEADER")
    event.preventDefault();

  // set class dragged
  event.target.setAttribute('dragged', '');

}

function dragstart(event) {

  // prevent anything else thant headers to be drag
  if (event.target.nodeName.toUpperCase() !== "HEADER")
    event.preventDefault();

  // set class dragged
  event.target.setAttribute('dragged', '');

}


