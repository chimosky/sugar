import logging

from sugar.graphics.menuicon import MenuIcon
from view.clipboardmenu import ClipboardMenu
from sugar.activity import ActivityFactory
from sugar.clipboard import clipboardservice
from sugar import util

class ClipboardIcon(MenuIcon):

    def __init__(self, menu_shell, object_id, name):
        MenuIcon.__init__(self, menu_shell)
        self._object_id = object_id
        self._name = name
        self._percent = 0
        self._preview = None
        self.connect('activated', self._icon_activated_cb)
        self._menu = None
        
    def create_menu(self):
        self._menu = ClipboardMenu(self._name, self._percent, self._preview)
        self._menu.connect('action', self._popup_action_cb)
        return self._menu

    def set_state(self, name, percent, icon_name, preview):
        self._name = name
        self._percent = percent
        self._preview = preview
        self.set_icon_name(icon_name)
        if self._menu:
            self._menu.set_state(name, percent, preview)

    def _get_activity_for_mime_type(self, mime_type):
        # FIXME: We should use some kind of registry that could be extended by
        # newly installed activities.
        if mime_type == "application/pdf":
            return "org.laptop.sugar.Xbook"
        elif mime_type in ["application/msword", "text/rtf", "application/rtf"]:
            return "org.laptop.AbiWordActivity"
        else:
            return None

    def _activity_create_success_cb(self, handler, activity):
        activity.start(util.unique_id())
        activity.execute("open_document", [self._object_id])

    def _activity_create_error_cb(self, handler, err):
        pass

    def _icon_activated_cb(self, icon):
        if self._percent < 100:
            return

        cb_service = clipboardservice.get_instance()        
        (name, percent, icon, preview, format_types) =  \
            cb_service.get_object(self._object_id)
        if not format_types:
            return

        logging.debug("_icon_activated_cb: " + self._object_id)
        activity_type = self._get_activity_for_mime_type(format_types[0])        
        if not activity_type:
            return

        # Launch the activity to handle this item
        handler = ActivityFactory.create(activity_type)
        handler.connect('success', self._activity_create_success_cb)
        handler.connect('error', self._activity_create_error_cb)
                
    def _popup_action_cb(self, popup, action):
        self.popdown()
        
        if action == ClipboardMenu.ACTION_STOP_DOWNLOAD:
            raise "Stopping downloads still not implemented."
        elif action == ClipboardMenu.ACTION_DELETE:
            cb_service = clipboardservice.get_instance()
            cb_service.delete_object(self._object_id)

    def get_object_id(self):
        return self._object_id
