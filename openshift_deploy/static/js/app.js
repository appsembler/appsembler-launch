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
        this.projects = new ProjectList(apps);
        var _this = this;
        _this.render();

    },

    render: function() {
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
        if (this.project) {
            return {
                'project_uri': this.project.get('resource_uri'),
                'app_name': this.project.get('name')
            };
        }
        else {
            return {
                'project_uri': this.$('select[name=project]').val(),
                'app_name': $("#project_select option:selected").text()
            };
        }
    },

    deploy: function(e) {
        e.preventDefault();
        app_data = this.get_app_data();
        var project_uri = app_data['project_uri'];
        var app_name = app_data['app_name'];
        var email = this.$('input[name=email]').val();
        // creates a deployment app name from the project name and random characters
        var deploy_id = app_name + Math.random().toString().substr(2,6);
        deploy_id = deploy_id.replace(' ', '');
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
            this.showInfoWindow(app_name);
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

    showInfoWindow: function(app_name) {
        var template = _.template($("#deploy_status_template").html(), {
            app_name: app_name
        });
        this.$el.html(template);
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
