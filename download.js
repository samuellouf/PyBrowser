function if_then_else_return(condition, then_return, else_return){
  if (condition) {return then_return;} else {return else_return;}
}

function getOS(){
  if (navigator.userAgent.includes("Mac OS")) return "macOS";
  if (navigator.userAgent.includes("Linux")) return "Linux";
  if (navigator.userAgent.includes("Windows")) return "Windows";
  return "Other";
}

function getArchitecture(){
  if (navigator.userAgent.includes("x64")){
    return "64";
  } else {
    return "32";
  }
}

async function loadDownloadButton(){
  var lastest_version = await fetch('https://samuellouf.github.io/api/PyBrowser/update.json').then(result => result.text());
  lastest_version = JSON.parse(lastest_version);
  
  var download_button = document.querySelector('#page #download a.downloadbutton button');
  var download_link = document.querySelector('#page #download a.downloadbutton');
  
  download_button.innerHTML = 'Download version ' + lastest_version.lastest_version + ' for <img src="' + if_then_else_return(getOS() == 'Windows', 'windows', if_then_else_return(getOS() == 'macOS', 'macOS', 'linux')) + '.svg" width="24"> ' + getOS();

  download_link.href = 'javascript: download();';
}

async function loadVersions(){
  var versions = await fetch('https://samuellouf.github.io/api/PyBrowser/versions.json').then(result => result.text()).then(r => JSON.parse(r));
  const addOptionInSelect = (name, value, select) => {
    var opt = document.createElement('option');
    opt.innerText = name;
    opt.value = value;
    document.querySelector(select).appendChild(opt);
  }
  versions.forEach((version) => {
    if (!(version.toString().includes('.'))) version = String(version) + '.0'
    addOptionInSelect(version, version, '#selectanotherversion');
  });
}

// This download function can work all by itself
async function download(version='lastest', os=if_then_else_return(getOS() == 'Windows', 'win', if_then_else_return(getOS() == 'macOS', 'macOS', 'linux'))){
  if (version == 'lastest'){
    var lastest_version = await fetch('https://samuellouf.github.io/api/PyBrowser/update.json').then(result => result.text());
    lastest_version = JSON.parse(lastest_version);
    version = lastest_version.lastest_version;
  }
  const link = document.createElement("a");
  link.href = 'https://github.com/samuellouf/PyBrowser/releases/download/v' + version + '/PyBrowser-v' + version + '-' + os + '.zip';
  link.download = 'PyBrowser-v' + version + '-' + os + '.zip';
  document.body.appendChild(link);
  link.click();
  link.remove();
}

loadVersions();
loadDownloadButton();

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const download_urlparam = urlParams.get('download');

if (download_urlparam != null){
  download();
}
