import _thread as _ab_t
import sys
import time

_ab_const = {
    'VERSION': "v0.0.6",
    'MIN_LED_POS': 1,
    'MAX_LED_POS': 25,
    'LED_WIDTH': 5,
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
    'DIGITS': [
        [2, 3, 4, 7, 9, 12, 14, 17, 19, 22, 23, 24],
        [3, 7, 8, 13, 18, 22, 23, 24],
        [2, 3, 4, 9, 12, 13, 14, 17, 22, 23, 24],
        [2, 3, 4, 9, 12, 13, 14, 19, 22, 23, 24],
        [2, 4, 7, 9, 12, 13, 14, 19, 24],
        [2, 3, 4, 7, 12, 13, 14, 19, 22, 23, 24],
        [2, 3, 4, 7, 12, 13, 14, 17, 19, 22, 23, 24],
        [2, 3, 4, 9, 14, 19, 24],
        [2, 3, 4, 7, 9, 12, 13, 14, 17, 19, 22, 23, 24],
        [2, 3, 4, 7, 9, 12, 13, 14, 19, 22, 23, 24],
    ],
    'SYMBOLS': {
        '-' : [12, 13, 14],
        '.' : [23],
        '!' : [3, 8, 13, 23],
    },
    'ALPHABETS': {
        'a': [2, 3, 4, 9, 12, 13, 14, 17, 19, 22, 23, 24],
        'A': [3, 7, 9, 12, 13, 14, 17, 19, 22, 24],
        'e': [2, 3, 4, 6, 8, 12, 13, 14, 17, 22, 23, 24],
        'E': [2, 3, 4, 7, 12, 13, 14, 17, 22, 23, 24],
        'M': [2, 4, 7, 8, 9, 12, 14, 17, 19, 22, 24],
        'r': [1, 6, 8, 9, 11, 12, 15, 16, 21],
        'R': [2, 3, 7, 9, 12, 13, 17, 19, 22, 24],
        's': [3, 4, 7, 12, 13, 14, 19, 22, 23],
        'S': [2, 3, 4, 7, 12, 13, 14, 19, 22, 23, 24],
        'x': [12, 14, 18, 22, 24],
        'X': [2, 4, 7, 9, 13, 17, 19, 22, 24],
        'y': [2, 4, 7, 9, 12, 13, 14, 19, 22, 23, 24],
        'Y': [2, 4, 7, 9, 12, 13, 14, 19, 23],
    },
    'BLINK_INTERVAL': {
        'LOOP': 1,
        'OPEN': 500,
        'CLOSE': 100,
        'INTERVAL': 1000,
    },
    'DEFAULT_BLINK_INTERVAL_FUNCTION': '_ab_get_blink_interval',
}
_ab_const['CHAR_TYPES'] = [
    _ab_const['ALPHABETS'], _ab_const['SYMBOLS'], {str(d): v for d, v in enumerate(_ab_const['DIGITS'])}
]

_ab_lock = _ab_t.allocate_lock()

if 'imu' not in sys.modules:
    import imu
    imu0 = imu.IMU()

def _ab_get_const(key, default=None):
   return _ab_const.get(key, default)

def _ab_get_rgb(r, g, b):
    return int('0x{:02x}{:02x}{:02x}'.format(r, g, b))

def _ab_get_version():
    return _ab_get_const('VERSION')

_ab_global = {
    'eye_color': ${_eye_color},
    'cheek_color': ${_cheek_color},
    'background_color': ${_background_color},
    'position': 'POS_NORMAL',
    'orientation': 'ORI_NORMAL',
    'auto_orientation': True,
    'gravity_threshold': 0.75,
    'blink_thread_running': False,
    'blink_running': False,
    'blink_interval_function': _ab_get_const('DEFAULT_BLINK_INTERVAL_FUNCTION'),
    'scroll_buffer': []
}


def _ab_get_global(key):
    return _ab_global[key]


def _ab_set_global(key, val):
    _ab_global[key] = val


def _ab_get_led_position(orientation, position):
    return _ab_get_const('ORIENTATIONS')[orientation][position - 1]


