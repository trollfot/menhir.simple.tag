# -*- coding: utf-8 -*-

import grok
import zope.event
import lovely.tag

from dolmen.app.site import IDolmen
from menhir.simple.tag import events
from zope.component import getSiteManager, getUtility
from zope.app.intid.interfaces import IIntIds
from zope.cachedescriptors.property import Lazy

try:
    from z3c.batching.batch import Batch
except ImportError:
    # batch that does nothing
    Batch = lambda x, *args: x 



class TaggingEngine(lovely.tag.TaggingEngine):
    
    def update(self, item, user, tags):
        """Fires an event on update
        """
        super(TaggingEngine, self).update(item, user, tags)
        # retrieve object to be able to fire event
        intIds = zope.component.getUtility(IIntIds, context=self)
        obj = intIds.getObject(item)
        zope.event.notify(events.TagsModifiedEvent(obj, user, tags))
        

class EngineUtility(grok.Model):
    """Tag engine.
    """
    grok.provides(lovely.tag.interfaces.ITaggingEngine)
    
    # make it editable attributes with a form
    min_tag_size = 0.6
    max_tag_size = 2.5
    base_tag_size = 1.5 # the size for one tag alone eg.
    expected_cloud_width = 15 # expected width in em

    def __init__(self, *args, **kwargs):
        self._engine = TaggingEngine()
        # put in context
        setattr(self._engine, '__parent__', self)
    
    def __getattr__(self, name):
        # delegate all
        return getattr(self._engine, name)
    
    def cloud(self, items):
        """Computing of the weights.
        """
        cloudInfo = self._engine.getCloud(items=items)
        if cloudInfo:
            # we do not always user min and max, we use those values
            # only if difference between tags is big enough
            minw = min(weight for tag, weight in cloudInfo)
            maxw = max(weight for tag, weight  in cloudInfo)
            balance = maxw / float(minw) - 1
            stronger = min(self.base_tag_size + balance / 2,
                             float(self.max_tag_size))
            weaker = max(self.base_tag_size - balance / 2, 
                             float( self.min_tag_size))
            
            # now that a scale problem
            if maxw == minw:
                scale = 1
            else:
                scale = (stronger - weaker) / (maxw - minw)
            relativeCloud = [(tag, (weight - minw) * scale + weaker) 
                                for tag, weight in cloudInfo]
            
            # ordering 
            # get estimated width of each tag
            widths = list((w * len(t), (t,w)) for t,w in relativeCloud)
            
            # estimates how many lines we will need
            lines_nb = (sum(w for w, dummy in widths) /
                        self.expected_cloud_width + 1)
            space = [self.expected_cloud_width ,] * int(lines_nb)
            cloudbyline = [[] for i in range(int(lines_nb))]
            
            # order by width
            widths.sort(key = lambda e: e [0])
            
            # add line by line, with line having more space
            for width, (tag, weight) in widths:
                index = space.index(max(space))
                space[index] -= width
                cloudbyline[index].append((tag, weight))
            cloud = []
            
            # append lines reverting one over two
            transfo, nexttransfo = lambda x:x, reversed
            for line in cloudbyline:
                cloud.extend(line)
                transfo, nexttransfo = nexttransfo, transfo
        else:
            cloud = []
        return cloud
        
    @Lazy
    def intids(self):
        """return intids utility"""
        return getUtility(IIntIds)


    @Lazy
    def getId(self):
        """
        given id return object
        
        shortcut to a call to IntId
        """
        return self.intids.getId

    @Lazy
    def getObject(self):
        """
        given id return object
        
        shortcut to a call to IntId
        """
        return self.intids.getObject
            
    

@grok.subscribe(IDolmen, grok.IObjectAddedEvent)
def register_engine(site, event):
    """Register utility (at site creation)
    """
    # Creation of the engine
    engine = EngineUtility()
    zope.event.notify(grok.ObjectCreatedEvent(engine))

    # Persistence of the engine in the site.
    site[u'tags'] = engine

    # Registration of the engine as a local utility
    sm = getSiteManager(site)
    sm.registerUtility(engine, lovely.tag.interfaces.ITaggingEngine)


        

import interfaces

class Tags(grok.Model):
    """a class representing on or more tags""" 
    grok.provides(interfaces.ITags)
    
    def __init__(self, values):
        self.values = tuple(values)
    
    @Lazy
    def engine(self):
        return getUtility(lovely.tag.interfaces.ITaggingEngine)
    
        
    def tagged(self, size = None, start = 0):
        """
        All ids of elements with this tag
        
        return an iterator
        if size is not None, result is batched
        """
        engine = self.engine
        ids = intersect_sets(engine.getItems(tags=(v,)) for v in self.values)
                
        if size is not None:
            #use batch
            try:
                # FixMe Batch try to do a self.sequence[self.start: self.end+1]
                # so we put list(ids) that's not cool
                ids = Batch(list(ids), start = start, size = size)
            except IndexError:
                ids = []
        return (engine.getObject(id) for id in ids)
        
    def related(self):
        """
        list of related tags
        """
        engine = self.engine
        return intersect_sets(engine.getRelatedTags(v) for v in self.values)
            
        
        
def intersect_sets(sets):
    """
    return intersection of all sets
    """
    result = set()
    try:
        result = sets.next()
        while True:
            result &= sets.next()
    except StopIteration:
        pass
    return result
        
    


class TagTraverser(grok.Traverser):
    """A nice custom traverser.
    """
    grok.context(EngineUtility)
    
    def traverse(self, name):
        """
        Return representation of tag implementing ITag
        """
        
        return Tags((name,))

class MultiTagTraverser(grok.Traverser):
    """A nice custom traverser.
    """
    grok.context(Tags)
    
    def traverse(self, name):
        """
        Return representation of tag implementing ITag
        """
        return Tags(self.context.values + (name,))
