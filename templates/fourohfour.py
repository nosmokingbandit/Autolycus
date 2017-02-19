import core
import dominate
from cherrypy import expose
from dominate.tags import *
from head import Head


class FourOhFour():

    @staticmethod
    @expose
    def default():

        doc = dominate.document(title='Autolycus')

        with doc.head:
            meta(name='enable_notifs', content='false')
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/style.css?v=02.02')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/fourohfour.css?v=02.02')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/fourohfour.css?v=02.02'.format(core.CONFIG['Server']['theme']))

        with doc:
            with div(id='content'):
                with span(cls='msg'):
                    span(u'404')
                    br()
                    span(u'Page Not Found')

        return doc.render()

# pylama:ignore=W0401
