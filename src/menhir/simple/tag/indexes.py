# -*- coding: utf-8 -*-

import grokcore.component as grok
from lovely.tag.interfaces import ITaggable, ITagging
from zope.index.text.interfaces import ISearchableText


class TaggedSearchable(grok.Adapter):
    grok.context(ITaggable)
    grok.implements(ISearchableText)

    def getSearchableText(self):
        tags = ITagging(self.context).getTags()
        return (self.context.title,) + tuple(tags)
