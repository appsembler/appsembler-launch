$(function(){
    var API_ROOT = '/api/v1/';

    // Models
    var Project = Backbone.Model.extend({});

    var ProjectList = Backbone.Collection.extend({
        model: Project,
        url: API_ROOT + 'projects/',
        parse: function(response) {
            return response.objects;
        }
    });

    var Deployment = Backbone.Model.extend({
        url: API_ROOT + 'deployments/'
    });

    // Views
    var AppView = Backbone.View.extend({
        el: $('.container'),
        initialize: function() {
            this.projects = new ProjectList();
            var _this = this;
            this.projects.fetch().complete(function() {
                _this.render();
            });

        },
        render: function() {
            var project_form_template = _.template($("#project_form_template").html(), {
                projects: this.projects.toJSON()
            });
            this.$el.html(project_form_template);
            return this;
        }
    });

    var appview = new AppView();

});