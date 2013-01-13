$(function() {
	// intialize the terminal
	window.term = new Terminal('.output', $('footer .cmd input'));

	term.open = function(term) {
		$('#console').css({
			'left': $('#console').position().left, 
			'width': 'auto'
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
				$('#console div.cmd input').focus();
			}
		});
	}

	term.close = function(term) {
		$('#console #closeTrigger').fadeOut();

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
				$('#console').removeAttr('style');
				$('#output').removeAttr('style');
				$('#console #closeTrigger').removeAttr('style');
			}
		});
	}

	$('#console .prompt pre').on('click', function() {
		term.console(true);
	}.bind(this));

	$('#console #closeTrigger').on('click', function() {
		term.console(false);
	});

	// initialize AutoComplete
	CodeMirror.commands.autocomplete = function(cm) {
		CodeMirror.simpleHint(cm, CodeMirror.pythonHint);
	}

	// initialize the IDE
	window.ide = new IDE($('#codingsohard'));
	window.ide.buildHTMLStructure($('#codingsohard'), true, {
		theme: "monokai",
		lineNumbers: true,
		autofocus: true, // autofocus the CodeMirror upon initialization
		indentWithTabs: true,
		tabSize: 4,
		indentUnit:4,
		extraKeys: {'Ctrl-Space': "autocomplete"}
	});

	window.ide.dragNDrop($('#codingsohard'));

	ide.getFileList(ide.populateFilePanel.bind(ide));
	ide.openFileList();

	initCommands(term, ide);
	ide.console(term);	

});