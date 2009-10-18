"""
"""

import grokcore.view as grok
import lovely.tag.interfaces

import dolmen.app.layout


from menhir.simple.tag.interfaces import ITags
import menhir.simple.tag.engine as engine





class Tags(dolmen.app.layout.Index):
    """
    default view on tag engine, return all tags
    
    TODO better a big tag cloud ?
    """
    grok.context(engine.EngineUtility)
    
    def update(self):
        self.items = self.context.getTags()
        

class Tagged(dolmen.app.layout.Index):
    """
    View that list all objects with a certain tag
    
    FIXME : I would better have urls like list/tag and list/tag1+tag2 and so on
    """
    grok.context(engine.Tags)
        
    
    def update(self, start = 0, size = 30):
        """
        display list using a batch
        """
        objects = self.context.tagged(start = start, size = size)
        self.items = []
        for obj in objects:
            self.items.append(dict(title = obj.title,
                                    url = self.url(obj)))
        self.related = self.context.related()
        self.tags = ", ".join(self.context.values)
        self.current = self.context.values[-1]
            
        
        
    
