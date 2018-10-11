__author__ = 'Rafik Hadfi'


# importing 3rd party libraries
import sys
sys.path.insert(0, 'libs')

from google.appengine.api import channel
from google.appengine.ext import deferred
import webapp2
from webapp2_extras import sessions_memcache
from webapp2_extras import sessions
from webapp2_extras import jinja2
import uuid
import time

import networkx as nx
from Routing import route

TEST_NETX = False
Paths = []

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session(name='mc_session', factory=sessions_memcache.MemcacheSessionFactory)

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        j = jinja2.get_jinja2(app=self.app)
        #        j.environment.globals['is_admin']= is_admin()
        pass
        return j

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

class MainHandler(BaseHandler):

    client_ids = dict()

    def get(self):
        channel_token = self.session.get('channel_token')
        if channel_token is None: # if the session user does not have a channel token, create it and save it in the session store.
            client_id = str(uuid.uuid4()).replace("-",'')
            channel_token = channel.create_channel(client_id)
            self.session['channel_token'] = channel_token
            self.session['client_id'] = client_id

        client_id = self.session['client_id']

        # Put some messages in the deferred queue which will appear in the browser a few seconds after loading the page.
        deferred.defer(channel.send_message,client_id,"Mediator: Choose your path.",_countdown=1)

        self.render_response('home.html',**{"token":channel_token,"client_id":client_id})

    def post(self):
        channel_token = self.session.get('channel_token')
        if channel_token is None: # if the session user does not have a channel token, create it and save it in the session store.
            client_id = str(uuid.uuid4()).replace("-",'')
            channel_token = channel.create_channel(client_id)
            self.session['channel_token'] = channel_token
            self.session['client_id'] = client_id

        client_id = self.session['client_id']
        cmd = self.request.get("path2")
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        
        print '_______________________________________________________________________________________________'

        if cmd != 'list':
            if client_id in self.client_ids:
                self.client_ids[client_id].append((t, str(cmd)))
            else:
                self.client_ids[client_id] = [(t, str(cmd))]

        print "Mediator    t = ", t
        print "            receiving path: ", cmd 
        print "            from client: ", client_id
        print "            channel token: ", channel_token

        path = [str(_) for _ in cmd.split(';')]
        path = [ _[1:-1].split(',') for _ in path]
        new_path = [[0,0] for _ in xrange(len(path))]
        
        i = 0
        for p in path:
            if len(p)==2:
                new_path[i][0] = float(p[0])
                new_path[i][1] = float(p[1])
                i+=1
        
        new_path = new_path[:-1]
        path = new_path
        source = path[0]
        destination = path[-1]

        print '\n            source = ', source
        print '            destination = ', destination
        print '_______________________________________________________________________________________________'

        if TEST_NETX:
            print 'Testing Networkx !!'
            G = nx.Graph()
            G.add_node('A')
            G.add_node('B')
            G.add_node('C')
            G.add_edge('A', 'B')
            G.add_edge('A', 'C')
            print ' G : ', G.nodes()
            print '     ', G.edges()        

        Paths.append(path)

        result = route(Paths, source, destination, view=False)
        
        print '> ', result

        cost = 0
        if result != -1:
            cost = result[1]
        
        response =  "Mediator: I received: %s from %s<br>" % (cmd, client_id)
        num_clients = len(self.client_ids)
        
        response = 'Mediator: Listing clients (#=%d)<br>' % num_clients
        
        for clid in self.client_ids:
            
            if clid == client_id:
             
                received_time = self.client_ids[clid][0][0]
                
                print ' received_time = ', received_time            
                print '###########################################################################'
                
                response += "   Client <font color=\"blue\">%s</font> <br>" % clid
                
                res_tmp = ""

                for bid in self.client_ids[clid]:
                    if result == -1:
                        res_tmp = "&nbsp;&nbsp;&nbsp; &nbsp;  t=<font color=\"red\">%s</font>  &nbsp;&nbsp;   path=}<br>" % bid[0]
                    else:
                        res_tmp = "&nbsp;&nbsp;&nbsp; &nbsp;  t=<font color=\"red\">%s</font>  &nbsp;&nbsp;   path=%s}<br>" % (bid[0], bid[1])
                
        response += res_tmp
        response += '<br>'
        response += 'Your cost is %d.<br>' % cost
        response += 'Total: %d cars.<br>' % len(self.client_ids)
             
        print '\n'       
        print 'Sending to ', client_id
        channel.send_message(client_id, response)

        self.render_response('home.html',**{"token":channel_token,"client_id":client_id})


#

config = {}
config['webapp2_extras.sessions'] = { 'secret_key': '9upj9p80pi08hn09k9jk',}
app = webapp2.WSGIApplication([('/', MainHandler) ,   ('/message', MainHandler) ], debug=True, config=config)


