import webapp2
from google.appengine.ext import ndb
import jinja2
import os
import logging
import json
import urllib
from google.appengine.api import users
#from google.appengine.api import simplejson as json
import csv
import re


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

class Thesis(ndb.Model):
    year = ndb.IntegerProperty()
    thesisTitle = ndb.StringProperty(indexed=True)
    abstract = ndb.TextProperty()
    adviser = ndb.StringProperty(indexed=True)
    section = ndb.IntegerProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    userName = ndb.StringProperty(indexed=False)
    userId = ndb.StringProperty(indexed=False)
    thesis_created_by = ndb.KeyProperty(kind='User')
    thesis_department_key = ndb.KeyProperty(kind='Department')
    thesis_student_keys = ndb.KeyProperty(kind='Student',repeated=True)
    thesis_adviser_key = ndb.KeyProperty(kind='Faculty')


class User(ndb.Model):
    user_email = ndb.StringProperty(indexed=True)
    user_first_name = ndb.StringProperty(indexed=True)
    user_last_name = ndb.StringProperty(indexed=True)
    user_date = ndb.DateTimeProperty(auto_now_add=True)
    user_identity = ndb.StringProperty(indexed=False)
    user_authority = ndb.StringProperty(indexed=False)
    user_phone_number = ndb.IntegerProperty()

class Faculty(ndb.Model):
    faculty_title = ndb.StringProperty(indexed=True)
    faculty_first_name = ndb.StringProperty(indexed=True,default='')
    faculty_last_name = ndb.StringProperty(indexed=True,default='')
    faculty_email = ndb.StringProperty(indexed=True)
    faculty_phone_number = ndb.StringProperty(indexed=True)
    faculty_birthdate = ndb.StringProperty()
    faculty_picture = ndb.StringProperty(indexed=True)
    faculty_middle_name = ndb.StringProperty(indexed=True)

    @classmethod
    def get_by_key(cls, keyname):
        try:
            return ndb.Key(cls, keyname).get()
        except Exception:
            return None

class Student(ndb.Model):
    student_first_name = ndb.StringProperty(indexed=True,default='')
    student_middle_name = ndb.StringProperty(indexed=True,default='')
    student_last_name = ndb.StringProperty(indexed=True,default='')
    student_email = ndb.StringProperty(indexed=True)
    student_phone_number = ndb.StringProperty(indexed=True)
    student_number = ndb.StringProperty(indexed=True)
    student_birthdate = ndb.StringProperty()
    student_picture = ndb.StringProperty(indexed=True)
    student_year_graduated = ndb.StringProperty(indexed=True)

class University(ndb.Model):
    university_name = ndb.StringProperty(indexed=True)
    university_address = ndb.StringProperty(indexed=True)
    university_initials = ndb.StringProperty(indexed=True)

class College(ndb.Model):
    college_name = ndb.StringProperty(indexed=True)
    college_university_key = ndb.KeyProperty(indexed=True)

class Department(ndb.Model):
    department_name = ndb.StringProperty(indexed=True)
    department_college_key = ndb.KeyProperty(indexed=True)

class Greeting(ndb.Model):
    """Guestbook used as comment section"""
    author = ndb.StructuredProperty(User)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    
