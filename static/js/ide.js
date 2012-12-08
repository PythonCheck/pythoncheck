
(function(window) {

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
		this.listPuller = null;
		this.internalCodeMirror = null;
		this.currentCourse = false;
		this.currentProject = false;
		this.mainFile = false;
		this.currentlyOpenFiles = [];
		this.focusedFileReadURL = null;

		//this.buildHTMLStructure(appendTo)
	};

	IDE.fn = IDE.prototype = {
		constructor: IDE,

		buildHTMLStructure: function(appendTo, codeMirror, codeMirrorOptions) {
			$(appendTo)
				.append(this.tabPanel = $('<nav class="' + this.options.tabPanelClass + '"></nav>'))
				.append(this.menuPanel = $('<div class="' + this.options.menuPanelClass + '"></div>'))
				.append(this.codePanel = $('<div class="' + this.options.codePanelClass + '"></div>'))
				.append(this.filePanel = $('<div class="' + this.options.filePanelClass + '"></div>'));

			this.menuPanel.append(this.listPuller = $('<a class="icon-chevron-left icon-white ' + this.options.listTriggerClass + '"></a>'));

			if(arguments.length > 1) {
				this.codeMirror(arguments[1], arguments[2]);
			}

			this.registerActions();
		},

		registerActions: function() {
			$(this.listPuller).click(this.openFileList.bind(this));
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

			fileInformation = {
				filename: filename
			}

			if(this.currentCourse && this.currentProject) {
				fileInformation["type"] = 'exercise';
				fileInformation.course = this.currentCourse;
				fileInformation.project = this.currentProject;
			}
			else {
				fileInformation["type"] = 'project';
				fileInformation.project = this.currentProject;	
			}

			this.api(this.options.apiNew, fileInformation, 
				function(data) {
					console.log(data);
				})
		},

		populateFilePanel: function(files) {
			var list = $('<ul></ul>');
			$(this.filePanel).empty().append(list);

			if(files.courses) {
				for(var coursename in files.courses) {

					var course;
					list.append($('<li>' + coursename + '</li>').append(course = $('<ul></ul>')))

					for(var exercisename in files.courses[coursename].exercises) {
						var ex, fileObj, details; 
						course.append($('<li>' + exercisename + '</li>').append(ex = $('<ul></ul>')))

						for(var filename in files.courses[coursename].exercises[exercisename].files) {
							details = this.fileDetails(files.courses[coursename].exercises[exercisename].files[filename]);
							
							this.createFileLink(details, 'filename', ex, this.openFile.bind(this))
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
				this.currentlyOpenFiles[index].tab.text(tabText.substring(0, tabText.length-1));
			}
			// file is newly not saved (just edited)
			else if (statusChanged && !saved) {
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

			this.api(this.options.apiRun, {
				execute: file.filename,
				course: file.course,
				project: file.project
			}, function(data) {
				var interval = setInterval(function() {
					this.api(this.options.apiResult, {buildId: data.buildId}, function(resultData, resultTextStatus, resultJqXHR) {
							// if the results are ready --> PARTY!
							if(resultData.finished) {
								clearInterval(interval);
								this.results(resultData.error, resultData.output);
							}
						}.bind(this));
				}.bind(this), data.timeout || this.options.defaultTimeout);
			}.bind(this));
		},

		results: function(error, output) {
			this.output('error:', error, 'output:', output);
		},

		output: function() {
			for(var i = 0; i < arguments.length; i++) {
				console.log(arguments[i]);
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
			return this.internalCodeMirror;
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
				cm.IDE.syncFile(cm.IDE.getFocusedFile());
			}
		},
	};

	window.IDE = IDE;

})(window);

var _m;
$(function() {
	window.ide = new IDE($('#codingsohard'));
	window.ide.buildHTMLStructure($('#codingsohard'), true, {
		theme: "monokai",
		lineNumbers: true
	});
	ide.getFileList(ide.populateFilePanel.bind(ide));
	ide.openFileList();
});