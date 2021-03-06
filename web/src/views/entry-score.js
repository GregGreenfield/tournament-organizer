/* global $ React ReactDOM:true */
var Inputs = require("./component-inputs");

var EnterScoreForm = React.createClass({
    propTypes: {
        categories:         React.PropTypes.array.isRequired,
        opponent:           React.PropTypes.string,
        scoreChangeHandler: React.PropTypes.func.isRequired,
        submitHandler:      React.PropTypes.func.isRequired,
    },
    render: function() {
        if (!this.props.categories.length) {
            return <div>"No score categories available"</div>;
        }

        var inputs = this.props.categories.map(function(cat) {
            var helpText = "Enter a score between " + cat.min_val + " and " +
                    cat.max_val,
                opp = this.props.opponent && cat.opponent_score ?
                    " for " + this.props.opponent : "",
                name = cat.name + " Score" + opp;
            return <Inputs.textField name={name}
                id={cat.name}
                key={cat.name}
                changeHandler={this.props.scoreChangeHandler}
                value={cat.score || ""}
                helpText={helpText} />;
        }.bind(this));

        return (
            <form onSubmit={this.props.submitHandler}>

                <div>{inputs}</div>

                <button type="submit">Enter Score</button>
            </form>
        );
    }
});

var EnterScorePage = React.createClass({
    getInitialState: function () {
        return ({
            error: null,
            message: null,
            perTournament: false,
            score: null,
            showForm: false,
            categories: null
        });
    },
    componentDidMount: function() {

        this.contentRequest = $.get(window.location + "/content",
            function(contents) {

                this.setState(contents);

                this.categoryRequest = $.get(
                    window.location + "/scorecategories",
                    function (res) {

                        var cats = res.categories.filter(function(cat) {
                                return this.state.perTournament ?
                                    cat.per_tournament
                                    : !cat.per_tournament;
                                }.bind(this));

                        this.setState({categories: cats, showForm: true});
                    }.bind(this));
                }.bind(this));
    },
    componentWillUnmount: function() {
        this.contentRequest.abort();
        this.categoryRequest.abort();
    },
    handleScoreChange: function(event) {
        this.setState({categories: this.state.categories.map(function(cat) {
            cat.score = cat.name === event.target.id ?
                event.target.value : cat.score;
            return cat;
            })
        });
    },
    handleSubmit: function (e) {
        e.preventDefault();

        var data = {
            scores: this.state.categories
                .filter(function(cat) {
                    return cat.score !== null;
                })
                .map(function(cat) {
                    return {
                        gameId: this.state.game_id,
                        category: cat.name,
                        score: cat.score
                    };
                }.bind(this))
            };

        $.post(window.location,
            data,
            function success(res) {
                this.setState({
                    error: null,
                    message: res.message,
                    showForm: false,
                    categories: []});
            }.bind(this))
            .fail(function (res) {
                var state = res.responseJSON;
                state.showForm = true;
                this.setState(state);
            }.bind(this));
    },
    render: function() {
        return (
            <div>
                <div>{this.state.message}</div>
                <div>{this.state.error}</div>
                {this.state.showForm ?
                    <EnterScoreForm submitHandler={this.handleSubmit}
                        categories={this.state.categories}
                        scoreChangeHandler={this.handleScoreChange}
                        opponent={this.state.opponent} />
                    : null}
            </div>
        );
    }
});


ReactDOM.render(
    <EnterScorePage />,
    document.getElementById("content")
);
