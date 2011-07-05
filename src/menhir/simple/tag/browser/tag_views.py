# -*- coding: utf-8 -*-

import grokcore.view as grok
import lovely.tag.interfaces
import dolmen.app.layout
import menhir.simple.tag.engine as engine
from menhir.simple.tag.browser import views
from menhir.simple.tag.interfaces import ITags


class Tags(dolmen.app.layout.Index):
    """Default view on tag engine, return all tags
    """
    grok.context(engine.EngineUtility)

    def update(self):
        views.TagStyles.need()
        cloudInfo = self.context.global_cloud()
        self.info = ({"tag": i[0], "weight": i[1]} for i in cloudInfo)


class Tagged(dolmen.app.layout.Index):
    """View that list all objects with a certain tag
    """
    grok.context(engine.Tags)

    def update(self, start = 0, size = 30):
        """Display list using a batch
        """
        views.TagStyles.need()
        objects = self.context.tagged(start = start, size = size)
        self.items = []
        for obj in objects:
            self.items.append(
                dict(title = obj.title, url = self.url(obj)))
        self.related = self.context.related()
        self.tags = ", ".join(self.context.values)
        self.current = self.context.values[-1]
