(function (window) {

	var defaultOptions = {
		remoteCommandPrefix: '$',
		commandSeperator: ' ',
		errorWrapperClass: 'errorMessage',
		successWrapperClass: 'successMessage',
		neutralWrapperClass: 'outputMessage'
	}

	var Terminal = function(output, input, options) {
		this.log = $(output);
		this.commandline = $(input);

		//-- set options
		this.options = {};
		$.extend(this.options, defaultOptions);
		$.extend(this.options, options || {});

		this.commandline.keypress(function(evt) {
			if(evt.which == 13) { // ENTER key
				evt.preventDefault();
				this.input(evt.target);
			}
		}.bind(this));

		this.commandline.keydown(function(evt) {
			switch(evt.which) { 
				case 38: // UP key
					this.commandline.val(this.prevCommand());
				break;
				case 40: // DOWN key
					this.commandline.val(this.nextCommand());
				break;	
				
			}
		}.bind(this));

		this.commands = {};
		this.commandHistory = [];
		this.commandHistoryIndex = -1;

	}

	Terminal.fn = Terminal.prototype = {
		constructor: Terminal,

		// cleanes up the command before either sending it to the API or executing it localy (by calling command)
		//
		// returns: undefined
		//
		// possible calls:
		// (event) -- executes the commandline
		input: function() {
			var target = $(arguments[0]);
			var inputLine = target.val();

			// remove empty inputs
			if(inputLine == '') {
				return false;
			}

			this.success(inputLine); // print command to log
			this.commandHistory.push(inputLine); // push to history
			this.currentCommandIndex = -1; // set command history index

			var input = target.val().split(this.options.commandSeperator);
			target.val('');
			
			var structure = {
				command: input[0],
				args: input.slice(1)
			};

			// execute command
			this.command(structure)

		},

		prevCommand: function() {
			var nextIndex = this.currentCommandIndex + 1;
			if(nextIndex < this.commandHistory.length) {
				this.currentCommandIndex = nextIndex;
			}

			return this.history();
		},

		nextCommand: function() {
			var nextIndex = this.currentCommandIndex - 1;
			if(nextIndex >= 0) {
				this.currentCommandIndex = nextIndex;
			}
			else {
				this.currentCommandIndex = -1;
				return '';
			}

			return this.history();
		},

		history: function(index) {
			if(arguments.length == 0) {
				index = this.currentCommandIndex;
			}

			if(index >= 0 && index < this.commandHistory.length) {
				return this.commandHistory[this.commandHistory.length-index-1];
			}

			return '';
		},

		// binds commands to the commandline
		// 
		// possible calls:
		// () -- returns a map of all commands bound
		// (command, function) -- bind a new command where command is the invoking string
		// ({command: ..., args: ...}) -- calls a command
		command: function(command, fn) {
			if(arguments.length == 0) {
				return this.commands;
			}

			if(arguments.length == 1 && typeof(command) == 'object') {
				// invoking a command
				if(command.command && command.args) {

					// look if the command should be sent to the server
					if(command.command.startsWith(this.options.remoteCommandPrefix) && typeof(this.remote) == 'function') {
						// remove command prefix
						command.command = command.command.substring(this.options.remoteCommandPrefix.length, command.command.length);

						// and finaly send it to the api
						this.remote(command.command, command, function(result, resultTextStatus, resultJqXHR) {
							this.output(result.toString());
						}.bind(this));
					}
					else if (this.commands[command.command]) {
						this.commands[command.command].apply(this, command.args);	
						return true;
					}
					else {
						this.error('Command not found!');
						return false;
					}
					
					
				}
				// a object is given containing a command map
				else {
					for(var key in command) {
						this.command(key, command[key]);
					}
				}
			}
			else if(arguments.length >= 2 && typeof(command) == 'string' && typeof(fn) == 'function') {
				this.commands[command] = fn;
				return true;
			}
			else {	
				return false;
			}
		},

		// opens or adds output to the console
		//
		// for opening the console, this.open is called. For closing this.close is called. 
		// both functions have to be defined after initiating the IDE
		//
		// text params should always be valid HTML code
		// after adding output, the pane will scroll to the bottom
		// 
		// returns: undefined
		//
		// possible calls:
		// () -- invert the consoles open state
		// (bool) -- set the consoles open state.
		// (bool, text) -- set the consoles open state and add the text as output
		// (text) -- open the console and add the text as output
		console: function() {

			var doOpen;
			var str = null;
			// console() --> inverts console state
			if(arguments.length == 0) {
				this.doOpen = !this.consoleIsOpen
			}
			
			// console(bool) --> set console state
			if(arguments.length >= 1 && typeof(arguments[0]) == 'boolean') {
				doOpen = arguments[0];

				// console(bool, str) --> set console state and add output
				if(arguments.length >= 2 && typeof(arguments[1]) == 'string') {
					str = arguments[1]
				}
			}
			// console(str) --> open console if not open and add output
			else if (arguments.length >= 1 && (typeof(arguments[0]) == 'string' || typeof(arguments[0]) == 'object')) {
				doOpen = true;
				str = arguments[0];
			}

			if(doOpen || this.consoleIsOpen) {
				if(doOpen && !this.consoleIsOpen) {
					//open console
					if(typeof(this.open) == 'function') {
						this.open(this);
					}
					this.consoleIsOpen = true;
				}
				else if (!doOpen){
					// close console
					if(typeof(this.close) == 'function') {
						this.close(this);
					}
					this.consoleIsOpen = false;
				}
			}

			if(str != null) {
				// add output to console
				this.log.append(str).animate({scrollTop: this.log.prop('scrollHeight')});

			}
		},

		// adds output to the console
		//
		// possible calls:
		// (string, ...) -- adds output to the console using console(wrapInSpan(htmlify(string)), errorWrapperClass)
		error: function () {
			for(var i = 0; i < arguments.length; i++) {
				this.console(this.wrapInSpan(this.htmlify(arguments[i]), this.options.errorWrapperClass));
			}
		},

		// adds output to the console
		//
		// possible calls:
		// (string, ...) -- adds output to the console using console(wrapInSpan(htmlify(string)), neutralWrapperClass)
		output: function() {
			for(var i = 0; i < arguments.length; i++) {
				this.console(this.wrapInSpan(this.htmlify(arguments[i]), this.options.neutralWrapperClass));
			}
		},

		// adds output to the console
		//
		// possible calls:
		// (string, ...) -- adds output to the console using console(wrapInSpan(htmlify(string)), successWrapperClass)
		success: function () {
			for(var i = 0; i < arguments.length; i++) {
				this.console(this.wrapInSpan(this.htmlify(arguments[i]), this.options.successWrapperClass));
			}	
		},

		clear: function() {
			this.log.empty();
		},

		// htmlifies a string including:
		// * replacing < and > with &lt; and &gt; respectively
		// * replacing \n, \r, or \r\n with <br>
		// * adding a <br> at the end if there isn't any
		//
		// returns: a html-string (e.g. 'abc<br>abc<br>')
		//
		// possible calls:
		// (string)
		htmlify: function(str) {
			str = str.replace(/</g, '&lt;');
			str = str.replace(/>/g, '&gt;');
			str = str.replace(/(\r\n)|(\r)|(\n)/g, '<br>');

			if(str.match(/.*<br>$/)) {
				return str;
			}
			else {
				return str + '<br>';
			}
		},

		// wraps a given text into a span, assuming it is valid HTML (see htmlify)
		// 
		// returns: the output wrapped in a span of this pattern: <span class="[classes]">[text]</span>
		//
		// possible calls:
		// (textString, classesString) -- both arguments are strings
		wrapInSpan: function(text, classes) {
			return $('<span class="' + classes + '">' + text + '</span>')
		}
	}

	window.Terminal = Terminal;
})(window);