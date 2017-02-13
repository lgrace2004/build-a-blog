import os
import webapp2
import jinja2
import time


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entry(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        self.redirect('/blog')



class NewPost(Handler):

    def render_newpostform(self, title="", entry="", error=""):
        self.render("newpost.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_newpostform()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            #creates a new instance of Entry, called e
            e = Entry(title=title, entry = entry)
            #stores new Entry object in database:
            e.put()
            time.sleep(1)
            new_route = "/blog/" + str(e.key().id())
            self.redirect(new_route)

        else:
            error = "Error: please enter both a title and an entry"
            self.render_newpostform(title, entry, error)

class MainBlog(Handler):

    def render_topfive(self, title="", entry=""):
        #run a query:
        entries = db.GqlQuery("SELECT * from Entry ORDER BY created DESC LIMIT 5")
        self.render("topfive.html", title=title, entry=entry, entries=entries)

    def get(self):
        self.render_topfive()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")
        self.response.write(title, entry)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):

        blog_id= Entry.get_by_id(int(id))
        if blog_id == None:
            error = "ERROR: No post associated with this id."
            self.response.write(error)
        else:
            self.response.write(blog_id.title)
            self.response.write("<html><body><br><br></body></html>")
            self.response.write(blog_id.entry)



app = webapp2.WSGIApplication([
    ('/' , MainHandler),
    ('/blog', MainBlog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
