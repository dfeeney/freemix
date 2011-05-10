from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Variable
from freemix.freemixprofile.views import create_view_json, get_metadata
from freemix.freemixprofile import models
import json

register = template.Library()


@register.inclusion_tag("dataview/dataview_detail.html", takes_context=True)
def dataview_detail(context, dataview):
    return {"dataview": dataview, "request": context['request']}

@register.inclusion_tag("dataview/dataview_list.html", takes_context=True)
def dataview_list(context, queryset, max_count=10, pageable=True):
    return {"queryset": queryset, "max_count": max_count, "pageable": pageable,
            "request": context['request']}

@register.inclusion_tag("dataview/new_dataview.html", takes_context=True)
def new_dataview(context):
    return {'STATIC_URL': settings.STATIC_URL}

@register.tag
def new_view_json ( parser, token ):
    try:
        tag_name, data_profile, canvas = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents[0]
    return NewViewJsonNode( data_profile, canvas )

@register.tag
def view_json ( parser, token ):
    try:
        tag_name, username, slug = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents[0]
    return ViewJsonNode( username, slug )

class NewViewJsonNode( template.Node ):
    def __init__ (self, data_profile, canvas):
        self.data_profile = Variable(data_profile)
        self.canvas = Variable(canvas)

    def render(self, context):

        return render_to_string("dataview/profile.js", {"json":
            create_view_json(self.data_profile.resolve(context),
                self.canvas.resolve(context))})


class ViewJsonNode( template.Node ):
    def __init__ (self, username, slug):
        self.username = Variable(username)
        self.slug = Variable(slug)

    def render(self, context):

        return render_to_string("dataview/profile.js", {"json":
            json.dumps(get_metadata(self.username.resolve(context),
                self.slug.resolve(context)))})

# Theme tags
@register.tag
def theme_list(parser, token):
    return ThemeListNode("view_theme/list.html" )

@register.tag
def theme_css_link(parser, token):
    try:
        tag_name, slug = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents[0]
    return ThemeLinkNode(slug)

class ThemeListNode( template.Node ):
    def __init__ (self, template):
        self.template = template

    def render(self, context):
        return render_to_string(self.template, {"theme_list": models.ExhibitTheme.objects.filter(enabled=True)})

class ThemeLinkNode( template.Node ):
    def __init__(self, slug):
        self.slug = slug

    def render(self, context):
        slug = Variable(self.slug).resolve(context)
        theme = models.ExhibitTheme.objects.get(slug=slug)
        return "<link rel='stylesheet' href='%s' type='text/css' />"%theme.url
