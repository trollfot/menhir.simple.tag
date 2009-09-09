# -*- coding: utf-8 -*-

import grokcore.viewlet as grok

from zope.schema import TextLine
from zope.app.intid.interfaces import IIntIds
from zope.cachedescriptors.property import Lazy
from zope.component import getUtility, getMultiAdapter
from lovely.tag.interfaces import IUserTagging, ITaggingEngine, ITaggable

from dolmen.content import IBaseContent
from dolmen.forms.base import Field, Fields, button
from dolmen.app.layout import master, IDisplayView, Form

grok.context(ITaggable)


class TagsViewlet(grok.Viewlet):
    grok.view(IDisplayView)
    grok.viewletmanager(master.DolmenTop)
    grok.require("dolmen.content.View")
    grok.order(100)
    
    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name = u'user_tags_add')
        self.form.update()
        self.form.updateForm()
        
        self.context_url = self.view.url(self.context)
        self.actual_url = str(self.request.URL)
        
        try:
            cloudInfo = self.engine.getCloud(items=(self.contextId,))
            self.user_tags = IUserTagging(self.context).tags
            self.cloudInfo = [{
                'tag': tag,
                'weight': weight,
                'marked': tag in self.user_tags
                } for tag, weight in cloudInfo]
 
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
    
            
