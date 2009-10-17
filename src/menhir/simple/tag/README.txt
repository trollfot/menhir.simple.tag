=================
menhir.simple.tag
=================

Computing
=========

compute tag info
        
- giving respective weights
- ordering to have tags harmonously placed 
        
   >>> from menhir.simple.tag import engine

   >>> class dummyEngine(object):
   ...     def getCloud(self, items):
   ...         return (("toto", 20),("tata", 10), ("titi", 5))
   ... 
   >>> a = engine.EngineUtility()
   >>> a.base_tag_size = 1
   >>> a.max_tag_size = 5
   >>> a.min_tag_size = .2
   >>> a.expected_cloud_width = 10
        
   >>> setattr(a, "_engine", dummyEngine())
   >>> a.cloud(0)
   [('titi', 0.20000000000000001), ('toto', 2.5), ('tata', 0.96666666666666656)]

   >>> class dummyEngine2(dummyEngine):
   ...     def getCloud(self, items):
   ...         return (("toto", 1),("tata", 1))
   ... 
   >>> setattr(a, "_engine", dummyEngine2())
   >>> a.cloud(0)        
   [('toto', 1.0), ('tata', 1.0)]
        
   >>> class dummyEngine2(dummyEngine):
   ...     def getCloud(self, items):
   ...         return ()
   ... 
   >>> setattr(a, "_engine", dummyEngine2())
   >>> a.cloud(0)
   []
