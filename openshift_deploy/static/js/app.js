function validateEmail(email)
{
    var re = /\S+@\S+\.\S+/;
    return re.test(email);
}

var API_ROOT = '/api/v1/';
var pusher = new Pusher('cea6dff5fc1f38a2d45d');

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
        if(attrs.email.length > 60) {
            return "You've entered an email address that is too long (>60 characters)";
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
        this.projects = new ProjectList(apps);
        var _this = this;
        _this.render();

    },

    render: function() {
        // detects if the app is running inside an iframe
        if ( window.self !== window.top ) {
            this.$el.addClass('iframe');
        }
        data = {};
        if (this.projects.length > 1) {
            data['projects'] = this.projects.toJSON();
        }
        else {
            var project = this.projects.models[0];
            this.project = project;
            data['project'] = project;
        }
        var template = _.template($("#project_form_template").html(), data);
        this.$el.html(template);
        if($('embed-buttons').length > 0) {
            this.showEmbedButtons = true;
        }
        else {
            this.showEmbedButtons = true;
        }
        return this;
    },

    get_app_data: function() {
        var project = this.project || this.projects.findWhere({'resource_uri': this.$('select[name=project]').val()});
        return {
            'project_uri': project.get('resource_uri'),
            'app_name': project.get('name'),
            'survey_url': project.get('survey_form_url')
        };
    },

    deploy: function(e) {
        e.preventDefault();
        app_data = this.get_app_data();
        var project_uri = app_data['project_uri'];
        var app_name = app_data['app_name'];
        var email = this.$('input[name=email]').val();
        // creates a deployment app name from the project name and random characters
        var deploy_id = app_name.toLowerCase() + Math.random().toString().substr(2,6);
        deploy_id = deploy_id.replace(' ', '').replace('.', '').replace('-', '');

        // tracks the user interaction
        analytics.identify(email, {
            email: email
        });
        analytics.track('Deployed an app', {
            app_name: app_name,
            deploy_id: deploy_id,
            email: email
        });

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
            this.showInfoWindow(app_data);
            deploy.save({}, {
                error: this.deploymentFail
            });
        }
        else {
            this.$('div.control-group').addClass('error');
            var $errorMessage = $(".help-inline");
            $errorMessage.text(deploy.validationError);
        }
    },

    showInfoWindow: function(app_data) {
        var template = _.template($("#deploy_status_template").html(), {
            app_name: app_data['app_name'],
            survey_url: app_data['survey_url']
        });
        this.$el.html(template);
    },

    updateInfoStatus: function(data) {
        $("#info-message").text(data.message);
        $(".bar").width(data.percent + "%");
    },

    deploymentSuccess: function(data) {
        $("div.progress").hide();
        $("img.spinner").hide();
        $(".survey").hide();
        var $info = $("#info-message-section");
        $(".form-deploy h3").text("Deployed " + data['app_name']);
        $info.removeClass('alert-info').addClass('alert-success');
        $info.html('<i class="icon-ok"></i>' + data['message']);
        var app_link = '<a class="app-url" href="' + data['app_url'] + '">' + data['app_url'] + '</a>';
        $(app_link).insertAfter($info);
        if(data['username'] || data['password']) {
            var auth_data = '<div class="alert alert-info auth-details">Authentication details<br/>' +
                            '<strong>Username:</strong> ' + data['username'] + '<br/>' +
                            '<strong>Password:</strong> ' + data['password'] +
                            '</div>';
            $(auth_data).insertAfter($info);
        }
},

    deploymentFail: function(data) {
        $("div.progress").hide();
        $("img.spinner").hide();
        var $info = $("#info-message-section");
        $info.removeClass('alert-info').addClass('alert-error');
        $info.html('<i class="icon-remove"></i>' + data['message']);
    }
});

var EmbedView = Backbone.View.extend({
    events: {
        "click .btn": "generateEmbedCode"
    },

    initialize: function() {
        this.imageTxt = $('#embed-image-code');
        this.markdownTxt = $('#embed-markdown-code');
        this.htmlTxt = $('#embed-html-code');
        this.restTxt = $('#embed-rest-code');
    },

    generateEmbedCode: function(event) {
        $('.btn').removeClass('active');
        var $btn = $(event.currentTarget);
        $btn.addClass('active');
        var size = $btn.data('size');
        var color = $btn.data('color');
        var slug = $btn.data('slug');
        this.markdownTxt.text(this.generateMarkdownCode(size, color, slug));
        this.htmlTxt.text(this.generateHTMLCode(size, color, slug));
        this.restTxt.text(this.generateRestCode(size, color, slug));
        this.imageTxt.text(this.generateImgURL(size, color));
        return false;
    },

    generateMarkdownCode: function(size, color, slug) {
        var imgURL = this.generateImgURL(size, color);
        var appURL = this.generateAppURL(slug);
        return "[![Launch demo site]("+ imgURL + ")](" + appURL + ")";
    },

    generateHTMLCode: function(size, color, slug) {
        var imgURL = this.generateImgURL(size, color);
        var appURL = this.generateAppURL(slug);
        return '<a href="' + appURL + '"><img src="' + imgURL + '"></a>';
    },

    generateRestCode: function(size, color, slug) {
        var imgURL = this.generateImgURL(size, color);
        var appURL = this.generateAppURL(slug);
        return '.. image:: ' + imgURL+ '\n:target: ' + appURL;
    },

    generateImgURL: function(size, color) {
        return 'http://launch.appsembler.com/static/img/buttons/btn-' + size + '-' + color + '.png';
    },

    generateAppURL: function(slug) {
        return 'http://launch.appsembler.com/' + slug + '/';
    }
});

$(function(){
    var appview = new AppView();
    if(appview.showEmbedButtons === true) {
        var embedview = new EmbedView({el: '#embed-buttons'});
    }
});
