import rumps
from multiprocessing import Process, Pipe
import os
import configparser
import service

ote = {
    'enabled': True,
    'exit': False,
    'reload_config': False,
    'config': {
        'word_listeners': {}
    }
}
parent_conn, child_conn = Pipe()


class OpenTextExpanderApp(rumps.App):

    btn = {
        "listeners_enabled": "\u2713 Listeners enabled",
        "listeners_disabled": "\u2717 Listeners disabled",
        "reload_config": "\u21BA Reload config",
        "quit_app": "\u2717 Quit OpenTextExpander",
    }
    
    def __init__(self):
        super(OpenTextExpanderApp, self).__init__("OTE")
        rumps.debug_mode(True)
        self.menu = [self.btn['listeners_enabled'], self.btn["reload_config"], self.btn["quit_app"]]
        self.quit_button = None
        self.reload_config(None)

    @rumps.clicked(btn["reload_config"])
    def reload_config(self, sender):
        config_filepath = os.path.expanduser("~") + r"/ote.ini"

        if not os.path.exists(config_filepath):
            # write empty config
            with open(config_filepath, 'w') as file:
                file.writelines(["[OTE_WORD_LISTENERS]", ""])
        config = configparser.ConfigParser()
        config.read(config_filepath)
        ote['config']['word_listeners'] = config['OTE_WORD_LISTENERS']

        ote['reload_config'] = True
        parent_conn.send(ote)
        ote['reload_config'] = False

    @rumps.clicked(btn['listeners_enabled'])
    def onoff(self, sender):
        global ote
        ote['enabled'] = not ote['enabled']
        sender.title = self.btn["listeners_disabled"] if not ote['enabled'] else self.btn['listeners_enabled']
        parent_conn.send(ote)

    @rumps.clicked(btn["quit_app"])
    def quit(self, _):
        global ote
        ote['exit'] = True
        parent_conn.send(ote)
        rumps.quit_application()
    

if __name__ == "__main__":
    p = Process(target=service.run, args=(child_conn,))
    p.start()
    OpenTextExpanderApp().run()
    p.join()