
import json
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized
from OFS.Image import File

from .config import get_config
from os.path import splitext

def save_wordlist(context, request):
    config = get_config()
    lang = request.form.get('lang')
    content_json = request.form.get('content')
    wordlist_path = config['wordlist_path']
    # must remove leading /, it breaks traversal. In any
    # case, we traverse from the portal root.
    assert wordlist_path.startswith('/')
    basename, ext = splitext(wordlist_path[1:])
    path = '%s_%s%s' % (basename, lang, ext)
    portal_url = getToolByName(context, 'portal_url')
    portal = portal_url.getPortalObject()
    try:
        file_content = portal.unrestrictedTraverse(path)
    except KeyError:
        split_path = path.rsplit('/', 1)
        if len(split_path) > 1:
            folder_path, name = split_path
            try:
                folder = portal.unrestrictedTraverse(folder_path)
            except KeyError:
                raise RuntimeError, 'Cannot save wordlist, because folder does not exists [%s]' % (folder_path, )
        else:
            folder = portal
            name = split_path[0]
        try:
            file_content = folder[name] = File(name, '', '[]', 'application/json', '')
        except Unauthorized:
            raise RuntimeError, 'Cannot save wordlist, no permission to create object in folder [%s]' % (path, )
    # No need to clean the list, as the client has done it already.
    file_content.data = content_json

class SaveWordlistView(BrowserView):
    """
    """
    def __call__(self):
        return save_wordlist(self.context, self.request)
