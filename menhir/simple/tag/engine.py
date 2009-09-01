# -*- coding: utf-8 -*-

import grok
import lovely.tag

from dolmen.app.site import IDolmen
from zope.component import getSiteManager
from zope.app.container.interfaces import IObjectAddedEvent


class EngineUtility(grok.LocalUtility):
    """Tag engine contained in a utility.
    """
    grok.provides(lovely.tag.interfaces.ITaggingEngine)
    
    def __init__(self, *args, **kwargs):
        self._engine = lovely.tag.TaggingEngine()
    
    def __getattr__(self, name):
        # delegate all
        return getattr(self._engine, name)


@grok.subscribe(IDolmen, grok.IObjectAddedEvent)
def register_engine(ob, event):
    """Register utility (at site creation)
    """
    sm = getSiteManager(ob)
    sm.registerUtility(EngineUtility(), lovely.tag.interfaces.ITaggingEngine)
