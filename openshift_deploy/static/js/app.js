var API_ROOT = '/api/v1/';
var pusher = new Pusher('bb4a670d8f7a12112716');

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

    events: {
        "submit form.form-deploy": "deploy"
    },

    channel: pusher.subscribe('deployment'),

    initialize: function() {
        this.channel.bind('info_update', this.updateInfoStatus);
        this.projects = new ProjectList();
        var _this = this;
        this.projects.fetch().complete(function() {
            _this.render();
        });

    },

    render: function() {
        var template = _.template($("#project_form_template").html(), {
            projects: this.projects.toJSON()
        });
        this.$el.html(template);
        return this;
    },

    deploy: function(e) {
        var project_uri = this.$('select[name=project]').val();
        var email = this.$('input[name=email]').val();
        var deploy = new Deployment({
            project: project_uri,
            email: email
        });
        this.showInfoWindow();
        deploy.save({}, {
            success: this.deploymentSuccess,
            error: this.deploymentFail
        });
        e.preventDefault();
    },

    showInfoWindow: function() {
        this.$el.html($("#deploy_status_template").html());
    },

    updateInfoStatus: function(data) {
        $("#info-message").text(data.message);
        $(".bar").width(data.percent + "%");
    },

    deploymentSuccess: function(model, response, options) {
        $("div.progress").hide();
        $("img.spinner").hide();
        var $info = $("#info-message-section");
        $info.removeClass('alert-info').addClass('alert-success');
        $info.html('<i class="icon-ok"></i> Your deployment was successful!');
        var app_link = '<a class="app-url" href="' + model.get('url') + '">' + model.get('url') + '</a>';
        $(app_link).insertAfter($info);
    },

    deploymentFail: function(model, xhr, options) {
        var $info = $("#info-message-section");
        $info.removeClass('alert-info').addClass('alert-error');
        $info.html('<i class="icon-remove"></i> An error occurred!');
    }
});

$(function(){
    var appview = new AppView();
});
