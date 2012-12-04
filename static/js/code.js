//-- UTILS
String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

//-- Code CORE
var Code = function(code, output) {
	this.code = $(code);
	this.options = {
		path: '/PythonCheck/run/',
		run: 'run.json',
		submit: 'submit',
		retrieve: 'result.json',
		defaultTimeout: 1000

	}
	this.console = output;
}

Code.prototype.run = function() {
	$.ajax(this.wrap(this.options.path + this.options.run));
	this.printMessages("Sending....");
}

Code.prototype.submit = function() {
	$.ajax(this.wrap(this.options.path + this.options.submit));
	this.printMessages("Sending....");
}

Code.prototype.printMessages = function(output) {
	if(!output.endsWith("\n") && !output.endsWith("\r")) {
		output += "\n";
	}

	$(this.console).val($(this.console).val() + output);
}

Code.prototype.wrap = function(url) {
	var settings = {
		type: 'POST',
		url: url,
		data: {
			code: this.code.val()
		},
		dataType: 'JSON', 
		success: this.wait.bind(this)
	}
	return settings;
};

Code.prototype.wait = function(data, textStatus, jqXHR) {
	this.printMessages("Building...");
	
	//-- Closure Variables
	var options = this.options;
	var buildId = data.buildId;
	var output = this.output.bind(this);

	var interval = setInterval(function() {
		// make ajax request to see if the results are ready
		$.ajax({
			type: 'GET',
			url: options.path + options.retrieve,
			data: {
				buildId: buildId
			},
			dataType: 'JSON',
			success: function(resultData, resultTextStatus, resultJqXHR) {
				// if the results are ready --> PARTY!
				if(resultData.finished) {
					clearInterval(interval);
					output(resultData);
				}
			}
		});
	}, data.timeout || this.options.defaultTimeout);
}

//-- Prints results to the console
Code.prototype.output = function(data) {
	this.printMessages("Done!");
	this.printMessages(data.output);
};

//-- Helper function to stop all running requests
Code.prototype.cancel = function() {
	clearTimeout();
}

var _c;
$(document).ready(function() {
	_c = new Code($('#code-pane'), $('#output'));
})