class CreateThesis(webapp2.RequestHandler):    
    def get(self):
        thesis = Thesis.query().order(-Thesis.date).fetch()
        thesis_list = []

        for t in thesis:
            creatorId = t.userId
            created_by = ndb.Key('User', creatorId)
            thesis_list.append({
                    'year' : t.year,
                    'thesisTitle' : t.thesisTitle,
                    'abstract' : t.abstract,
                    'adviser' : t.adviser,
                    'section' : t.section,
                    'id' : t.key.id(),
                    'userName' : t.userName,
                    'first_name' : created_by.get().first_name,
                    'last_name' : created_by.get().last_name
                })
        #return list to client
        response = {
            'result' : 'OK',
            'data' : thesis_list
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

    def post(self):
        user = users.get_current_user()
        t = Thesis()
        t.thesisTitle = self.request.get('thesisTitle')
        t.abstract = self.request.get('abstract')
        t.adviser = self.request.get('adviser')
        t.year = self.request.get('year')
        t.section = self.request.get('section')
        t.userName = user.nickname()
        t.userId = user.user_id()
        t.put()

        creatorId = t.userId
        created_by = ndb.Key('User', creatorId)

        self.response.headers['Content-Type'] = 'application/json'
        response = {
            'result' : 'OK',
            'data': {
                'year' : t.year,
                'thesisTitle' : t.thesisTitle,
                'abstract' : t.abstract,
                'adviser' : t.adviser,
                'section' : t.section,
                'id' : t.key.id(),
                'userName' : t.userName,
                'first_name' : created_by.get().first_name,
                'last_name' : created_by.get().last_name
            }
        }
        self.response.out.write(json.dumps(response))

class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('main.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/login')
            #self.redirect(users.create_login_url(self.request.uri))

class deleteThesis(webapp2.RequestHandler):
    def get(self, thesisId):
        d = Thesis.get_by_id(int(thesisId))
        d.key.delete()
        self.redirect('/')

class login(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render())
        user = users.get_current_user()
        if user:
            template = JINJA_ENVIRONMENT.get_template('main.html')
            self.response.write(template.render(template_data))

class loginurl(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        url = users.create_logout_url('/login')
        url_linktext = 'Logout'

        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            self.redirect('/register')
        else:
            #self.redirect('/login')
            self.redirect(users.create_login_url(self.request.uri))


class register(webapp2.RequestHandler):
    def get(self):
        loggedin_user = users.get_current_user()
        if loggedin_user:
            user_key = ndb.Key('User',loggedin_user.user_id())
            user = user_key.get()
            if user:
                self.redirect('/home')
            else:
                if loggedin_user:
                    template = JINJA_ENVIRONMENT.get_template('register.html')
                    logout_url = users.create_logout_url('/login')
                    template_value = {
                        'logout_url' : logout_url
                    }
                    self.response.write(template.render(template_value))
                else:
                            login_url = users.create_login_url('/register')
                            self.redirect(login_url)
        else:
            self.redirect('/login')

    def post(self):
        loggedin_user = users.get_current_user()
        user =  User(id=loggedin_user.user_id(), user_email=loggedin_user.email(), user_first_name=self.request.get('first_name').title(), user_last_name=self.request.get('last_name').title(), user_phone_number=int(self.request.get('phone_number')))
        user.put()

class editThesis(webapp2.RequestHandler):
    def get(self, thesisId):
        thesis = Thesis.get_by_id(int(thesisId))
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        template_value = {
            'thesis' : thesis,
            'user' : user,
            'url' : url
        }
        template = JINJA_ENVIRONMENT.get_template('edit.html')
        self.response.write(template.render(template_value))

    def post(self,thesisId):
        thesis = Thesis.get_by_id(int(thesisId))      
        thesis.year = int(self.request.get('year'))
        thesis.thesisTitle = self.request.get('thesisTitle')
        thesis.abstract = self.request.get('abstract')
        thesis.section = int(self.request.get('section'))
        thesis.put()
        self.redirect('/')

class importCSV(webapp2.RequestHandler):
    def post(self):

        if self.request.get('csv_name'):
            if self.request.get('csv_name').find('.csv') > 0:
                csvfile = self.request.get('csv_name')
            else:
                csvfile = False;
                error = 'file type error'
        else:
            csvfile = False;
            error = 'please import a file!'

        if csvfile:
            f = csv.reader(open(csvfile , 'r'),skipinitialspace=True)
            counter = 1
            for row in f:
                thesis = Thesis()
                th = Thesis.query(Thesis.thesisTitle == row[4]).fetch()
                if not th:
                    if len(row[7]) > 2:
                        adviser_name = row[7]
                        x = adviser_name.split(' ')
                        adv_fname = x[0]
                        adv_lname = x[1]
                        adviser_keyname = adviser_name.strip().replace(' ', '').lower()
                        adviser = Faculty.get_by_key(adviser_keyname)
                        if adviser is None:
                            adviser = Faculty(key=ndb.Key(Faculty, adviser_keyname), faculty_first_name=adv_fname, faculty_last_name=adv_lname)
                            thesis.thesis_adviser_key = adviser.put()
                        else:
                            thesis.thesis_adviser_key = adviser.key
                    else:
                        adv_fname = 'Anonymous'
                        adviser = Faculty(faculty_first_name=adv_fname, faculty_last_name=adv_lname)
                        thesis.thesis_adviser_key = adviser.put()
                    
                    for i in range(8,13):
                        stud = Student()
                        if row[i]:
                            stud_name = row[i].title().split(' ')
                            size = len(stud_name)
                            if size >= 1:
                                stud.student_first_name = stud_name[0]
                            if size >= 2:
                                stud.student_middle_name = stud_name[1]
                            if size >= 3:
                                stud.student_last_name = stud_name[2]
                            thesis.thesis_student_keys.append(stud.put())

                    university = University(university_name = row[0])
                    university.put()
                    college = College(college_name = row[1], college_university_key = university.key)
                    college.put()
                    department = Department(department_name = row[2], department_college_key = college.key)
                    thesis.thesis_department_key = department.put()

                    thesis.year = int(row[3])
                    thesis.thesisTitle = row[4]
                    thesis.abstract = row[5]
                    thesis.section = int(row[6])

                    user = users.get_current_user()
                    user_key = ndb.Key('User',user.user_id())

                    thesis.thesis_created_by = user_key
                    thesis.put()

                    adv_fname = ''
                    adv_lname = ''
                    counter=counter+1
            self.response.write('Success!<ul><a href="/home">Home</a></ul>')
        else:
            self.response.write(error)

class test(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('test.html')
        self.response.write(template.render())

class createFaculty(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('faculty_create.html')
        self.response.write(template.render())
    def post(self):
        faculty = Faculty()
        faculty.faculty_title = self.request.get('title')
        faculty.faculty_first_name = self.request.get('first_name')
        faculty.faculty_middle_name = self.request.get('middle_name')
        faculty.faculty_last_name = self.request.get('last_name')
        faculty.faculty_email = self.request.get('email')
        faculty.faculty_phone_number = self.request.get('phone_number')
        faculty.faculty_birthdate = self.request.get('birthdate')
        faculty.put()

class createStudent(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('student_create.html')
        self.response.write(template.render())
    def post(self):
        student = Student()
        student.student_first_name = self.request.get('first_name')
        student.student_middle_name = self.request.get('middle_name')
        student.student_last_name = self.request.get('last_name')
        student.student_email = self.request.get('email')
        student.student_phone_number = self.request.get('phone_number')
        student.student_birthdate = self.request.get('birthday')
        student.student_number = self.request.get('student_number')
        student.student_year_graduated = self.request.get('year_graduated')
        student.put()

class createUniversity(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('university_create.html')
        self.response.write(template.render())
    def post(self):
        university = University()
        university.university_name = self.request.get('university_name')
        university.put()

class createCollege(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('college_create.html')
        self.response.write(template.render())
    def post(self):
        college = College()
        college.college_name = self.request.get('college_name')
        college.put()

class createDepartment(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('department_create.html')
        self.response.write(template.render())
    def post(self):
        department = Department()
        department.department_name = self.request.get('department_name')
        department.put()

class createThesiss(webapp2.RequestHandler):
    def get(self):

        thesis = Thesis.query().order(-Thesis.date).fetch()
        thesis_list = []

        for t in thesis:
            thesis_list.append({
                'year' : t.year,
                'thesisTitle' : t.thesisTitle,
                'abstract' : t.abstract,
                'section' : t.section,
                'id' : t.key.id()
            })
        #return list to client
        response = {
            'result' : 'OK',
            'data' : thesis_list
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))


    # def post(self):
    #     thesis = Thesis()
    #     #thesis.university = self.request.get('university')
    #     #thesis.college = self.request.get('college')
    #     #thesis.thesis_department_key = self.request.get('department')
    #     thesis.thesisTitle = self.request.get('title')
    #     #thesis.thesis_adviser_key = self.request.get('adviser')
    #     thesis.year = int(self.request.get('year'))
    #     thesis.section = int(self.request.get('section'))
    #     thesis.abstract = self.request.get('abstract')
    #     thesis.put()

    def post(self):
        user = users.get_current_user()
        t = Thesis()
        t.thesisTitle = self.request.get('title')
        t.abstract = self.request.get('abstract')
        #t.adviser = self.request.get('adviser')
        t.year = int(self.request.get('year'))
        t.section = int(self.request.get('section'))
        t.userName = user.nickname()
        t.userId = user.user_id()
        t.put()

        self.response.headers['Content-Type'] = 'application/json'
        response = {
            'result' : 'OK',
            'data': {
                'year' : t.year,
                'thesisTitle' : t.thesisTitle
            }
        }
        self.response.out.write(json.dumps(response))

class homepage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('homepage.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/login')

class thesisListPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        universities = []
        f = Faculty.query(projection=[Faculty.faculty_first_name,Faculty.faculty_last_name]).order(+Faculty.faculty_last_name).fetch()
        u = University.query(projection=[University.university_name]).order(+University.university_name).fetch()
        for univ in u:
            if univ.university_name not in universities:
                universities.append(univ.university_name)
        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'faculty':f,
            'universities':universities
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('thesis_list.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/login');

class thesisList(webapp2.RequestHandler):
    def get(self):
        thesis_list = []
        if self.request.get('year').isdigit():
            filt_year = int(self.request.get('year'))
        else:
            filt_year = None
        filt_adviser = self.request.get('adviser')

        if filt_adviser:
            x = filt_adviser.split(' ')
            filt_adv_fname = x[0]
            f = Faculty.query(Faculty.faculty_first_name == filt_adv_fname).fetch()
            for faculty in f:
                filt_adv_key = faculty.key
        else:
            filt_adv_key = None

        filt_university = self.request.get('university')

        if filt_university:
            filt_univ = University.query(University.university_name == filt_university).get()
            filt_col = College.query(College.college_university_key == filt_univ.key).get()
            filt_dept = Department.query(Department.department_college_key == filt_col.key).get()
        else:
            filt_dept = None

        if filt_year and filt_university and filt_adv_key:
            thesis = Thesis.query(Thesis.year == filt_year,Thesis.thesis_department_key == filt_dept.key,Thesis.thesis_adviser_key == filt_adv_key).order(+Thesis.thesisTitle).fetch()
        elif filt_year and filt_university:
            thesis = Thesis.query(Thesis.year == filt_year,Thesis.thesis_department_key == filt_dept.key).order(+Thesis.thesisTitle).fetch()
        elif filt_year and filt_adv_key:
            thesis = Thesis.query(Thesis.year == filt_year,Thesis.thesis_adviser_key == filt_adv_key).order(+Thesis.thesisTitle).fetch()
        elif filt_university and filt_adv_key:
            thesis = Thesis.query(Thesis.thesis_department_key == filt_dept.key,Thesis.thesis_adviser_key == filt_adv_key).order(+Thesis.thesisTitle).fetch()
        elif filt_year:
            thesis = Thesis.query(Thesis.year == filt_year).order(+Thesis.thesisTitle).fetch()
        elif filt_adv_key:
            thesis = Thesis.query(Thesis.thesis_adviser_key == filt_adv_key).order(+Thesis.thesisTitle).fetch()
        elif filt_university:
            thesis = Thesis.query(Thesis.thesis_department_key == filt_dept.key).order(+Thesis.thesisTitle).fetch()
        else:
            thesis = Thesis.query().order(+Thesis.thesisTitle).fetch()

        for thes in thesis:
            d = ndb.Key('Department',thes.thesis_department_key.id())
            dept = d.get()
            dept_name = dept.department_name
            
            c = ndb.Key('College',dept.department_college_key.id())
            col = c.get()
            col_name = col.college_name

            u = ndb.Key('University',col.college_university_key.id())
            univ = u.get()
            univ_name = univ.university_name

            creator = thes.thesis_created_by.get()

            if thes.thesis_adviser_key:
                adv = thes.thesis_adviser_key.get()
                adv_fname = adv.faculty_first_name
                adv_lname = adv.faculty_last_name
            else:
                adv = None
                adv_fname = None
                adv_lname = None

            thesis_list.append({
                'self_id':thes.key.id(),
                'thesis_title':thes.thesisTitle,
                'thesis_year':thes.year,
                'faculty_first_name':adv_fname,
                'faculty_last_name':adv_lname,
                'thesis_creator_fname':creator.user_first_name,
                'thesis_creator_lname':creator.user_last_name,
                })

        if thesis_list:
            response = {
                'status':'OK',
                'data':thesis_list
            }
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(response))
        else:
            response = {
                'status':'Error',
            }
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(response))

    def post(self):
        th = Thesis.query(Thesis.thesisTitle == self.request.get('thesisTitle')).fetch()
        thesis = Thesis()
        thesis.thesisTitle = self.request.get('thesisTitle')
        thesis.abstract = self.request.get('abstract')
        thesis.year = int(self.request.get('year'))
        thesis.section = int(self.request.get('section'))

        proponents = []
        if self.request.get('thesis_member1'):
            proponents.append(self.request.get('thesis_member1'))
        if self.request.get('thesis_member2'):
            proponents.append(self.request.get('thesis_member2'))
        if self.request.get('thesis_member3'):
            proponents.append(self.request.get('thesis_member3'))
        if self.request.get('thesis_membe4'):
            proponents.append(self.request.get('thesis_member4'))
        if self.request.get('thesis_member5'):
            proponents.append(self.request.get('thesis_member5'))

        adviser = self.request.get('adviser')
        univ = self.request.get('university')
        col = self.request.get('college')
        dept = self.request.get('department')

        if len(th) >= 1:
            self.response.headers['Content-Type'] = 'application/json'
            response = {
                'status':'Cannot create thesis. Title may be already exist'
            }
            self.response.out.write(json.dumps(response))

        else:
            for i in range(0,len(proponents)):
                name = proponents[i].title().split(' ')
                size = len(name)
                s = Student()
                if size >= 1:
                    s.student_first_name = name[0]
                if size >= 2:
                    s.student_middle_name = name[1]
                if size >= 3:
                    s.student_last_name = name[2]
                thesis.thesis_student_keys.append(s.put())

            if len(adviser) > 2:
                adviser_name = adviser
                x = adviser_name.title().split(' ')
                sizex = len(x)
                if sizex >= 1:
                    adv_fname = x[0]
                else:
                    adv_fname = None

                if sizex >= 2:
                    adv_midname = x[1]
                else:
                    adv_midname = None

                if sizex >= 3:
                    adv_lname = x[2]
                else:
                    adv_lname = None

                adviser_keyname = adviser_name.strip().replace(' ', '').lower()
                adv = Faculty.get_by_key(adviser_keyname)
                if adv is None:
                    adv = Faculty(key=ndb.Key(Faculty, adviser_keyname), faculty_first_name=adv_fname, faculty_last_name=adv_lname, faculty_middle_name=adv_midname)
                    thesis.thesis_adviser_key = adv.put()
                else:
                    thesis.thesis_adviser_key = adv.key
            else:
                adv_fname = 'Anonymous'
                adv = Faculty(faculty_first_name=adv_fname, faculty_last_name=adv_lname)
                thesis.thesis_adviser_key = adv.put()


            university = University(university_name = univ)
            university.put()
            college = College(college_name = col, college_university_key = university.key)
            college.put()
            department = Department(department_name = dept, department_college_key = college.key)
            thesis.thesis_department_key = department.put()

            user = users.get_current_user()
            user_key = ndb.Key('User',user.user_id())

            thesis.thesis_created_by = user_key

            thesis.put()

            self.response.headers['Content-Type'] = 'application/json'
            response = {
            'status':'OK'
            }
            self.response.out.write(json.dumps(response))

class createThesisPage(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        universities = []
        colleges = []
        departments = []

        f = Faculty.query(projection=[Faculty.faculty_first_name,Faculty.faculty_last_name]).order(+Faculty.faculty_last_name).fetch()
        u = University.query(projection=[University.university_name]).order(+University.university_name).fetch()
        c = College.query(projection=[College.college_name]).order(+College.college_name).fetch()
        d = Department.query(projection=[Department.department_name]).order(+Department.department_name).fetch()

        for univ in u:
            if univ.university_name not in universities:
                universities.append(univ.university_name)

        for col in c:
            if col.college_name not in colleges:
                colleges.append(col.college_name)

        for dept in d:
            if dept.department_name not in departments:
                departments.append(dept.department_name)

        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'faculty':f,
            'universities':universities,
            'colleges' : colleges,
            'departments' : departments
        }

        template = JINJA_ENVIRONMENT.get_template('thesis_create.html')
        self.response.write(template.render(template_data))


class thesisDetails(webapp2.RequestHandler):
    def get(self, thesisId):
        thesis = Thesis.get_by_id(int(thesisId))
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        template_value = {
            'thesis' : thesis,
            'user' : user,
            'url' : url
        }
        template = JINJA_ENVIRONMENT.get_template('thesis_details.html')
        self.response.write(template.render(template_value))

    # def post(self,thesisId):
    #     thesis = Thesis.get_by_id(int(thesisId))      
    #     thesis.year = int(self.request.get('year'))
    #     thesis.thesisTitle = self.request.get('thesisTitle')
    #     thesis.abstract = self.request.get('abstract')
    #     thesis.section = int(self.request.get('section'))
    #     thesis.put()
    #     self.redirect('/')

app = webapp2.WSGIApplication([
    ('/home', homepage),
    ('/', homepage),
    ('/api/thesis', createThesiss),
    ('/thesis/delete/(.*)', deleteThesis),
    ('/login', login),
    ('/loginurl', loginurl),
    ('/register', register),
    ('/thesis/edit/(.*)',editThesis),
    ('/importCSV', importCSV),
    ('/test', test),
    ('/faculty/create' , createFaculty),
    ('/student/create' , createStudent),
    ('/university/create' , createUniversity),
    ('/college/create' , createCollege),
    ('/department/create' , createDepartment),
    ('/thesis/create' , createThesisPage),
    ('/thesis/page', thesisListPage),
    ('/thesis/list', thesisList),
    ('/thesis/details/(.*)', thesisDetails)

], debug=True)