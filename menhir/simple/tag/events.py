from zope.interface import implements, Attribute
import zope.component.interfaces

class ITagsModfiedEvent(zope.component.interfaces.IObjectEvent):
    """tags were modified for an object"""
    
    user = Attribute("User that modified his tagging")
    
    tags = Attribute("New tags for this user")



class TagsModifiedEvent(zope.component.interfaces.ObjectEvent):
    implements(ITagsModfiedEvent)
    
    object = None
    
    def __init__(self, object, user = None, tags = None):
        super(TagsModifiedEvent, self).__init__(object)
        self.user = user
        self.tags = tags

