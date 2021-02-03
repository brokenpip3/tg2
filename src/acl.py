"""from https://botogram.dev/docs/0.6.1/custom-components"""

import botogram

class MyACL(botogram.Component):
    """Create custom class: filter message by id"""
    component_name = "myacl"

    def __init__(self, allowed=None):
        if allowed is None:
            allowed = []
        self.allowed = allowed
        self.add_before_processing_hook(self.filter)

    def filter(self, chat, message):
        if message.sender.id not in self.allowed:
            chat.send(f"YOU ARE NOT ALLOWED\nplease add your id `{message.sender.id}` to acl list or contact the administrator", syntax="markdown")
            return True  # Stop processing the update