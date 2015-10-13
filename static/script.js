$(function(){
	function onFormSubmit(event){
		var data = $(event.target).serializeArray();
		var thesis = {};

		for(var i = 0; i<data.length ; i++){
			thesis[data[i].name] = data[i].value;
		}

		var thesis_create_api = '/api/thesis';

		$.post(thesis_create_api, thesis, function(response){
			// read response from server
			if (response.status = 'OK') {
				var thesis_list = response.data.year + ' ' + response.data.thesisTitle + ' - by ' + response.data.first_name + ' ' + response.data.last_name;
				$('.thesis-list').prepend('<li>' + thesis_list + '<br><a href=\"/thesis/delete/'+response.data.id+'\"><button type=\"submit\">DELETE</button></a>'+ '<a href=\"/thesis/edit/'+response.data.id+'\"><button type=\"submit\">EDIT</button></a>')
				$('input:text').val('');
				$('textarea[name=abstract]').val('');
				$('select[name=year]').val('2011');
				$('select[name=section]').val('1');
			} else {

			}
		});

		return false;
	}

	function onRegister(event){
		var data = $(event.target).serializeArray();
		var user = {};

		for(var i = 0; i<data.length ; i++){
			user[data[i].name] = data[i].value;
		}

		var user_create_api = '/register';

		$.post(user_create_api, user, function(response){
			// read response from server
			if (response.status = 'OK') {
				location.href = '/home';
			}
		});

		return false;
	}

	function loadThesis(){
		var thesis_list_api = '/api/thesis';
		$.get(thesis_list_api, {} , function(response) {
			console.log('.thesis-list', response)
			response.data.forEach(function(thesis){
				var thesis_list = thesis.year + ' ' + thesis.thesisTitle + ' - by ' + thesis.first_name + ' ' + thesis.last_name;
				$('.thesis-list').append('<li>' + thesis_list + '<br><a href=\"/thesis/delete/'+thesis.id+'\"><button type=\"submit\">DELETE</button></a>'+ '<a href=\"/thesis/edit/'+thesis.id+'\"><button type=\"submit\">EDIT</button></a>' + '</li>')
			});
		});
	}

	function onCreateUniversity(event){
		var data = $(event.target).serializeArray();
		var university = {};

		for(var i = 0; i<data.length ; i++){
			university[data[i].name] = data[i].value;
		}

		var university_create_api = '/university/create';

		$.post(university_create_api, university, function(response){
			// read response from server
			if (response.status = 'OK') {
				location.href = '/home';
			}
		});

		return false;
	}

	function onCreateCollege(event){
		var data = $(event.target).serializeArray();
		var college = {};

		for(var i = 0; i<data.length ; i++){
			college[data[i].name] = data[i].value;
		}

		var college_create_api = '/college/create';

		$.post(college_create_api, college, function(response){
			// read response from server
			if (response.status = 'OK') {
				location.href = '/home';
			}
		});

		return false;
	}

	function onCreateDepartment(event){
		var data = $(event.target).serializeArray();
		var department = {};

		for(var i = 0; i<data.length ; i++){
			department[data[i].name] = data[i].value;
		}

		var department_create_api = '/department/create';

		$.post(department_create_api, department, function(response){
			// read response from server
			if (response.status = 'OK') {
				location.href = '/home';
			}
		});

		return false;
	}

	function onCreateStudent(event){
		var data = $(event.target).serializeArray();
		var student = {};

		for(var i = 0; i<data.length ; i++){
			student[data[i].name] = data[i].value;
		}

		var student_create_api = '/student/create';

		$.post(student_create_api, student, function(response){
			// read response from server
			if (response.status = 'OK') {
				location.href = '/home';
			}
		});

		return false;
	}

	function onCreateFaculty(event){
		var data = $(event.target).serializeArray();
		var faculty = {};

		for(var i = 0; i<data.length ; i++){
			faculty[data[i].name] = data[i].value;
		}

		var faculty_create_api = '/faculty/create';

		$.post(faculty_create_api, faculty, function(response){
			// read response from server
			if (response.status = 'OK') {
				location.href = '/home';
			}
		});

		return false;
	}
	
	function onCreateThesis(event){
		var data = $(event.target).serializeArray();
		var thesis = {};

		for(var i = 0; i<data.length ; i++){
			thesis[data[i].name] = data[i].value;
		}

		var thesis_create_api = '/thesis/create';

		$.post(thesis_create_api, thesis, function(response){
			// read response from server
			if (response.status = 'OK') {
				location.href = '/home';
			}
		});

		return false;
	}


    //$('.create-form').submit(onFormSubmit);
    $('.register-form').submit(onRegister);
    $('.faculty-form').submit(onCreateFaculty);
    $('.university-create-form').submit(onCreateUniversity);
    $('.college-create-form').submit(onCreateCollege);
    $('.department-create-form').submit(onCreateDepartment);
    $('.student-create-form').submit(onCreateStudent);
    $('.faculty-create-form').submit(onCreateFaculty);
    $('.thesis-create-form').submit(onCreateThesis);
    //loadThesis();
});