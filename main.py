import webapp2
import jinja2
import os
from google.appengine.ext import db
from google.appengine.api import users
import datetime
from google.appengine.api import mail


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       autoescape=True)

class Items(db.Model): #key_name = key_date
    Title = db.StringProperty()
    Seller = db.UserProperty()
    Description = db.StringProperty()
    Price = db.StringProperty()
    Creation_Date = db.StringProperty()
    Key_Date = db.StringProperty()
    Comments = db.ListProperty(str)

class Profile(db.Model): #key_name = email
    Name = db.StringProperty()
    Items = db.StringProperty()

class Login(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            url_red = ('/browse')
            urltext_red = 'Browse'
            url_blue = (users.create_logout_url("/"))
            urltext_blue = 'Log Out'
            
        else:
            # login link
            url_red = users.create_login_url(self.request.uri)
            urltext_red ='Log in'
            url_blue = ('/browse')
            urltext_blue = 'View as guest'
            
        template_values = {
		'url_red': url_red,
                'urltext_red':urltext_red,
                'url_blue': url_blue,
                'urltext_blue': urltext_blue,
	}

        template = jinja_environment.get_template('login.html')
        self.response.out.write(template.render(template_values))
    
class Browse(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        data = Items.all()

        if user:
            usernick = user.nickname()
            login = ''
        else:
            usernick = 'guest'
            login = users.create_login_url(self.request.uri)


        template_values = {
            'usernick':usernick,
            'data' :data,
            'user' : user,
            'login':login,
            }
        
        template = jinja_environment.get_template('browse.html')
        self.response.out.write(template.render(template_values))


class Post_Item(webapp2.RequestHandler):
    def get(self):
        template_values = {

            }
        template = jinja_environment.get_template('postitem.html')
        self.response.out.write(template.render(template_values))


class Post_Item_Confirmed(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        seller = user
        title = self.request.get("title")
        description = self.request.get("description")
        price = self.request.get("price")
        creation_date = str((datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%d %B %Y %I:%M %p"))
        key_date = str(datetime.datetime.now() + datetime.timedelta(hours=8))
        Items(key_name = key_date, Title = title, Description = description, Price = price, Seller = seller, Creation_Date = creation_date, Key_Date = key_date).put()
        #mail
        user_address = user.email()
        sender_address = "DHShardcode <hardcodedhs@gmail.com>"
        subject = "[DHS HARDCODE]Your item has been created."
        body = ''' Your item has been created.
    Title: %s
    Description: %s
    Price: %s

    Thank you for using our service.
                    '''%(title, description, price)
        mail.send_mail(sender_address, user_address, subject, body)
        self.redirect("/browse")

class Item_Detail(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        key_name = self.request.get("key_name")
        self.response.write("""Title: """ + Items.get_by_key_name(key_name).Title)
        self.response.write("""<br>Description: """ + Items.get_by_key_name(key_name).Description)
        self.response.write("""<br>Price: """ + Items.get_by_key_name(key_name).Price)
        self.response.write("""<br>Seller: """ + Items.get_by_key_name(key_name).Seller.nickname())
        self.response.write("""<br>Creation Date: """ + Items.get_by_key_name(key_name).Creation_Date)
        for comment in Items.get_by_key_name(key_name).Comments:
            self.response.write("""<br>""" + comment)
        if user:
            self.response.write("""<br><form name="comment_post" action="/item_detail" method="post">
                                        <input type="text" name="key_name" style="display:none" value="%s" />
                                        <input type="text" name="comment" multiline="true" /><br>
                                        <button type="submit">Post Reply</button>
                                        </form>""" % key_name)
    def post(self):
        user = users.get_current_user()
        key_name = self.request.get("key_name")
        comment = user.nickname() + """ says: """ + self.request.get("comment") #needs more efficient way of storing comments
        comments_list = Items.get_by_key_name(key_name).Comments
        comments_list.append(comment)
        Items(key_name = key_name, Title = Items.get_by_key_name(key_name).Title, Description = Items.get_by_key_name(key_name).Description, \
              Price = Items.get_by_key_name(key_name).Price, Creation_Date = Items.get_by_key_name(key_name).Creation_Date, \
              Key_Date = Items.get_by_key_name(key_name).Key_Date, Seller = Items.get_by_key_name(key_name).Seller, Comments = comments_list).put()
        user_address = Items.get_by_key_name(key_name).Seller.email()
        sender_address = "DHShardcode <hardcodedhs@gmail.com>"
        subject = "[DHS HARDCODE] %s commented on your item" % user.email()
        body = '''%s commented on your item: %s
Please visit dhshardcode.appspot.com to view your item.
Thank you for using our service.''' %(user.email(), comment)
        mail.send_mail(sender_address, user_address, subject, body)
        self.response.write("""Title: """ + Items.get_by_key_name(key_name).Title)
        self.response.write("""<br>Description: """ + Items.get_by_key_name(key_name).Description)
        self.response.write("""<br>Price: """ + Items.get_by_key_name(key_name).Price)
        self.response.write("""<br>Seller: """ + Items.get_by_key_name(key_name).Seller.nickname())
        self.response.write("""<br>Creation Date: """ + Items.get_by_key_name(key_name).Creation_Date)
        for comment in Items.get_by_key_name(key_name).Comments:
            self.response.write("""<br>""" + comment)

        if user:
            
            self.response.write("""<br><form name="comment_post" action="/item_detail" method="post">
                            <input type="text" name="key_name" style="display:none" value="%s" />
                            <input type="text" name="comment" multiline="true" /><br>
                                    <button type="submit">Post Reply</button>
                                    </form>""" % key_name)

app = webapp2.WSGIApplication([
    ('/', Login),
    ('/browse', Browse),
    ('/post_item', Post_Item),
    ('/post_item_confirmed', Post_Item_Confirmed),
    ('/item_detail', Item_Detail)
], debug=True)
