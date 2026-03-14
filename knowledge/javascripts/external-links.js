// Open all external links in a new tab
document.addEventListener("DOMContentLoaded", function () {
  var links = document.querySelectorAll("a[href]");
  for (var i = 0; i < links.length; i++) {
    var link = links[i];
    if (link.hostname && link.hostname !== window.location.hostname) {
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");
    }
  }
});
