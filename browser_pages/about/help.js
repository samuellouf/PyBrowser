async function init(){
    document.querySelector('section div.update p.updatetext').innerText = 'Searching for updates...';

    if (navigator.userAgent.includes('x64')){
        document.querySelector('section div.update span.bits').innerText = '64';
    } else {
        document.querySelector('section div.update p.version span.bits').innerText = '32';
    }

    try{
        var update = await fetch('https://samuellouf.github.io/api/PyBrowser/update.json').then(r => r.text());
        update = JSON.parse(update);
        if (Number(update.lastest_version) <= 1){
            document.querySelector('section div.update p.updatetext').innerText = 'PyBrowser is up to date.';
            document.querySelector('section div.update img[src="ok.png"]').style.display = '';
        } else if (Number(update.lastest_version) > 1){
            document.querySelector('section div.update p.updatetext').innerHTML = 'PyBrowser isn\'t up to date. <a href=""><button>Click here to download and install the update</button></a>';
            document.querySelector('section div.update img[src="error.svg"]').style.display = '';
        } else {
            document.querySelector('section div.update p.updatetext').innerText = 'PyBrowser is up to date.';
            document.querySelector('section div.update img[src="ok.png"]').style.display = '';
        }
    } catch (error) {
        try{
            document.querySelector('section div.update p.updatetext').innerText = 'Unknown error';
            document.querySelector('section div.update img[src="error.svg"]').style.display = '';
        } catch (e){
            document.querySelector('section div.update p.updatetext').innerText = 'An error occured while PyBrowser was checking for updates : There is no internet connection.';
            document.querySelector('section div.update img[src="error.svg"]').style.display = '';
        }
    }
}

init()