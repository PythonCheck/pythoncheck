function initCommands(terminal, ide) {

	var err = ide.error.bind(ide);
	var out = ide.output.bind(ide);
	var yes = ide.success.bind(ide);

	//-- clear
	terminal.command({
		'clear': function(args) {
			term.clear();
		},
		'do': function(args) {
			console.log('lol');
		},
		'new': function(project, filename) {
			if(arguments.length < 2) {
				err('Need to specify project and filename!');
			}
			else if (typeof(project) != 'string' || typeof(filename) != 'string') {
				err('Need to specify two strings!');
			}
			else {
				ide.currentProject = project;
				ide.newFile.call(ide, filename);
			}
		},
		'help': function() {
			out('The following commands are available:');
			var map = terminal.command();
			for(var command in map) {
				out(command);
			}
		},
		'close': function() {
			ide.console.call(ide, false);
		}, 
		'shortcuts': function(){
			for(var k in ide.keys) {
				out(k + ': ' + ide.keysText[k]);
			}
		},
		'e': function() {
			var js = ''
			for(var k in arguments) {
				js += arguments[k] + ' ';
			}
			eval(js);
		}
	});
}	

