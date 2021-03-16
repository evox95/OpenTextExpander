import keyboard

_ote = {}


def _watch_for_word(lookout, replace_with):
    def word_typed():
        if not _ote.get('enabled', False):
            print('- word \'%s\' typed but OTE is disabled' % lookout)
            return
        for i in range(len(lookout) + 1):
            keyboard.press('backspace')
        keyboard.write(replace_with)
    print('+ \'%s\' - \'%s\'' % (lookout, replace_with))
    keyboard.add_word_listener(lookout, callback=word_typed, timeout=2, triggers=['space'])


def _add_word_listeners():
    keyboard.unhook_all()
    for lookout, replace_with in _ote['config']['word_listeners'].items():
        _watch_for_word(lookout, replace_with)


def run(child_conn):
    global _ote
    try:
        while not _ote.get('exit', False):
            _ote = child_conn.recv()
            if _ote['reload_config']:
                _add_word_listeners()
    except EOFError:
        pass
    
    keyboard.unhook_all()