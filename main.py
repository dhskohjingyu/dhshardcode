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
    Seller_Name = db.StringProperty()
    Description = db.StringProperty()
    Price = db.StringProperty()
    Creation_Date = db.StringProperty()
    Key_Date = db.StringProperty()
    Comments = db.ListProperty(str)
    Message_Time = db.StringProperty()
    Buyers = db.ListProperty(str)

class User(db.Model): #key_name = email
    Name = db.StringProperty()
    Sell_Items = db.ListProperty(str)
    Buy_Items = db.ListProperty(str)

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
            if User.get_by_key_name(user.email()):
                usernick = User.get_by_key_name(user.email()).Name
                login = ''
            else:
                User(key_name = user.email(), Name = user.nickname()).put()
                login = ''
                usernick = User.get_by_key_name(user.email()).Name
                
        else:
            usernick = 'guest'
            login = users.create_login_url(self.request.uri)


        template_values = {
            'usernick':usernick,
            'data' :data,
            'user' : user,
            'login':login,
            'User':User,
            }
        
        template = jinja_environment.get_template('browse.html')
        self.response.out.write(template.render(template_values))

class Profile(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.out.write('''
                <form method='post' action='/profileedit'>
                        <b>nickname</b><input type='text' name='nickname' value='%s' />
                        <button type='submit'>change</button>
                </form><br /><br />
                
                '''%(User.get_by_key_name(user.email()).Name))
        sell_list = User.get_by_key_name(user.email()).Sell_Items
        
        for element in sell_list:
            item = Items.get_by_key_name(element)
            self.response.out.write('''
                <form method='post' action='/item_delete'>
                    <b>Name:</b>%s
                    <input type='text' name='key_name' value='%s' style='display:none' />
                    <button type='submit'>delete item</button>
                <form><br/>''' % (item.Title, item.Key_Date))
            buyerlist=item.Buyers
            if buyerlist:
                self.response.out.write('''<b>BUYERS:</b>''')
            
                for buyer in buyerlist:
                    self.response.out.write('''<h6>%s</h6>'''%User.get_by_key_name(buyer).Name)
            
            
        self.response.out.write('''<a href='/deleteprofile'>Delete Profile</a>''')

class Delete_Profile(webapp2.RequestHandler):
    def get(self):
        user=users.get_current_user()
        for i in Items.all():
            
            if i.Seller.email() == user.email() :
                Items.get_by_key_name(i.Key_Date).delete()
        User.get_by_key_name(user.email()).delete()        
        self.redirect("/")
        
        
class Delete_Item(webapp2.RequestHandler):
    def post(self):
        user=users.get_current_user()
        name = User.get_by_key_name(user.email()).Name
        sell_list = User.get_by_key_name(user.email()).Sell_Items
        sell_list.remove(self.request.get('key_name'))
        User(key_name = user.email(), Name = name, Sell_Items = sell_list).put()
        Items.get_by_key_name(self.request.get('key_name')).delete()
        self.redirect('/profile')
        
        
class Edit_Profile(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        User(key_name = user.email(), Name = self.request.get('nickname'),Sell_Items = User.get_by_key_name(user.email()).Sell_Items,Buy_Items = User.get_by_key_name(user.email()).Buy_Items).put()
        self.redirect('/browse')



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
        Items(key_name = key_date, Buyers = [], Title = title, Description = description, Price = price, Seller = seller, Seller_Name = User.get_by_key_name(user.email()).Name, Creation_Date = creation_date, Key_Date = key_date).put()
        sell_list = User.get_by_key_name(user.email()).Sell_Items
        sell_list.append(key_date)
        nickname = User.get_by_key_name(user.email()).Name
        User(key_name = user.email(), Sell_Items = sell_list, Name = nickname,Buy_Items = User.get_by_key_name(user.email()).Buy_Items).put()
        try:#mail
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
        except:
            self.redirect("/browse")

class Item_Detail(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        key_name = self.request.get("key_name")
        if key_name in User.get_by_key_name(user.email()).Sell_Items:
            not_seller = False
        else:
            not_seller = True

        template_values = {
		'user':user,
                'key_name':key_name,
                'Items':Items,
                'not_seller':not_seller,
	}

        template = jinja_environment.get_template('itemdetail.html')
        self.response.out.write(template.render(template_values))

            
    def post(self):
        try: #email (just in case mail exceeds the daily quota of 100 )
            user = users.get_current_user()
            key_name = self.request.get("key_name")
            comment = user.nickname() + """ says: """ + self.request.get("comment") #needs more efficient way of storing comments
            comments_list = Items.get_by_key_name(key_name).Comments
            comments_list.append(comment)
            Items(key_name = key_name, Buyers = Items.get_by_key_name(key_date).Buyers,Title = Items.get_by_key_name(key_name).Title, Description = Items.get_by_key_name(key_name).Description, \
                  Price = Items.get_by_key_name(key_name).Price, Creation_Date = Items.get_by_key_name(key_name).Creation_Date, \
                  Key_Date = Items.get_by_key_name(key_name).Key_Date, Seller = Items.get_by_key_name(key_name).Seller, Comments = comments_list).put()
            
            user_address = Items.get_by_key_name(key_name).Seller.email()
            sender_address = "DHShardcode <hardcodedhs@gmail.com>"
            subject = "[DHS HARDCODE] %s commented on your item" %(user.email())
            body = '''%s commented on your item: %s
    Please visit dhshardcode.appspot.com to view your item.
    Thank you for using our service.''' %(user.email(), comment)
            mail.send_mail(sender_address, user_address, subject, body)
            if key_name in User.get_by_key_name(user.email()).Sell_Items:
                not_seller = False
            else:
                not_seller = True

        except:
            user = users.get_current_user()
            key_name = self.request.get("key_name")
            comment = user.nickname() + """ says: """ + self.request.get("comment") #needs more efficient way of storing comments
            comments_list = Items.get_by_key_name(key_name).Comments
            comments_list.append(comment)
            Items(key_name = key_name, Buyers = Items.get_by_key_name(key_date).Buyers,Title = Items.get_by_key_name(key_name).Title, Description = Items.get_by_key_name(key_name).Description, \
                  Price = Items.get_by_key_name(key_name).Price, Creation_Date = Items.get_by_key_name(key_name).Creation_Date, \
                  Key_Date = Items.get_by_key_name(key_name).Key_Date, Seller = Items.get_by_key_name(key_name).Seller, Comments = comments_list).put()
            if key_name in User.get_by_key_name(user.email()).Sell_Items:
                not_seller = False
            else:
                not_seller = True

        template_values = {
		'user':user,
                'key_name':key_name,
                'Items':Items,
                'not_seller':not_seller,
	}
 
        template = jinja_environment.get_template('itemdetail.html')
        self.response.out.write(template.render(template_values))

class Interest(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        item_id = self.request.get('item_id')
        buyers = Items.get_by_key_name(item_id).Buyers
        buy_items = User.get_by_key_name(user.email()).Buy_Items
        if not(user.email() in buyers):
            buyers.append(user.email())
            buy_items.append(item_id)
            User(key_name = user.email(), Name = User.get_by_key_name(user.email()).Name ,Sell_Items = User.get_by_key_name(user.email()).Sell_Items,Buy_Items=buy_items).put()
            Items(key_name =item_id , Buyers = buyers ,Title = Items.get_by_key_name(item_id).Title, Description = Items.get_by_key_name(item_id).Description, \
                  Price = Items.get_by_key_name(item_id).Price, Creation_Date = Items.get_by_key_name(item_id).Creation_Date, \
                  Key_Date = Items.get_by_key_name(item_id).Key_Date, Seller = Items.get_by_key_name(item_id).Seller, Comments = Items.get_by_key_name(item_id).Comments).put()
        self.redirect('/browse')


class Expired(webapp2.RequestHandler):
    def get(self):
        user=users.get_current_user()
        data=Items.all()
        today_date=datetime.datetime.today()
        month_list={'January':1,'February':2,'March':3,'April':4,'May':5,
            'June':6,'July':7,'August':8,'September':9,'October':10,
            'November':11,'December':12}

        for i in data:
            creation_date=i.Creation_Date.split()
            #convert string back to date format
            creation_date=creation_date[0]+'-'+str(month_list[creation_date[1]])+'-'+creation_date[2]
            creation_date=datetime.datetime.strptime(creation_date,'%d-%m-%Y')
            #set expired date to 30 days after creation date
            expired_date=creation_date+datetime.timedelta(days=1)
            if today_date>expired_date:
                i.delete()
        
        template_values = {
            'data' :data,
            }
        template = jinja_environment.get_template('expired.html')
        self.response.out.write(template.render(template_values))       

        
app = webapp2.WSGIApplication([
    ('/', Login),
    ('/browse', Browse),
    ('/post_item', Post_Item),
    ('/post_item_confirmed', Post_Item_Confirmed),
    ('/item_detail', Item_Detail),
    ('/profile',Profile),
    ('/profileedit',Edit_Profile),
    ('/item_delete',Delete_Item),
    ('/deleteprofile',Delete_Profile),
    ('/expired',Expired),
    ('/interest',Interest)
], debug=True)
