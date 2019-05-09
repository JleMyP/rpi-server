function getXmlHttp(){
  var xmlhttp;

  try {
    xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
  } catch (e) {
    try {
      xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    } catch (E){
      xmlhttp = false;
    }
  }

  if (!xmlhttp && typeof XMLHttpRequest!='undefined') xmlhttp = new XMLHttpRequest();

  return xmlhttp;
}


function command(text){
  xmlhttp = getXmlHttp();
  xmlhttp.onreadystatechange = function(){
    if (xmlhttp.readyState == 4 && xmlhttp.status != 200) alert(error, xmlhttp.status);
  }

  xmlhttp.open('GET', '?'+text);
  xmlhttp.send(null);
}
