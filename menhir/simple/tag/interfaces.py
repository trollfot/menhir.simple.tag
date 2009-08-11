import zope.interface as zi
import zope.schema as zs
# we use interface of lovely.tag
from lovely.tag.interfaces import ITaggingEngine, ITaggable


class IUserTagAdding(zi.Interface):
    # FIXME i18n
    new_tag = zs.TextLine(title = u'Add tag', required = False)

    
