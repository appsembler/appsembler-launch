function validateEmail(email)
{
    var re = /\S+@\S+\.\S+/;
    return re.test(email);
}

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
    url: API_ROOT + 'deployments/',
    validate: function(attrs, options) {
        var re = /\S+@\S+\.\S+/;
        if(attrs.email === "" || !re.test(attrs.email)) {
            return "You must enter an email address!";
        }
    }
});

// Views
var AppView = Backbone.View.extend({
    el: $('.container'),

    events: {
        "submit form.form-deploy": "deploy"
    },

    initialize: function() {
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
        e.preventDefault();
        var project_uri = this.$('select[name=project]').val();
        var email = this.$('input[name=email]').val();
        var deploy_id = $("#project_select option:selected").text() + Math.random().toString(36).substr(2,16);
        this.channel = pusher.subscribe(deploy_id);
        this.channel.bind('info_update', this.updateInfoStatus);
        this.channel.bind('deployment_complete', this.deploymentSuccess);
        this.channel.bind('deployment_failed', this.deploymentFail);

        var deploy = new Deployment({
            project: project_uri,
            email: email,
            deploy_id: deploy_id
        });
        if(deploy.isValid()) {
            this.showInfoWindow();
            deploy.save({}, {
                error: this.deploymentFail
            });
        }
        else {
            this.$('div.control-group').addClass('error');
            var $input = this.$('#email_input').parent();
            var errorMessage = '<span class="help-inline">' + deploy.validationError + '</span>';
            $(errorMessage).insertAfter($input);
        }   
    },

    showInfoWindow: function() {
        this.$el.html($("#deploy_status_template").html());
    },

    updateInfoStatus: function(data) {
        console.log(data);
        $("#info-message").text(data.message);
        $(".bar").width(data.percent + "%");
    },

    deploymentSuccess: function(data) {
        $("div.progress").hide();
        $("img.spinner").hide();
        var $info = $("#info-message-section");
        $info.removeClass('alert-info').addClass('alert-success');
        console.log(data);
        $info.html('<i class="icon-ok"></i>' + data['message']);
        var app_link = '<a class="app-url" href="' + data['app_url'] + '">' + data['app_url'] + '</a>';
        $(app_link).insertAfter($info);
    },

    deploymentFail: function(data) {
        $("div.progress").hide();
        $("img.spinner").hide();
        var $info = $("#info-message-section");
        $info.removeClass('alert-info').addClass('alert-error');
        $info.html('<i class="icon-remove"></i>' + data['message']);
        $('<p class="error_message">' + data['details'] + '</p>').insertAfter($info);
    }
});

$(function(){
    var appview = new AppView();
});
