# -*- coding: utf-8 -*-

import zope.component.interfaces
from zope.interface import implements, Attribute


class ITagsModfiedEvent(zope.component.interfaces.IObjectEvent):
    """tags were modified for an object
    """
    tags = Attribute("New tags for this user")
    user = Attribute("User that modified his tagging")
    

class TagsModifiedEvent(zope.component.interfaces.ObjectEvent):
    implements(ITagsModfiedEvent)
        
    def __init__(self, object, user=None, tags=None):
        super(TagsModifiedEvent, self).__init__(object)
        self.user = user
        self.tags = tags
