var system = require('system'),
	page = require('webpage').create(),
	firstload = true,
	ENABLE_LOAD = /(jquery\.min\.js|jquery\.jtruncate\.pack\.js)$/i,
	openload_id = system.stdin.readLine();

page.onResourceRequested = function(req, net) {
	if( firstload || req.url.match(ENABLE_LOAD) )
	{
		firstload = false
	}else{
		net.abort();
	}
};

page.onInitialized = function() {
  page.evaluate(function() {
	delete window._phantom;
	delete window.callPhantom;
  });
};

page.onLoadFinished = function(status) {
	console.log('STATUS: ' + status)
	if(status == 'success'){
		var data = page.evaluate(function() {
				return {
					'title': document.querySelector('meta[name="og:title"]').content,
					'image': document.querySelector('meta[name="og:image"]').content,
					'video': document.querySelector('#streamurl,#streamurj,#streamuri').innerHTML
				}
			});
		console.log('TITLE: ' + data.title);
		console.log('IMAGE: ' + data.image);
		console.log('VIDEO: ' + data.video);
	}else{
		console.log("ERROR: Failed to load page");
	}
	phantom.exit();
};
page.settings.userAgent = 'Mozilla / 5.0(Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1';
page.open('https://oload.stream/embed/' + openload_id +'/');