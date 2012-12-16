(function(window) {

	var Utils = function() {

	};

	Utils.prototype = {
		constructor: Utils,

		flash: function(container) {
			if(!container) {
				container = $('.flash');
			}

			var flashRemoved = false;
			container.delay(2000).fadeOut(5000, function() {
				flashRemoved = true;
			});
			container.on('hover', function() {
				if(!flashRemoved) {
					container.stop().clearQueue();
					container.show(0).css({
						opacity: '1.0'
					});
				}
			})
		}, 
		numberOfProperties: function(obj) {
			var count = 0;
			for(k in obj) {
				count++;
			}
			return count;
		}
	};

	window.Utils = new Utils();
})(window);
