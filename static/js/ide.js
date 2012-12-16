
// depends on 
// Utils
(function(window) {

	var EXERCISE_CONTAINS_SINGLE_FILE = true;
	var EXERCISE_MAIN_FILE = 'main.py';

	var defaultOptions = {
		tabPanelClass: 'tabs',
		menuPanelClass: 'menu',
		codePanelClass: 'code',
		filePanelClass: 'files',
		listTriggerClass: 'listtrigger',
		apiURL: '/PythonCheck/',
		apiNew: 'file/new.json',
		apiList: 'file/list.json',
		apiFileDetails: 'file/details.json',
		apiRun: 'run/run.json',
		apiSubmit: 'run/submit.json',
		apiResult: 'run/result.json',
		defaultTimeout: 1500,
		fileListWidth: 250
	};

	var IDE = function(appendTo, options) {
		//-- set options
		this.options = {};
		$.extend(this.options, defaultOptions);
		$.extend(this.options, options);

		//-- initialize variables
		this.tabPanel = null;
		this.menuPanel = null;
		this.codePanel = null;
		this.filePanel = null;
		this.filePanelMenu = null;
		this.filePanelContent = null;
		this.listPuller = null;
		this.internalCodeMirror = null;
		this.currentCourse = false;
		this.currentProject = false;
		this.mainFile = false;
		this.currentlyOpenFiles = [];
		this.focusedFileReadURL = null;
	};

	IDE.fn = IDE.prototype = {
		constructor: IDE,

		buildHTMLStructure: function(appendTo, codeMirror, codeMirrorOptions) {
			$(appendTo)
				.append(this.tabPanel = $('<nav class="' + this.options.tabPanelClass + '"></nav>'))
				.append(this.menuPanel = $('<nav class="' + this.options.menuPanelClass + '"></nav>'))
				.append(this.codePanel = $('<div class="' + this.options.codePanelClass + '"></div>'))
				.append(
					this.filePanel = $('<div class="' + this.options.filePanelClass + '"></div>')
						.append(
							this.filePanelMenu = $('<nav></nav>')
								.append($('<a>New Project</a>'))
						)
						.append(
							this.filePanelContent = $('<section class="filelist"></section>')
						)
				);

			this.menuPanel
				.append($('<a>Run</a>').on('click',    function() { this.run();      }.bind(this)))
				.append($('<a>Save</a>').on('click',   function() { this.syncFile(); }.bind(this)))
				.append($('<a>Submit</a>').on('click', function() { this.submit();   }.bind(this)))
				.append(this.listPuller = $('<a class="icon-chevron-left icon-white ' + this.options.listTriggerClass + '">Files</a>'));

			if(arguments.length > 1) {
				this.codeMirror(arguments[1], arguments[2]);
			}

			this.registerActions();
		},

		registerActions: function() {
			
			// file list
			$(this.listPuller).click(this.openFileList.bind(this));

			// save/edit actions
			this.internalCodeMirror.setOption('onChange', this.contentUpdated.bind(this));

		},

		contentUpdated: function(cm, changeObject) {
			var file = this.getFocusedFile();
			
			this.saved(file, cm.getValue() == file.content);
		},

		openFileList: function(event) {
			var editArea = $(this.codePanel).find('.CodeMirror-scroll');

			editArea.animate({
				left: '-' + this.options.fileListWidth + 'px'
			}, 'fast');

			$(this.filePanel).animate({
				left: ($(this.codePanel).width() - this.options.fileListWidth) + 'px'
			}, 'fast');

			$(this.listPuller).removeClass('icon-chevron-left').addClass('icon-chevron-right');

			// unbind current handlers
			$(this.listPuller).off('click');

			// bind new handlers
			$(this.listPuller).add(editArea).on('click', this.closeFileList.bind(this));
		},

		closeFileList: function(event) {
			var editArea = $(this.codePanel).find('.CodeMirror-scroll');

			editArea.animate({
				left: 0
			}, 'fast');

			$(this.filePanel).animate({
				left: '100%'
			}, 'fast');

			$(this.listPuller).removeClass('icon-chevron-right').addClass('icon-chevron-left');

			// unbind current handlers
			$(this.listPuller).add(editArea).off('click');

			// bind new handlers
			$(this.listPuller).on('click', this.openFileList.bind(this));
		},

		newFile: function(filename) {

			fileInformation = {};

			if(typeof(filename) == 'string') {
				fileInformation.filename = filename;

				if(this.currentCourse && this.currentProject) {
					fileInformation["type"] = 'exercise';
					fileInformation.course = this.currentCourse;
					fileInformation.project = this.currentProject;
				}
				else {
					fileInformation["type"] = 'project';
					fileInformation.project = this.currentProject;	
				}
			}
			else {
				fileInformation['type'] = 'exercise';
				fileInformation.project = filename.project;
				fileInformation.course = filename.course;
			}

			this.api(this.options.apiNew, fileInformation, 
				function(data) {
					console.log(data);
				})
		},

		populateFilePanel: function(files) {
			var list = $('<ul></ul>');
			$(this.filePanelContent).empty().append(list);

			if(files.courses) {
				for(var coursename in files.courses) {

					var course;
					var courseCaption;
					list.append((courseCaption = $('<li>' + coursename + '</li>')).append(course = $('<ul></ul>')))
					courseCaption.attr({
						'data-type': 'course',
						'data-course': files.courses[coursename].id
					});

					for(var exercisename in files.courses[coursename].exercises) {
						var ex, fileObj, details, exerciseCaption; 

						// if an exercise is allowed to contain more than one file, list all files
						if(!EXERCISE_CONTAINS_SINGLE_FILE || EXERCISE_CONTAINS_SINGLE_FILE === false) {
							course.append((exerciseCaption = $('<li>' + exercisename + '</li>')).append(ex = $('<ul></ul>')))

							exerciseCaption.attr({
								'data-type': 'project',
								'data-project': files.courses[coursename].exercises[exercisename].id
							});
						
							for(var filename in files.courses[coursename].exercises[exercisename].files) {
								details = this.fileDetails(files.courses[coursename].exercises[exercisename].files[filename]);

								this.createFileLink(details, 'filename', ex, this.openFile.bind(this))
							}
						}
						else {
							var numberOfFiles = (Utils.numberOfProperties(files.courses[coursename].exercises[exercisename].files));
							console.log(numberOfFiles);
							if(numberOfFiles == 0) {
								details = {
									'exercisename': exercisename,
									'filename': EXERCISE_MAIN_FILE,
									'course': files.courses[coursename].id,
									'project': files.courses[coursename].exercises[exercisename].id
								}

								this.createFileLink(details, 'exercisename', course, this.newFile.bind(this))
							}
							else {
								console.log(coursename);
								details = {};
								for(var k in files.courses[coursename].exercises[exercisename].files) {
									details = files.courses[coursename].exercises[exercisename].files[k];
								}
								details.filename = exercisename;
								this.createFileLink(details, 'filename', course, this.openFile.bind(this));
							}
						}
					}
				}
			}
			
			if (files.projects) {
				for(var projectname in files.projects) {
					var project;
					list.append($('<li>' + projectname + '</li>').append(project = $('<ul></ul>')))

					for(var filename in files.projects[projectname].files) {
						details = this.fileDetails(files.projects[projectname].files[filename]);

						this.createFileLink(details, 'filename', project, this.openFile.bind(this))
					}
				}
			}
		},

		fileDetails: function(fileObj) {
			return {
				'filename': fileObj.filename,
				'readURL': fileObj.readURL,
				'saveURL': fileObj.saveURL,
				'version': fileObj.version,
				'edited': fileObj.edited,
				'project': fileObj.project,
				'course': fileObj.course
			};
		},

		openFile: function(file) {
			if(this.focusFile(file) === false) {
				//file wasn't open already
				var tab = this.createFileTab(file, 'filename', this.focusFile.bind(this));
				this.tabPanel.append(tab);
				file.tab = tab;
				
				this.currentlyOpenFiles.push(file);
				file.saved = true;

				this.focusedFileReadURL = file.readURL;

				this.syncFile(file);
				this.focusFile(file);
			}
			else {
				this.focusFile(file);
			}
			this.internalCodeMirror.setOption('readOnly', false);
		},

		saveFile: function(file, content, callbacks) {

			// use the current editors content as content for the file
			if(typeof(content) == 'function') {
				callbacks = content;
				content = false;
			}

			if(typeof(callbacks) == 'function') {
				callbacks = {success: callbacks};
			}

			var data = {
				course: file.course,
				project: file.project, 
				filename: file.filename,
				code: (content === false) ? this.internalCodeMirror.getValue() : content 
			};

			this.api(file.saveURL, data, function(ret) {
				ret = $.parseJSON(ret);
				if(ret.success == true) {

					this.saved(file, true);

					if(callbacks.success) {
						callbacks.success();	
					}
					
				}
				else {

					if(callbacks.error) {
						callbacks.error();
					}

				}
			}.bind(this));
		},

		saved: function(file, saved) {

			if(arguments.length == 1) {
				// only file object was given
				return file.saved;

			}

			if(typeof(file) == 'boolean') {
				saved = file;
				file = this.currentlyFocusedFile();
			}
			if(saved) {
				saved = true;
			}
			else {
				saved = false;
			}

			var index = this.getOpenFileIndex(file);
			var previousState = this.currentlyOpenFiles[index].saved;
			this.currentlyOpenFiles[index].saved = saved;
			
			var statusChanged = previousState != saved;

			var tabText = this.currentlyOpenFiles[index].tab.text();
			// file is newly saved
			if(statusChanged && saved) {
				// remove the * indicating that the file is unsaved
				this.currentlyOpenFiles[index].tab.text(tabText.substring(0, tabText.length-1));
			}
			// file is newly not saved (just edited)
			else if (statusChanged && !saved) {
				// add the * indicating that the file is unsaved
				this.currentlyOpenFiles[index].tab.text(tabText + '*');
			}
		},

		sync: function(fileObj) {
			this.api(fileObj.readURL, function(data) {
				// because the files most probably end with .py
				// and therefore the request ends with .py we need to parse explicitly
				data = $.parseJSON(data);
				
				var details = this.fileDetails(data);
				details.saved = true;
				details.content = data.content;

				var index = this.getOpenFileIndex(data);
				details.tab = this.currentlyOpenFiles[index].tab;
				this.currentlyOpenFiles[index] = details;

				//check if the file is currently focused (and therefore visible)
				if(data.readURL == this.focusedFileReadURL && this.internalCodeMirror.getValue() != data.content) {
					this.updateView(details, true);
				}
			}.bind(this));
		},

		syncFile: function(fileObj) {
			if(!fileObj) {
				fileObj = this.getFocusedFile();
			}

			var openFile = this.getOpenFile(fileObj);

			if(openFile.readURL == fileObj.readURL) {
				if(openFile.saved) {
					this.sync(openFile);
				}
				else {
					this.saveFile(openFile, function() {
						this.sync(openFile);
					}.bind(this));
				}
			}
		},

		getFocusedFile: function() {
			return this.getOpenFile({readURL: this.focusedFileReadURL});
		},

		getOpenFile: function(file, index) {
			var fileFound = null;

			$.each(this.currentlyOpenFiles, function(i, openFile) {
				// index is the start index
				if(typeof(index) == 'number' && index >= 0) {
					if(index < i) return;
				}

				if(openFile.readURL == file.readURL) {
					// index specifies wether the index should be returned;
					if(index === true) {
						fileFound = i;
					}
					else {
						fileFound = openFile;	
					}
				}
			});

			return fileFound;
		},

		getOpenFileIndex: function(file) {
			return this.getOpenFile(file, true);
		},

		createFileTab: function(file, titleAttribute, callback) {
			var tab = $('<a>' + file[titleAttribute] + '</a>');
			tab.on('click', function() {
				callback(file);
			});
			return tab;
		},

		createFileLink: function(details, nameProperty, appendTo, callback) {
			var item = $('<li></li>');
			var title;

			if(nameProperty && details[nameProperty]) {
				title = details[nameProperty];
			}
			else if(!nameProperty && details['title']) {
				title = details['title'];	
			}
			else {
				title = '';		
			}

			item.append(title);
			item.data(details);

			item.on('click', function() {
				callback(details);
			});
			appendTo.append(item);
		},

		focusFile: function(file) {
			var fileIsOpen = false;
			var openFile = this.getOpenFile(file);

			if(openFile === null) {
				return false;
			}
			else {

				this.updateView(openFile);
				this.focusedFileReadURL = openFile.readURL;

				$(openFile.tab).siblings().removeClass('active');
				$(openFile.tab).addClass('active');

				this.currentProject = openFile.project;
				this.currentCourse = openFile.course;

				return true;
			}
			
		}, 

		updateView: function(openFile, ignoreContents) {
			// disable the change function
			var changeFunction = this.internalCodeMirror.getOption('onChange');
			this.internalCodeMirror.setOption('onChange', function() {});

			if(openFile) {
				//console.log('updating view with params');
				var currentlyFocusedFile = this.getFocusedFile();
				
				if(!ignoreContents) {
					currentlyFocusedFile.content = this.internalCodeMirror.getValue();	
				}
				this.internalCodeMirror.setValue(openFile.content || '');
			}
			else {
				//console.log('updating current view');
				var openFile = this.getFocusedFile();
				
				this.internalCodeMirror.setValue(openFile.content);
				
				console.log(openFile.content);
			}

			// enable the change function
			this.internalCodeMirror.setOption('onChange', changeFunction);

		},

		run: function(file) {
			if(!file) {
				file = this.getFocusedFile();
			}

			console.log(file);
			this.api(this.options.apiRun, {
				execute: file.filename,
				course: file.course,
				project: file.project
			}, function(data) {
				this.results(data);
			}.bind(this));
		},

		submit: function(file) {
			if(!file) {
				file = this.getFocusedFile();
			}

			this.api(this.options.apiSubmit, {
				execute: file.filename,
				course: file.course,
				project: file.project
			}, function(data) {
				this.results(data, function() {
					console.log('submitted');
				});
			}.bind(this));
		},

		results: function(error, output) {

			// results({ obj with build data }) or results({ obj with build data }, callback)
			if(typeof(arguments[0]) == 'object' && (arguments.length == 1) || (arguments.length == 2 && typeof(arguments[1]) == 'function')) {
				var data = arguments[0];
				var callback;
				
				if(arguments.length == 2 && typeof(arguments[1]) == 'function') {
					callback = arguments[1];
				}

				var interval = setInterval(function() {
					this.api(this.options.apiResult, {buildId: data.buildId}, function(resultData, resultTextStatus, resultJqXHR) {
							// if the results are ready --> PARTY!
							if(resultData.finished) {
								clearInterval(interval);
								this.results(resultData.error, resultData.output);
								
								if(callback) {
									callback({
										'error': resultData.error, 
										'output': resultData.output,
										'requestData': data
									})
								}
							}
						}.bind(this));
				}.bind(this), data.timeout || this.options.defaultTimeout);
			}
			else {
				if(error) {
					this.output('errors: ', error);
				}
				if(output) {
					this.output('outputs: ', output);
				}
			}
		},

		output: function() {
			for(var i = 0; i < arguments.length; i++) {
				this.console(arguments[i]);
			}
		},

		getFileList: function(callback) {
			this.api(this.options.apiList, {}, callback)
		},

		codeMirror: function(codeMirror, codeMirrorOptions) {
			if(codeMirror === true) {
				//extend the CodeMirror keyMap adding the IDE keys
				$.extend(CodeMirror.keyMap.default, this.keys);
				
				//default
				cmOptions = {
					//keyMap: CodeMirror.keyMap.default,
					//lineNumbers: true
				};

				if(codeMirrorOptions) {
					$.extend(cmOptions, codeMirrorOptions);
				}
				
				this.internalCodeMirror = new CodeMirror(this.codePanel[0], cmOptions);
			}
			else if(codeMirror) {
				this.internalCodeMirror = codeMirror;
			}
			this.internalCodeMirror.IDE = this;
			this.internalCodeMirror.setOption('readOnly', true);
			return this.internalCodeMirror;
		},

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
			else if (arguments.length >= 1 && typeof(arguments[0]) == 'string') {
				doOpen = true;
				str = arguments[0];
			}

			if(doOpen || this.consoleIsOpen) {
				if(doOpen && !this.consoleIsOpen) {
					//open console
					if(this.console.open && typeof(this.console.open) == 'function') {
						this.console.open(this);
					}
					this.consoleIsOpen = true;
				}
				else if (!doOpen){
					// close console
					if(this.console.close && typeof(this.console.close) == 'function') {
						this.console.close(this);
					}
					this.consoleIsOpen = false;
				}
			}

			if(str != null) {
				// add output to console
				$('.output').append(this.htmlify(str)).animate({scrollTop: $('.output').prop('scrollHeight')});

			}
		},

		htmlify: function(str) {
			str = str.replace(/(\r\n)|(\r)|(\n)/g, '<br>');
			if(str.match(/.*<br>$/)) {
				return str;
			}
			else {
				return str + '<br>';
			}
		},

		api: function(action, data, callback) {
			if(typeof(data) == 'function') {
				callback = data;
				data = {};
			} 

			$.ajax({
				type: 'POST',
				url: this.options.apiURL + action,
				data: data,
				dataFormat: 'JSON',
				success: callback
			});
		},

		keys: {
			"Ctrl-R": function(cm) {
				cm.IDE.run();
			}, 
			"Alt-Tab": function(cm) {
				console.log(cm);
			},
			"Cmd-S": function(cm) {
				cm.IDE.syncFile();
			}
		},
	};

	window.IDE = IDE;

})(window);

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