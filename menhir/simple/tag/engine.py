import lovely.tag
import interfaces
import grok
import dolmen.app.site.interfaces as di 
import zope.component as zc

class EngineUtility(grok.LocalUtility):
    """
    Tag engine contained in a utility
    """
    grok.provides(interfaces.ITaggingEngine)
    
    def __init__(self, *args, **kwargs):
        super(EngineUtility, self).__init__(*args, **kwargs)
        self._engine = lovely.tag.TaggingEngine()
    
    # delegate all
    def __getattr__(self, name):
        return getattr(self._engine, name)


# register this at site creation
@grok.subscribe(di.IDolmen, grok.IObjectAddedEvent)
def register_engine(ob, event):
    """
    register utility (at site creation)
    """
    sm = zc.getSiteManager(ob)
    e = EngineUtility()
    sm.registerUtility(e, grok.provides.bind().get(e))
    
