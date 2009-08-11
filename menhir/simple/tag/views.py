import dolmen
import dolmen.content
import grok
import zope.app.intid.interfaces as intid_interfaces
from dolmen.app.layout import master
import megrok.z3cform
import interfaces
import lovely.tag.interfaces as tag_interfaces
import zope.component as zc
import z3c.form 
from zope.cachedescriptors.property import Lazy


class TagsViewlet(grok.Viewlet):
    """
    
    TODO : yet all tag have same size use tag cloud when possible
    
    """
    grok.context(dolmen.content.IBaseContent)
    grok.viewletmanager(master.DolmenAboveBody)
    grok.require("dolmen.content.View") # FIXME chosse right in dolmen.app.security
    grok.order(100)
    
    
    def update(self):
        self.form = zc.getMultiAdapter((self.context, self.request),
                                    name = u'user_tags_add')
        self.form.update()
        self.form.updateForm()
        
        self.context_url = self.view.url(self.context)
        self.actual_url = str(self.request.URL)
        
            
        try:
            cloudInfo = self.engine.getCloud(items=(self.contextId,))
        
            # to know where to put + or -
            self.user_tags = tag_interfaces.IUserTagging(self.context).tags
            # FIXME some more thing to do here or see if lovely can already do this
            # - normalize values
            # - batch items per line
            self.cloudInfo = [dict(tag = tag, 
                                    weight = weight,
                                    marked = tag in self.user_tags,)
                        for tag, weight in sorted(cloudInfo, key = lambda i:i[1])]

        except KeyError:
            self.user_tags = []
            self.cloudInfo = []
    
    @Lazy
    def engine(self):
        return zc.getUtility(interfaces.ITaggingEngine)
    
    @Lazy
    def contextId(self):
        intids = zc.getUtility(intid_interfaces.IIntIds)
        return intids.getId(self.context)


class AddTag(megrok.z3cform.Form):
    grok.name('user_tags_add')
    grok.context(interfaces.IUserTagAdding)

    fields = z3c.form.field.Fields(interfaces.IUserTagAdding)
    form_name = u"Add a new tag"
    
    @megrok.z3cform.button.buttonAndHandler(u'Add', name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
        userTagging = tag_interfaces.IUserTagging(self.context)
        userTagging.tags |= set([data['new_tag'],])
        
class CameFromHandling(object):
    """
    view handling a came_from parameter
    """
    def render(self):
        """
        Renders redirecting to came_from url
        """
        url = self.request.get('came_from',None)
        if url:
            self.request.response.redirect(url)
        else:    
            return "done"

            
class QuickAddTag(CameFromHandling, grok.View):
    grok.name('user_tag_quick_add')
    grok.context(interfaces.IUserTagAdding)

    def update(self):
        """
        """
        tag = self.request.get('tag',None)
        if tag:
            userTagging = tag_interfaces.IUserTagging(self.context)
            userTagging.tags |= set([tag,])

class QuickRemoveTag(CameFromHandling, grok.View):
    grok.name('user_tag_quick_remove')
    grok.context(interfaces.IUserTagAdding)
    
    def update(self):
        """
        """
        tag = self.request.get('tag',None)
        if tag:
            userTagging = tag_interfaces.IUserTagging(self.context)
            userTagging.tags -= set([tag,])
    
            
