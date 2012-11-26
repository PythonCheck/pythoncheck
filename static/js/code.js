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
		submit: 'submit'
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
		success: this.output.bind(this)
	}
	return settings;
};

Code.prototype.output = function(data, textStatus, jqXHR) {
	this.printMessages("Done!");
	this.printMessages(data.output);
	console.log(data);
};

var _c;
$(document).ready(function() {
	_c = new Code($('#code-pane'), $('#output'));
})
