import _thread as _ab_t
import time

_ab_const = {
    'MIN_LED_POS': 1,
    'MAX_LED_POS': 25,
    'EYE_POSITIONS': {
        'POS_TOP': [2, 4],
        'POS_UP': [7, 9],
        'POS_NORMAL': [12, 14],
        'POS_RIGHT': [11, 13],
        'POS_LEFT': [13, 15],
        'POS_DOWN': [17, 19],
        'POS_BOTTOM': [22, 24],
    },
    'CHEEK_POSITIONS': {
        'POS_TOP': [6, 10],
        'POS_UP': [11, 15],
        'POS_NORMAL': [16, 20],
        'POS_RIGHT': [19],
        'POS_LEFT': [17],
        'POS_DOWN': [21, 25],
        'POS_BOTTOM': [],
    },
    'ORIENTATIONS': {
        'ORI_NORMAL': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
        'ORI_RIGHT': [21, 16, 11, 6, 1, 22, 17, 12, 7, 2, 23, 18, 13, 8, 3, 24, 19, 14, 9, 4, 25, 20, 15, 10, 5],
        'ORI_UPSIDE_DOWN': [25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        'ORI_LEFT': [5, 10, 15, 20, 25, 4, 9, 14, 19, 24, 3, 8, 13, 18, 23, 2, 7, 12, 17, 22, 1, 6, 11, 16, 21],
    },
    'BLINK_INTERVAL': {
        'LOOP': 1,
        'OPEN': 500,
        'CLOSE': 100,
        'INTERVAL': 1000,
    },
    'DEFAULT_BLINK_INTERVAL_FUNCTION': '_ab_get_blink_interval',
}


def _ab_get_const(key):
   return _ab_const[key]


def _ab_get_rgb(r, g, b):
    return int('0x{:02x}{:02x}{:02x}'.format(r, g, b))


_ab_global = {
    'eye_color': ${_eye_color},
    'cheek_color': ${_cheek_color},
    'background_color': ${_background_color},
    'position': 'POS_NORMAL',
    'orientation': 'ORI_NORMAL',
    'blink_thread_running': False,
    'blink_running': False,
    'blink_interval_function': _ab_get_const('DEFAULT_BLINK_INTERVAL_FUNCTION'),
}


def _ab_get_global(key):
    return _ab_global[key]


def _ab_set_global(key, val):
    _ab_global[key] = val


def _ab_get_led_position(orientation, position):
    return _ab_get_const('ORIENTATIONS')[orientation][position - 1]


def _ab_fill(color):
    rgb.setColorFrom(_ab_get_const('MIN_LED_POS'), _ab_get_const('MAX_LED_POS'), color)  # noqa: F821


def _ab_set_color(pos, color, orientation):
    rgb.setColor(_ab_get_led_position(orientation, pos), color)  # noqa: F821


def _ab_get_eye_position(pos):
    return _ab_get_const('EYE_POSITIONS')[pos]


def _ab_get_cheek_position(pos):
    return _ab_get_const('CHEEK_POSITIONS')[pos]


def _ab_set_eyes(pos, color, orientation):
    for _p in _ab_get_eye_position(pos):
        _ab_set_color(_p, color, orientation)


def _ab_set_cheeks(pos, color, orientation):
    for _p in _ab_get_cheek_position(pos):
        _ab_set_color(_p, color, orientation)


def _ab_set_face(pos, eye_color, cheek_color, orientation):
    _ab_set_eyes(pos, eye_color, orientation)
    _ab_set_cheeks(pos, cheek_color, orientation)


def _ab_show_face():
    _ab_fill(_ab_get_background_color())
    _ab_set_face(_ab_get_face_position(), _ab_get_eye_color(), _ab_get_cheek_color(), _ab_get_orientation())


def _ab_clear_face():
    _bg_color = _ab_get_background_color()
    _ab_set_face(_ab_get_face_position(), _bg_color, _bg_color, _ab_get_orientation())


def _ab_open_eyes():
    _ab_set_eyes(_ab_get_face_position(), _ab_get_eye_color(), _ab_get_orientation())


def _ab_close_eyes():
    _ab_set_eyes(_ab_get_face_position(), _ab_get_background_color(), _ab_get_orientation())


def _ab_set_eye_color(color):
    _ab_set_global('eye_color', color)


def _ab_get_eye_color():
    return _ab_get_global('eye_color')


def _ab_set_cheek_color(color):
    _ab_set_global('cheek_color', color)


def _ab_get_cheek_color():
    return _ab_get_global('cheek_color')


def _ab_set_background_color(color):
    _ab_set_global('background_color', color)


def _ab_get_background_color():
    return _ab_get_global('background_color')


def _ab_set_orientation(orientation):
    _ab_set_global('orientation', orientation)


def _ab_get_orientation():
    return _ab_get_global('orientation')


def _ab_set_face_position(position):
    _ab_set_global('position', position)


def _ab_get_face_position():
    return _ab_get_global('position')


def _ab_is_ascii(s):
    return all(ord(c) < 128 for c in s)


def _ab_get_function_name(name):
    if _ab_is_ascii(name):
        return name
    else:
        return ''.join(['_{:02X}'.format(b) for b in name.encode()])


_ab_lock = _ab_t.allocate_lock()


def _ab_blink_task():
    while _ab_get_global('blink_thread_running'):
        if _ab_get_global('blink_running'):
            with _ab_lock:
                _func = _ab_get_function_name(_ab_get_global('blink_interval_function'))
                _intervals = globals()[_func]()
                for _ in range(_intervals.get('LOOP', 1)):
                    time.sleep_ms(_intervals.get('OPEN', 500))
                    _ab_close_eyes()
                    time.sleep_ms(_intervals.get('CLOSE', 100))
                    _ab_open_eyes()
                time.sleep_ms(_intervals.get('INTERVAL', 1000))
        else:
            time.sleep_ms(1)


def _ab_set_blink_interval(interval):
    _ab_set_global('blink_interval', interval)


def _ab_start_blink(func=None):
    if not _ab_get_global('blink_thread_running'):
        _ab_set_global('blink_thread_running', True)
        _ab_t.start_new_thread(_ab_blink_task, ())
    _ab_set_global('blink_interval_function', func or '_ab_get_blink_interval')
    _ab_set_global('blink_running', True)


def _ab_stop_blink():
    _ab_set_global('blink_running', False)


def _ab_terminate_blink():
    _ab_set_global('blink_thread_running', False)


def _ab_get_blink_interval():
    return _ab_get_const('BLINK_INTERVAL')
