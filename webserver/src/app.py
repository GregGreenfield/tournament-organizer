import os
import yaml

from flask import Flask, render_template, request, json, make_response

from player_db import PlayerDBConnection
from tournament_db import TournamentDBConnection

app                     = Flask(__name__)
player_db_conn          = PlayerDBConnection()
tournament_db_conn      = TournamentDBConnection()

# Page rendering
@app.route("/")
def main():
    return render_template('index.html')

@app.route('/createATournament')
def showCreateATournament():
    return render_template('create-a-tournament.html')

@app.route('/showRegisterForTournament')
def showRegisterForTournament():
    return render_template('register-for-tournament.html')

@app.route('/signup')
def showAddPlayer():
    return render_template('create-a-player.html')

# Page actions
@app.route('/registerForTournament', methods=['POST'])
def applyForTournament():
    _name = request.form['inputName']
    _email = request.form['inputEmail']

    if _name and _email:
        return json.dumps({'html':'<p>You submitted the following fields:</p><ul><li>Name: {_name}</li><li>Email: {_email}</li></ul>'.format(**locals())})
    else:
        return json.dumps({'html':'<span>Enter the required fields</span>'})


@app.route('/addTournament', methods=['POST'])
def addTournament():
    _name = request.form['inputTournamentName']

    if _name:
        try:
            if tournament_db_conn.tournamentExists(_name):
                return make_response("A tournament with name %s already exists! Please choose another name" % _name, 400)
            tournament_db_conn.addTournament({'name': _name})
            return make_response('<p>Tournament Created! You submitted the following fields:</p><ul><li>Name: {_name}</li></ul>'.format(**locals()), 200)
        except Error as e:
            return make_response(e, 500)
    else:
        return make_response("Please enter the required fields", 400)


@app.route('/addPlayer', methods=['POST'])
def addPlayer():
    _user_name = request.form['inputUsername']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _confirmPassword = request.form['inputConfirmPassword']

    if not _user_name or not _email:
        return make_response("Please fill in the required fields", 400)

    if not _password or not _confirmPassword or _password != _confirmPassword:
        return make_response("Please enter two matching passwords", 400)

    try:
        if player_db_conn.usernameExists(_user_name):
            return make_response("A user with the username %s already exists! Please choose another name" % _user_name, 400)

        player_db_conn.addAccount({'user_name': _user_name, 'email' : _email, 'password': _password})
        return make_response('<p>Account created! You submitted the following fields:</p><ul><li>User Name: {_user_name}</li><li>Email: {_email}</li></ul>'.format(**locals()), 200)
    except Error as e:
        return make_response(e, 500)


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

