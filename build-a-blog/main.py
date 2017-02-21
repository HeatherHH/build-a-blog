#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
from string import letters
import webapp2
import jinja2
import cgi

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                            autoescape = True)

def render_str(template, **params): #"**params" is python syntax for extra parameters
        t = jinja_env.get_template(template)
        return t.render(params)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#class Art(db.Model): #this allows us to create an entity
#    title = db.StringProperty(required = True)
#    art = db.StringProperty(required = True)
#    created = db.DateTimeProperty(auto_now_add = True) #automatically attached DateTime stamp to all entries to our database

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class MainPage(BlogHandler):
    #def render_front(self, title="", art="", error=""):
    #    arts = db.GqlQuery("SELECT * FROM Art " #this is how we run a query
    #                    "ORDER BY created DESC")
    #    self.render("front.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.write("Heather's Build-a-Blog<br>file: main.py<br><a href = '/blog/'>See Past Posts</a>")
        #self.render_front()
#BLOG STUFF
def blog_key(name = 'default'): #this helps sort the database entries, it serves as the parent?
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)    #must exist and be less than 500 characters, StringProperty can be indexed
    content = db.TextProperty(required = True) #must exist, text property can be more than 500 characters, TextProperty cannot be indexed, TextProperty can also have new lines (like returns)
    created = db.DateTimeProperty(auto_now_add = True) #this entry will be created automatically when user makes a blog entry
    last_modified = db.DateTimeProperty(auto_now = True)#everytime we update an object, this automatically notes the time it was updated

    def render(self):
        self._render_text = self.content.replace('\n','<br>')#this replaces line breaks made my user and replaces them with html-coded line breaks to force the line breaks to happen
        return render_str("post.html", p = self)

class BlogFront(BlogHandler):
    def get(self):
        #posts = Post.all().order('-created')#this looks up all the old posts ordered by creation time, steve says this could have been done just as easily with GQL, but he wanted to try something new
        posts = db.GqlQuery("SELECT * FROM Post ORDER by created DESC LIMIT 10")#this is the GqlQuery code which could be used instead of the code in the previous line
        self.render('front.html', posts = posts)

class PostPage(BlogHandler):#this is a page for a particular post
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent = blog_key())
        post = db.get(key)
        if not post:
            self.error(404)
            return
        self.render("permalink.html", post = post)

class NewPost(BlogHandler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put() #this adds the input to our database
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "Please enter BOTH and Post Title and a Post Message"
            self.render("newpost.html", subject = subject, content = content, error = error)


#    def post(self):
#        title = self.request.get("title")
#        art = self.request.get("art")
#        if title and art:
#            a  = Art(title = title, art = art) #making a new art
#            a.put() #stores the input to our database
#            self.redirect("/")
##            self.write("thanks!")
#        else:
#            error = "we need both a title and some artwork"
#            self.render_front(title, art, error)

#class FizzBuzzHandler(Handler):
#    def get(self):
#        n = self.request.get('n', 0)
#        n = n and int(n)
#        self.render('fizzbuzz.html', n = n)


###### Unit 2 HW's
class Rot13(BlogHandler):
    def get(self):
        self.render('rot13-form.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')

        self.render('rot13-form.html', text = rot13)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):

    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username = username,
                      email = email)

        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.redirect('/unit2/welcome?username=' + username)

class Welcome(BlogHandler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
            self.redirect('/unit2/signup')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('unit2/rot13', Rot13),
    ('/unit2/signup', Signup),
    ('/unit2/welcome', Welcome),
    ('/unit2/welcome', BlogFront),
    ('/blog/([0-9]+)', PostPage),
    ('/blog/newpost', NewPost),
], debug=True)
