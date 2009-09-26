"""

About
=====

Tags can be added to any object that has an intid and implements 
lovely.tag.interfaces.ITaggable

Let's create a simple content providing Ilocation so that it get's an intid::

  >>> import lovely.tag.interfaces
  >>> import zope.location.interfaces
  >>> import grok
  >>> class ContentType(grok.Model):
  ...     '''Very basic content type'''
  ...     grok.implements(lovely.tag.interfaces.ITaggable,
  ...                     zope.location.interfaces.ILocation)
  
ILocation makes it get an intid

  >>> from zope.app.intid.interfaces import IIntIds
  >>> content = ContentType()
  >>> intids = getUtility(IIntIds)
  >>> intids.getId(content) is not None
  True
  



"""
