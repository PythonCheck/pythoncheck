$(function() {
	window.ide = new IDE($('#codingsohard'));
	window.ide.buildHTMLStructure($('#codingsohard'), true, {
		theme: "monokai",
		lineNumbers: true
	});

	window.ide.console.open = function(ide) {
		$('footer .legal').fadeOut();
		$('#console').css({
			'left': $('#console').position().left, 
			'width': 'auto'
		});
		$('#console .output').css({
			'right': '0px'
		});

		$('#console').animate({
			left: '0px',
			height: '200px'
		});

		$('.content').animate({
			bottom: '230px'
		});

		$('footer').animate({
			margin: '0px 20px',
			width: '-=40px',
			height: '200px'
		}, {
			complete: function() {
				$('#console #closeTrigger').fadeIn();
			}
		});
	}

	window.ide.console.close = function(ide) {
		$('#console #closeTrigger').fadeOut();

		
		$('#console .output').css({
			'right': '0px'
		});

		$('#console').animate({
			'left': ($(document).width()-40) + 'px', 
			'width': '40px',
			'height': '40px'
		});

		$('.content').animate({
			bottom: '70px'
		});

		$('footer').animate({
			margin: '0px',
			width: '+=40px',
			height: '40px'
		}, {
			complete: function() {
				$('footer .legal').fadeIn();
				$('#console').removeAttr('style');
				$('#output').removeAttr('style');
				$('#console #closeTrigger').removeAttr('style');
			}
		});
	}

	$('#console .prompt pre').on('click', function() {
			window.ide.console(true);
	}.bind(this));

	$('#console #closeTrigger').on('click', function() {
		window.ide.console(false);
	});

	ide.getFileList(ide.populateFilePanel.bind(ide));
	ide.openFileList();
});