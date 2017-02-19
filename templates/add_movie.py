import core
import dominate
from cherrypy import expose
from dominate.tags import *
from head import Head
from header import Header


class AddMovie():
    @expose
    def default(self):
        doc = dominate.document(title='Autolycus')

        with doc.head:
            Head.insert()
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/add_movie.css?v=02.06')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/add_movie.css?v=02.06'.format(core.CONFIG['Server']['theme']))
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/movie_info_popup.css?v=02.02')
            link(rel='stylesheet', href=core.URL_BASE + '/static/css/{}/movie_info_popup.css?v=02.02'.format(core.CONFIG['Server']['theme']))
            script(type='text/javascript', src=core.URL_BASE + '/static/js/add_movie/main.js?v=02.02b')

        with doc:
            Header.insert_header(current="add_movie")
            with div(id='search_box'):
                input(id='search_input', type="text", placeholder="Search...", name="search_term")
                with button(id="search_button"):
                    i(cls='fa fa-search')
            with div(id='thinker'):
                span()
                span()
                span()
                span()
                span()
                span()
                span()
            with div(id="database_results"):
                ul(id='artist_list')

            div(id='overlay')

            div(id='info_pop_up')

        return doc.render()

# pylama:ignore=W0401
