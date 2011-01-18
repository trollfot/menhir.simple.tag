# -*- coding: utf-8 -*-

import grokcore.viewlet as grok

from dolmen.app.layout import master, IDisplayView, Form
from dolmen.content import IBaseContent
from dolmen.forms.base import Fields, Actions, SUCCESS, FAILURE
from dolmen.forms.crud import actions as formactions

from grok import subscribe
from fanstatic import Library, Resource
from megrok import pagetemplate as pt

from zeam.form import base
from zeam.form.base.interfaces import IDataManager
from zeam.form.base.interfaces import IField
from zeam.form.viewlet import ViewletForm

from zope.cachedescriptors.property import Lazy
from zope.component import getUtility, getMultiAdapter
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import Attributes, ObjectModifiedEvent
from zope.schema import TextLine

from lovely.tag.interfaces import IUserTagging, ITaggingEngine, ITaggable

grok.context(ITaggable)


TagResources = Library('tag_styles', 'resources')
TagStyles = Resource(TagResources, 'tags.css')

try:
    import menhir.simple.livesearch
    from dolmen.app.layout.master import Header

    class TagLiveSearch(grok.Viewlet):
        grok.name('tag.livesearch')
        grok.viewletmanager(Header)

        def render(self):
            return u"""
            <script>
            $(document).ready(function(){
              $('#tags-widgets-tag').liveSearch({
                 ajaxURL: '%s/tag-search?search_term='
               });
            });
            </script>
            """ % self.view.url(self.context)
            
        def update(self):
            menhir.simple.livesearch.LiveSearchResources.need()
        

    class TagSearchResults(grok.View):
        grok.name("tag-search")
        
        @Lazy
        def engine(self):
            return getUtility(ITaggingEngine)
        
        def update(self, search_term=None):
            """
            search for tags to suggest
            """
            if search_term:
                user_tags = IUserTagging(self.context).tags
                # TODO is there a better way for filtering
                # than asking all tags ?
                self.items = (tag for tag in self.engine.getTags() 
                                    if  tag.startswith(search_term)
                                        and not tag in user_tags)
            else:
                self.items = []
            self.context_url = self.url(self.context)
            self.actual_url = str(self.request.URL)
        
except ImportError:
    # FIXME do some log here to say we wont have live search
    pass


class AddTag(base.Action):

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.submissionError = errors
            return FAILURE

        content = form.getContentData()
        if IDataManager.providedBy(content):
            content = content.content
        
        userTagging = IUserTagging(content)
        userTagging.tags |= set([data['tag'],])
        notify(ObjectModifiedEvent(content))
        form.flash('Added tag %s' % data['tag'])
        form.redirect(form.url(content))

        return SUCCESS


class TagAddForm(Form):
    grok.name('user_tags_add')

    prefix = "tags"

    ignoreContent = True
    submissionError = None

    fields = Fields(IField(
        TextLine(__name__="tag", title = u'Add tag', required = True)))

    actions = Actions(
        AddTag('Add'), formactions.CancelAction("Cancel"))


class TagsViewlet(ViewletForm):
    grok.view(IDisplayView)
    grok.viewletmanager(master.Top)
    grok.require("dolmen.content.Edit")
    grok.order(100)

    prefix = "tags"
    ignoreContent = True
    submissionError = None

    fields = Fields(IField(
        TextLine(__name__="tag", title = u'Add tag', required = True)))

    actions = Actions(AddTag('Add'))

    @property
    def flash(self):
        return self.view.flash

    def cloud(self):
        return self.engine.cloud(items=(self.contextId,))

    def update(self):
        TagStyles.need()
        ViewletForm.update(self)
        
        self.context_url = self.view.url(self.context)
        self.actual_url = str(self.request.URL)
        self.engine_url = self.view.url(self.engine)
        
        try:
            self.user_tags = IUserTagging(self.context).tags
            self.cloudInfo = [{
                'tag': tag,
                'weight': weight,
                'marked': tag in self.user_tags
                } for tag, weight in self.cloud()]
 
        except KeyError:
            self.user_tags = []
            self.cloudInfo = []

    @Lazy
    def engine(self):
        return getUtility(ITaggingEngine)

    @Lazy
    def contextId(self):
        intids = getUtility(IIntIds)
        return intids.getId(self.context)


class TagsViewletTemplate(pt.PageTemplate):
    pt.view(TagsViewlet)


class CameFromView(grok.View):
    """View handling a came_from parameter
    """
    grok.baseclass()

    def render(self, came_from=None):
        if came_from is not None:
            self.redirect(came_from)
        self.redirect(self.url(self.context))


class QuickAddTag(CameFromView):
    grok.name('user_tag_quick_add')

    def update(self, tag=None):
        if tag is not None:
            userTagging = IUserTagging(self.context)
            userTagging.tags |= set([tag,])


class QuickRemoveTag(CameFromView):
    grok.name('user_tag_quick_remove')

    def update(self, tag=None):
        if tag is not None:
            userTagging = IUserTagging(self.context)
            userTagging.tags -= set([tag,])
