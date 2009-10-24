# -*- coding: utf-8 -*-

import megrok.resourcelibrary

import grokcore.viewlet as grok

from grok import subscribe
from zope.event import notify
from zope.schema import TextLine
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, getMultiAdapter
from zope.cachedescriptors.property import Lazy
from zope.lifecycleevent import Attributes, ObjectModifiedEvent

from dolmen.content import IBaseContent
from dolmen.app.layout import master, IDisplayView, Form
from dolmen.forms.base import cancellable, button, Fields, Field
from lovely.tag.interfaces import IUserTagging, ITaggingEngine, ITaggable

grok.context(ITaggable)


class TagResources(megrok.resourcelibrary.ResourceLibrary):
    grok.name("tag.styles")
    megrok.resourcelibrary.directory('resources')
    megrok.resourcelibrary.include('tags.css')

try:
    import menhir.simple.livesearch.base
    class TagLiveSearchLibrary(megrok.resourcelibrary.ResourceLibrary):
        grok.name("tag.livesearch")
        megrok.resourcelibrary.directory('resources')
        megrok.resourcelibrary.depend(
                    menhir.simple.livesearch.base.LiveSearchLibrary)
        

    from dolmen.app.layout.master import DolmenHeader

    class TagLiveSearch(grok.Viewlet):
        grok.name('tag.livesearch')
        grok.viewletmanager(DolmenHeader)

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
            TagLiveSearchLibrary.need()
        

    class TagSearchResults(grok.View):
        grok.name("tag-search")
        
        @Lazy
        def engine(self):
            return getUtility(ITaggingEngine)
        
        def update(self, search_term):
            """
            search for tags to suggest
            """
            user_tags = IUserTagging(self.context).tags
            if search_term:
                # TODO is there a better way for filtering than asking all tags ?
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

class TagsViewlet(grok.Viewlet):
    grok.view(IDisplayView)
    grok.viewletmanager(master.DolmenTop)
    grok.require("dolmen.content.View")
    grok.order(100)
    
    def cloud(self):
        return self.engine.cloud(items=(self.contextId,))
    
    def update(self):
        TagResources.need()
        self.form = getMultiAdapter((self.context, self.request),
                                    name = u'user_tags_add')
        self.form.update()
        self.form.updateForm()
        
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

          
class AddTag(Form):
    grok.name('user_tags_add')
    prefix = "tags"
    ignoreContext = True
    cancellable(False)

    fields = Fields(Field(
        TextLine(title = u'Add tag', required = True),
        name = "tag"
        ))
    
    @button.buttonAndHandler(u'Add', name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
        else:
            userTagging = IUserTagging(self.context)
            userTagging.tags |= set([data['tag'],])
            notify(ObjectModifiedEvent(self.context))
            self.flash('Added tag %s' % data['tag'])
            self.redirect(self.url(self.context))


class CameFromView(grok.View):
    """View handling a came_from parameter
    """
    grok.baseclass()
    
    def render(self):
        url = self.request.get('came_from', None)
        if url is not None:
            self.redirect(url)
        self.redirect(self.url(self.context))

            
class QuickAddTag(CameFromView):
    grok.name('user_tag_quick_add')
    
    def update(self):
        tag = self.request.get('tag', None)
        if tag is not None:
            userTagging = IUserTagging(self.context)
            userTagging.tags |= set([tag,])


class QuickRemoveTag(CameFromView):
    grok.name('user_tag_quick_remove')
    
    def update(self):
        tag = self.request.get('tag',None)
        if tag is not None:
            userTagging = IUserTagging(self.context)
            userTagging.tags -= set([tag,])
    
            
