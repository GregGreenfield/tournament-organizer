# pylint: disable=C0111
from django.conf.urls import patterns, url

from public import views

# pylint: disable=C0103
urlpatterns = patterns('',

    # Basic pages. These are part of a regular journey
    url(r'^$', views.index, name='index'),
    url(r'^createtournament$',
        views.create_tournament, name='create_tournament'),
    url(r'^feedback$', views.feedback, name='feedback'),
    url(r'^login$', views.login, name='login'),
    url(r'^registerforatournament$',
        views.register_for_tournament, name='apply_for_tournament'),
    url(r'^signup$', views.create_account, name='create_account'),
    url(r'^suggestimprovement$',
        views.suggest_improvement, name='suggest_improvement'),

    # Post forwarding. These URLs are essentially posted to the dao
    url(r'^placefeedback$', views.place_feedback, name='forward_feedback'),
    url(r'^loginAccount$', views.login_account, name='forward_login'),
    url(r'^addPlayer$', views.add_player, name='forward_add_player'),
    url(r'^addTournament$',
        views.add_tournament, name='forward_add_tournament'),
    url(r'^registerForTournament$',
        views.apply_for_tournament, name='forward_register_for_tournament'),
)
