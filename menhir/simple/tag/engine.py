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
    
    # make it editable attributes with a form
    min_tag_size = 0.4
    max_tag_size = 2
    base_tag_size = 1 # the size for one tag alone eg.
    expected_cloud_width = 20 # expected width in em
    
    def cloud(self, items):
        """
        compute tag info
        
        - giving respective weights
        - ordering to have tags harmonously placed 
        
        
        >>> class dummyEngine(object):
        ...     def getCloud(self, items):
        ...         return (("toto", 20),("tata", 10), ("titi", 5))
        ... 
        >>> a = EngineUtility()
        >>> a.base_tag_size = 1
        >>> a.max_tag_size = 5
        >>> a.min_tag_size = .2
        >>> a.expected_cloud_width = 10
        
        >>> setattr(a, "_engine", dummyEngine())
        >>> a.cloud(0)
        [('titi', 0.20000000000000001), ('toto', 3.0), ('tata', 1.1333333333333333)]

        >>> class dummyEngine2(dummyEngine):
        ...     def getCloud(self, items):
        ...         return (("toto", 1),("tata", 1))
        ... 
        >>> setattr(a, "_engine", dummyEngine2())
        >>> a.cloud(O)        
        [('toto', 0.5), ('tata', 0.5)]
        
        FIXME :add test with empty sequence
        FIXME review result values  as I changed computation
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
            lines_nb = sum(w for w, dummy in widths) / self.expected_cloud_width + 1
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
    
    
    def __init__(self, *args, **kwargs):
        self._engine = lovely.tag.TaggingEngine()
        # put in context
        setattr(self._engine, '__parent__', self)
    
    def __getattr__(self, name):
        # delegate all
        return getattr(self._engine, name)


@grok.subscribe(IDolmen, grok.IObjectAddedEvent)
def register_engine(ob, event):
    """Register utility (at site creation)
    """
    sm = getSiteManager(ob)
    e = EngineUtility()
    sm.registerUtility(e, lovely.tag.interfaces.ITaggingEngine)
    # set in context as lovely.tag needs it
    e.__parent__ = ob
    
