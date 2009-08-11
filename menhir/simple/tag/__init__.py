# module
import zope.interface as zi
import zope.component as zc
import interfaces
import dolmen.content
from lovely import tag

# FIXME bad ?
zi.classImplements(dolmen.content.BaseContent, interfaces.ITaggable)
zi.classImplements(dolmen.content.BaseContent, interfaces.IUserTagAdding)
zc.provideAdapter(tag.UserTagging)
zc.provideAdapter(tag.Tagging)
