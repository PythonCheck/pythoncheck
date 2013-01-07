// depends on 
// Utils
(function(window) {

	// defaults for exercise projects
	// exercises may only contain a single file
	var EXERCISE_CONTAINS_SINGLE_FILE = true;
	// this file is called like this
	var EXERCISE_MAIN_FILE = 'main.py';

	// these are the default options for the IDE and can be modified after
	// initalizing by ideInstance.options['optionName'] = 'anything'
	// or during initializing by
	// new IDE(obj, {options go in here....})
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
		maxApiFailures: 4,
		fileListWidth: 250,
		defaultCommandSuffix: '/index.commandline',
		loaderImageURL: 'static/images/ajax-loader.gif',
		loadingImageClass: 'loading',

		filePanelOptions: {
			headerTag: '<h4></h4>',
			childContainer: '<div></div>',
			childTag: '<a></a>',
			childContainerInHeader: false,
			container: false,
			useJQUIAccordion: true,
			accordionOptions: {
				header: 'h4',
				heightStyle: 'content'
			}
		}

	};

	// constructor
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

		// builds the HTML structure needed into the given div
		// possible calls:
		// (jqObj) -- only adds the html structure assuming that codeMirror will be called extra
		// (jqObj, a, b) -- adds html structure
		buildHTMLStructure: function(appendTo, codeMirror, codeMirrorOptions) {
			$(appendTo)
				.append(this.tabPanel = $('<nav class="' + this.options.tabPanelClass + '"></nav>'))
				.append(this.menuPanel = $('<nav class="' + this.options.menuPanelClass + '"></nav>'))
				.append(this.codePanel = $('<div class="' + this.options.codePanelClass + '"></div>'))
				.append(
					this.filePanel = $('<div class="' + this.options.filePanelClass + '"></div>')
						// .append(
						// 	this.filePanelMenu = $('<nav></nav>')
						// 		 .append($('<a>New File</a>'))
						// )
						.append(
							this.filePanelContent = $('<section class="filelist"></section>')
						)
				);

			this.menuPanel
				.append($('<a>Run</a>').on('click',    function() { this.run();      }.bind(this)))
				.append($('<a>Save</a>').on('click',   function() { this.syncFile(); }.bind(this)))
				.append($('<a>Submit</a>').on('click', function() { this.submit();   }.bind(this)))
				.append(this.listPuller = $('<a class="' + this.options.listTriggerClass + '">Files</a>'));

			if(arguments.length > 1) {
				this.codeMirror(arguments[1], arguments[2]);
			}

			this.registerActions();
		},

		// instantiates drag'n'drop or reads the text of the dropped file and sets it as content of CodeMirror
		//
		// returns: undefined
		//
		// possible calls:
		// (dropZone) -- initiate the drag'n'drop. Every drop over the dropZone is caught. dropZone can be a selector or a $-Objects
		// (event) -- reads the dropped files content and sets it as the CodeMirror's content, if the CodeMirror is not readonly
		dragNDrop: function() {
			if(!this.dragNDropInitialized && arguments.length == 1 && (typeof(arguments[0]) == 'string' || arguments[0].on)) {
				var dropZone = $(arguments[0]);
				dropZone.on('drop', this.dragNDrop.bind(this));
				this.dragNDropInitialized = true;
			}
			else {
				var e = arguments[0].originalEvent;
				var files = e.dataTransfer.files;
				if(files.length > 0) {
					var file = files[0];
					var reader = new FileReader();

					reader.onload = function(evt) {
							if(this.internalCodeMirror.getOption('readOnly') === false) {
								this.internalCodeMirror.setValue(reader.result);
							}
						}.bind(this);

					reader.readAsText(file);
				}
			}
		},

		console: function(terminal) {
			if(arguments.length == 0) {
				return this.terminal;
			}
			else if(arguments.length >= 1 && 
				typeof(terminal.output) == 'function' && typeof(terminal.success) == 'function' && typeof(terminal.error) == 'function') {
				this.terminal = terminal;

				this.terminal.remote = function() {
					// just add the default command suffix and then send it to the api
					arguments[0] += this.options.defaultCommandSuffix;
					this.api.apply(this, arguments);
				}.bind(this);
			}
		},

		// adds event handlers to the IDE
		// 
		// currently the following handers are attached:
		// * the button triggering the fileList (using $.click())
		// * the codemirror on any change, used for chaning the saved-state (using cm.setOption('onChange'))
		// 
		// returns: undefined
		registerActions: function() {
			// file list
			$(this.listPuller).click(this.openFileList.bind(this));

			// save/edit actions
			this.internalCodeMirror.setOption('onChange', this.contentUpdated.bind(this));
		},

		// checks if the focused file is saved or not
		// to do this the currently focused file is retrieved and checked if the content of the textpane is the same as
		// the text in the file obj 
		//
		// returns: undefined
		contentUpdated: function(cm, changeObject) {
			var file = this.getFocusedFile();
			
			this.saved(file, cm.getValue() == file.content);
		},

		// opens the file list panel and changes the event listeners on the triggers
		// 
		// returns: undefined
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

		// closes the file list panel and changes the event listeners on the triggers
		// 
		// returns: undefined
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

		// creates a new file using the current IDE state
		// the states used are:
		// * currentCourse
		// * currentProject
		//
		// possible calls:
		// (fileName) -- 	if both currentCourse and currentProject are set a new file in the current exercise is created
		//					or
		//					if only currentProject is set, a new file in the current project is created
		// ({project: ..., course: ..., filename: ...}) -- a option object is given including project, course and filename,
		// 													then a file is created using all this information (only for exercises!)
		// 
		// returns: true if all neccessary information was given, false otherwise
		newFile: function(filename) {
			fileInformation = {};

			if(typeof(filename) == 'string') {
				fileInformation.filename = filename;

				if(this.currentCourse && this.currentProject) {
					fileInformation["type"] = 'exercise';
					fileInformation.course = this.currentCourse;
					fileInformation.project = this.currentProject;
				}
				else if (this.currentProject) {
					fileInformation["type"] = 'project';
					fileInformation.project = this.currentProject;	
				}
				else {
					return false;
				}
			}
			else if (typeof(filename) == 'object') {
				fileInformation = filename;
				if(!fileInformation.filename || ! fileInformation.project || !fileInformation.course) {
					return false;
				}

				fileInformation['type'] = 'exercise';
				fileInformation.project = filename.project;
				fileInformation.course = filename.course;
			}

			this.api(this.options.apiNew, fileInformation, 
				function(data) {
					this.getFileList(this.populateFilePanel.bind(this));
				}.bind(this));

			return true;
		},

		// clears the entire file panel and repopulates it using the files given. The files param is an object and has to have the following format:
		// {
		// 	'courses': {
		// 		'course1': {
		// 			'exercises': {
		// 				'exerciseA': {
		// 					'files': {
		// 						"file1.py": {
		// 							"edited": "2012-12-31 02:10:29",
		// 							"unique_identifier": "...",
		// 							"readURL": "...",
		// 							"filename": "file1.py",
		// 							"course": 1,
		// 							"version": null,
		// 							"saveURL": "..."
		// 						}
		// 					}
		// 				}
		// 			}
		// 		}	
		// 	}
		// 	"projects": {
		// 		"p1": {
		// 			"files": {
		// 				"file2.py": {
		// 					"edited": "2012-12-31 02:10:29",
		// 					"unique_identifier": "...",
		// 					"readURL": "...",
		// 					"filename": "file2.py",
		// 					"project": "p1",
		// 					"course": null,
		// 					"version": null,
		// 					"saveURL": "..."
		// 				}
		// 			}
		// 		}
		// 	}
		// }
		//
		// returns: undefined
		populateFilePanel: function(files) {
			var options = this.options.filePanelOptions;
			var headerTag = /*'<h4></h4>'*/'<li></li>';
			var childContainer = '<ul></ul>';
			var childTag = /*'<div></div>'*/'<li></li>';

			var childContainerInHeader = false;
			var container = $('<ul></ul>');

			$(this.filePanelContent).empty();

			var list;
			// if the container is given, insert it into the file panel
			if(options.container) {
				$(this.filePanelContent).append(list = container);
			}
			// otherwise the filepanel is the container
			else {
				list = $(this.filePanelContent);
			}

			if(files.courses) {
				for(var coursename in files.courses) {

					var course;
					var courseCaption;

					courseCaption = $(options.headerTag).append(coursename);
					course = $(options.childContainer);

					// put the caption into the container
					list.append(courseCaption);	

					if(options.childContainerInHeader) {
						courseCaption.append(course)
					}
					else {
						courseCaption.after(course);
					}
					
					
					// give data to the html objects
					courseCaption.attr({
						'data-type': 'course',
						'data-course': files.courses[coursename].id
					});

					for(var exercisename in files.courses[coursename].exercises) {
						var ex, fileObj, details, exerciseCaption; 
						
						//TODO this is ugly, should be replaced by server side counting
						var numberOfFiles = (Utils.numberOfProperties(files.courses[coursename].exercises[exercisename].files));
						if(numberOfFiles == 0) {

							// this is the descriptor of a non existing file, that will be used to create a file
							// whenever the user tries to open that file
							details = {
								'exercisename': exercisename,
								'filename': EXERCISE_MAIN_FILE,
								'course': files.courses[coursename].id,
								'project': files.courses[coursename].exercises[exercisename].id
							}

							course.append(this.createFileLink(details, 'exercisename', this.newFile.bind(this)));
						}
						else {
							// chooses the last file found
							for(var k in files.courses[coursename].exercises[exercisename].files) {
								details = files.courses[coursename].exercises[exercisename].files[k];
							}
							details.filename = exercisename;

							course.append(this.createFileLink(details, 'filename', this.openFile.bind(this)));
						}
					
					}
				}
			}
			
			if (files.projects) {
				for(var projectname in files.projects) {
					var project;

					var projectCaption = $(options.headerTag).append(projectname);
					var project = $(options.childContainer);
					
					list.append(projectCaption);

					if(options.childContainerInHeader) {
						projectCaption.append(project)
					}
					else {
						projectCaption.after(project);
					}

					for(var filename in files.projects[projectname].files) {
						details = this.fileDetails(files.projects[projectname].files[filename]);

						project.append(this.createFileLink(details, 'filename', this.openFile.bind(this)))
					}
				}
			}

			if(options.useJQUIAccordion) {
				if(list.hasClass('ui-accordion')) {
					list.accordion('destroy');
				}

				list.accordion(options.accordionOptions);
			}
		},

		// creates a link for a file in the filepanel
		//
		// The link will have the following format:
		// <li>details.nameProperty</li> and will be appended to $(appendTo)
		// Additionaly a onclick callback will be added (using on('click')). When a click occurs, the callback will be called like so
		// callback(details)
		//
		// returns: undefined
		createFileLink: function(details, nameProperty, callback) {
			var options = this.options.filePanelOptions;
			var item = $(options.childTag);
			var title;

			// set the title/text of the link
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
			return item;
		},

		// filters neccessary information out of a fileObject
		// 
		// returns: a file object containing filename, readURL, saveURL, version, edited, project and course
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

		// opens a file using the readURL in the file object given. if the file is open already, the file is focused
		// additionaly, the CodeMirror will be set to not readOnly
		// 
		// opening a file includes adding a tab for it, pushing it to the currentlyOpenFiles array, syncing it and focusing it
		// 
		// returns: undefined
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

		// saves a files content to the server. on success this.saved(fileObj, true) is called
		// 
		// note, that saving a file does also affect the file object, but syncing is recommended!
		//
		// returns: undefined
		// 
		// possible calls:
		// (fileObj, callbackFunction) -- the CodeMirror's current content will be saved into the file object and on the server. 
		// 									on success, the callbackFunction will be called
		// (fileObj, content, callbackFunction) -- the given content will be saved into the file object and on the server
		// 											on success, the callbackFunction will be called
		// (fileObj, {success: function(){...}, error: function(){...} }) -- see #1, additionaly an error callback can be specified
		// (fileObj, content, {success: function(){...}, error: function(){...} }) -- see #2, additionaly an error callback can be specified
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

			file.content = data.code;
		},

		// sets the saved state of a file, including the visual representation (e.g. adding/removing a '*' to the tab)
		// 
		// returns: if called with only the fileObj the saved state of the file, undefined otherwise
		//
		// possible calls:
		// (fileObj) -- returns the saved state of the fileObj
		// (bool) -- sets the saved state of the currently focused file
		// (fileObj, bool) -- set the saved state of the given fileObj
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

		// sets the updating state of a file including the visual representation (e.g. adding/removing an image to the tab)
		//
		// returns: if called with only the fileObj the saved state of the file, undefined otherwise
		//
		// possible calls:
		// (fileObj) -- returns the insync state of the fileObj
		// (bool) -- sets the insync state of the currently focused file
		// (fileObj, bool) -- set the insync state of the given fileObj
		updating: function(file, currentlyUpdating) {
			if(arguments.length == 1) {
				return file.insync;
			}

			if(typeof(file) == 'boolean') {
				currentlyUpdating = file;
				file = this.currentlyFocusedFile();
			}

			if(!file.tab) {
				file = this.getOpenFile(file);
				if(!file.tab) {
					return false;
				}
			}

			var image = $('<img class="' + this.options.loadingImageClass + '" src="' + this.options.apiURL + this.options.loaderImageURL + '" />');

			if(currentlyUpdating) {
				file.tab.append(image);
				file.insync = true;
			}
			else {
				file.tab.find('img').remove();
				file.insync = false;
			}
		},

		// syncs a file, taking care of saving:
		// * if a file is unsaved: save it, then sync it
		// * if a file is saved: just sync it
		// this functions uses sync() 
		// 
		// returns: undefined
		syncFile: function(fileObj) {
			if(!fileObj) {
				fileObj = this.getFocusedFile();
			}

			var openFile = this.getOpenFile(fileObj);

			if(openFile.readURL == fileObj.readURL) {
				if(this.saved(openFile)) { // check if the file is saved
					this.sync(openFile);
				}
				else {
					// file is unsaved --> save it, then sync
					this.saveFile(openFile, function() {
						this.sync(openFile);
					}.bind(this));
				}
			}
		},

		// syncs a file. CAUTION: If a file is unsaved, all data will be lost. it is therefore recommended to use syncFile()
		//
		// returns: undefined
		sync: function(fileObj) {
			this.updating(fileObj, true)
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
				this.updating(details, false)
			}.bind(this));
		},

		// retrieves the file object for the currently focused file
		getFocusedFile: function() {
			return this.getOpenFile({readURL: this.focusedFileReadURL});
		},

		// retrieves the complete file object for an incomplete file object given
		//
		// returns: the file object if found or null otherwise
		//
		// possible calls:
		// (fileObj) -- returns the fileObj (same as (fileObj, 0))
		// (fileObj, indexNumber) -- returns the fileObj starting to search at indexNumber
		// (fileObj, bool) -- returns the fileObj's index in the currentlyOpenFiles array
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

		// shortcut for getOpenFile(file, true) -- retrieves the index of a file in the currentlyOpenFiles array
		getOpenFileIndex: function(file) {
			return this.getOpenFile(file, true);
		},

		// creates a tab for a file: <a>Text</a>. Additionaly an onclick action listener (using on('click')) is added
		//
		// The signature of the callback is as follows:
		// function(details) -- the file details are passed as an argument
		//
		// The titleAttribute is the name of the property in the fileObj containing the text of the link
		// 
		// returns: the tab ($-Object)
		//
		// possible calls:
		// (file, titleAttribute, callback) -- creates a tab
		createFileTab: function(file, titleAttribute, callback) {
			var tab = $('<a>' + file[titleAttribute] + '</a>');
			tab.on('click', function() {
				callback(file);
			});
			return tab;
		},

		// focuses a file that is already open
		// 
		// Focusing a file includes setting it's tab to active and modifying the CodeMirror's content
		//
		// returns: true if the focus was successfull, false otherwise (e.g. the file wasn't open)
		//
		// possible calls:
		// (file) -- focuses the given file
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

		// updates the CodeMirror view (e.g. switching files)
		//
		// returns: false
		//
		// possible calls:
		// () -- the content of the file object is set as content of the CodeMirror (which means, that all changes are gone)
		// (openFile) -- the content of openFile is set as content of the CodeMirror. Before setting the content, the CodeMirror's content
		//					is saved back to the currently focused file object (shortcut for (openFile, false))
		// (openFile, ignoreContents) -- the content of openFile is set as content of the CodeMirror. If ignoreContents is true, 
		//									the CodeMirror's content will not be saved to the currently focused file 
		//									(which means, that all changes are gone)
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
			}

			// enable the change function
			this.internalCodeMirror.setOption('onChange', changeFunction);

		},

		// requests a build on the server.
		//
		// possible calls:
		// () -- the currently focused file is the main file
		// (file) -- the given file is the main file
		run: function(file) {
			if(!file) {
				file = this.getFocusedFile();
			}

			var run = function() { 
				this.success('Compiling....')

				this.api(this.options.apiRun, {
					execute: file.filename,
					course: file.course,
					project: file.project
				}, function(data) {
					this.results(data);
				}.bind(this), this.serverRespondedWithError.bind(this));
			}.bind(this);

			if(this.saved(file)) {
				run();
			}
			else {
				this.saveFile(file, run);
			}

			
		},

		// requests a submission on the server.
		//
		// possible calls:
		// () -- the currently focused file is the main file
		// (file) -- the given file is the main file
		submit: function(file) {
			if(!file) {
				file = this.getFocusedFile();
			}

			var submit = function() {
				this.api(this.options.apiSubmit, {
					execute: file.filename,
					course: file.course,
					project: file.project
				}, function(data) {
					this.results(data, function() {
						console.log('submitted');
					});
				}.bind(this), this.serverRespondedWithError.bind(this));
			}.bind(this);

			if(this.saved(file)) {
				submit();
			}
			else {
				this.saveFile(file, submit);
			}
			
		},

		// manages results of builds (either run or submit)
		// 
		// buildData contains the response of API regarding the build request. It has to include the buildId
		//
		// returns: undefined
		//
		// possible calls:
		// (buildData) -- wait for the results requesting a result every this.options.defaultTimeout or buildData.timeout
		// 					when the results are ready call results(error, output)
		// (buildData, callbackFunction) -- wait for the results requesting a result every this.options.defaultTimeout or buildData.timeout
		// 									when the results are ready call results(error, output) and then 
		//									callbackFunction({error: ..., output: ..., requestData: buildData})
		// (error, output) -- adds both strings to the console
		results: function(error, output) {
			// results({ obj with build data }) or results({ obj with build data }, callback)
			if(typeof(arguments[0]) == 'object' && (arguments.length == 1) || (arguments.length == 2 && typeof(arguments[1]) == 'function')) {
				var data = arguments[0];
				var callback;
				
				if(arguments.length == 2 && typeof(arguments[1]) == 'function') {
					callback = arguments[1];
				}

				var failureCount = 0;
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
						}.bind(this), function(resultJqXHR, resultTextStatus, errorThrown) {
							if(resultJqXHR.status == 422 && failureCount++ > this.options.maxApiFailures) {
								clearInterval(interval);
								this.error('Couldn\'t get results: ' + errorThrown);
							}
							else if(resultJqXHR.status == 500) {
								clearInterval(interval);
								result = $.parseJSON(resultJqXHR.responseText);
								if(result.error) {
									this.error(result.error);
								}

							}
						}.bind(this)
						);
				}.bind(this), data.timeout || this.options.defaultTimeout);
			}
			// results(str, str) output the results
			else {
				this.success('Build finished:')
				if(error) {
					this.error(error);
				}
				if(output) {
					this.output(output);
				}
			}
		},

		// calls to the api, retrieving the file list. On success callback will be called (see this.api for signature).
		getFileList: function(callback) {
			this.api(this.options.apiList, {}, callback)
		},

		// initiates the codeMirror instance for this IDE
		//
		// the CodeMirror will be set to readonly
		//
		// returns: the internalCodeMirror
		//
		// possible calls
		// (true, options) -- a new CodeMirror instance will created using the given options + the default options
		// (codeMirrorInstance) -- the given instance will be used for the IDE
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

		// adds output to the console
		//
		// possible calls:
		// (string, ...) -- adds output to the console using console(wrapInSpan(htmlify(string)), errorWrapperClass)
		error: function () {
			this.terminal.error.apply(this.terminal, arguments);
		},

		// adds output to the console
		//
		// possible calls:
		// (string, ...) -- adds output to the console using console(wrapInSpan(htmlify(string)), neutralWrapperClass)
		output: function() {
			this.terminal.output.apply(this.terminal, arguments);
		},

		// adds output to the console
		//
		// possible calls:
		// (string, ...) -- adds output to the console using console(wrapInSpan(htmlify(string)), successWrapperClass)
		success: function () {
			this.terminal.success.apply(this.terminal, arguments);
		},

		// makes an ajax-call to the api using the global options
		//
		// returns: undefined
		//
		// callback function signature:
		// function(resultData, resultTextStatus, resultJqXHR) -- further information see http://api.jquery.com/jQuery.ajax/ (search for success)
		//
		// possible calls:
		// (actionString, dataObj, callbackFunction) -- calls to the api using given actionString and the given data. 
		//												If successfull the callbackFunction will be called
		// (actionString, dataObj, callbackFunction, errorCallback) -- calls to the api using given actionString and the given data. 
		//												If successfull the callbackFunction will be called. If an error occurs,
		// 												the errorCallback will be called
		// (actionString, callbackFunction) -- calls to the api using given actionString and no data. 
		//										If successfull the callbackFunction will be called
		// (actionString, callbackFunction, errorCallback) -- calls to the api using given actionString and no data. 
		//													If successfull the callbackFunction will be called. If an error occurs,
		// 													the errorCallback will be called
		api: function(action, data, callback, errorCallback) {
			if(typeof(data) == 'function') {
				errorCallback = callback;
				callback = data;
				data = {};
			}

			$.ajax({
				type: 'POST',
				url: this.options.apiURL + action,
				data: data,
				dataFormat: 'JSON',
				success: callback, 
				error: errorCallback
			});
		},

		serverRespondedWithError: function(jqXHR, textStatus, errorThrown) {
			error = $.parseJSON(jqXHR.responseText);
			if(error.error) {
				this.error(error.error);
			}
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