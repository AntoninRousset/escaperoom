// Generated by CoffeeScript 2.3.2
var dom_parser, sleep;

dom_parser = new DOMParser();

sleep = function(ms) {
  return new Promise(function(resolve) {
    return setTimeout(resolve, ms);
  });
};

export var fetch_html = async function(url, slow = false) {
  var resp;
  resp = (await fetch(url, {
    mehtod: 'GET'
  }));
  if (slow) {
    await sleep(Math.floor(Math.random() * 3000));
  }
  if (!resp.ok) {
    console.warn('Failed to fetch', url);
    return null;
  }
  return dom_parser.parseFromString((await resp.text()), 'text/html');
};