def _ab_fill(color):
    with _ab_lock:
        rgb.setColorFrom(_ab_get_const('MIN_LED_POS'), _ab_get_const('MAX_LED_POS'), color)  # type: ignore # noqa: F821


def _ab_set_color(pos, color, orientation):
    with _ab_lock:
        rgb.setColor(_ab_get_led_position(orientation, pos), color)  # type: ignore # noqa: F821


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
    _ab_set_auto_orientation(False)


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


def _ab_blink_task():
    while _ab_get_global('blink_thread_running'):
        if _ab_get_global('blink_running'):
            _func = _ab_get_function_name(_ab_get_global('blink_interval_function'))
            _intervals = globals()[_func]()
            for _ in range(_intervals['LOOP']):
                time.sleep_ms(_intervals['OPEN'])
                _ab_close_eyes()
                time.sleep_ms(_intervals['CLOSE'])
                _ab_open_eyes()
            time.sleep_ms(_intervals['INTERVAL'])
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


def _ab_is_blinking():
    return _ab_get_global('blink_running')

def _ab_set_gravity_threshold(threshold):
    _ab_set_global('gravity_threshold', threshold)

def _ab_get_gravity_threshold():
    return _ab_get_global('gravity_threshold')

def _ab_detect_orientation():
    ax, ay, az = imu0.acceleration
    threshold = _ab_get_gravity_threshold()
    if ay >= threshold:
        return 'ORI_NORMAL'
    elif ax >= threshold:
        return 'ORI_RIGHT'
    elif ax <= -threshold:
        return 'ORI_LEFT'
    elif ay <= -threshold:
        return 'ORI_UPSIDE_DOWN'
    else:
        return _ab_get_global('orientation')

def _ab_is_auto_orientation():
    return _ab_get_global('auto_orientation')

def _ab_set_auto_orientation(auto_orientation):
    _ab_set_global('auto_orientation', auto_orientation)

def _ab_update_orientation():
    if _ab_is_auto_orientation():
        o = _ab_detect_orientation()
        if o != _ab_get_global('orientation'):
            _ab_set_global('orientation', o)
            return True
    return False

def _ab_update():
    return _ab_update_orientation()

def _ab_get_char_positions(c):
    for t in _ab_const['CHAR_TYPES']:
        if c in t:
            return t[c]
    else:
        return []

def _ab_get_scroll_buffer():
    return _ab_get_global('scroll_buffer')

def _ab_update_scroll_buffer(pos):
    _ab_get_scroll_buffer().append(pos)

def _ab_purge_scroll_buffer():
    w = _ab_get_const('LED_WIDTH')
    _ab_set_global('scroll_buffer',
        [p - 1 for p in _ab_get_global('scroll_buffer') if (p - 1) % w != 0])

def _ab_display_scroll_buffer(color, interval):
    _ab_update_orientation()
    for pos in _ab_get_scroll_buffer():
        _ab_set_color(pos, color, _ab_get_orientation())
    time.sleep_ms(interval)
    for pos in _ab_get_scroll_buffer():
        _ab_set_color(pos, _ab_get_background_color(), _ab_get_orientation())
    _ab_purge_scroll_buffer()

def _ab_set_char(c, color, orientation):
    for t in _ab_const['CHAR_TYPES']:
        if c in t:
            for pos in t[c]:
                _ab_set_color(pos, color, orientation)
            break

def _ab_scroll_text(text, color, interval):
    w = _ab_get_const('LED_WIDTH')
    for c in text:
        for x in range(1, w + 1):
            if c == ' ':
                _ab_display_scroll_buffer(color, interval)
            for p in _ab_get_char_positions(c):
                if p % w == x:
                    _ab_update_scroll_buffer(w + w * ((p - 1) // w))
            _ab_display_scroll_buffer(color, interval)
    for x in range(1, w + 1):
        _ab_display_scroll_buffer(color, interval)


def _ab_set_digit(digit, color, orientation):
    if digit < 0 or digit > 9:
        return
    for pos in _ab_get_const('DIGITS')[digit]:
        _ab_set_color(pos, color, orientation)

def _ab_scroll_digits(digits, color, interval):
    _ab_scroll_text(str(digits), color, interval)

_ab_update_orientation()