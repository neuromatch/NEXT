import os
import time
from datetime import datetime
import yaml
import random
import sys
import base64
import pprint
from decorator import decorator
from line_profiler import LineProfiler

color_ansi = {'yellow': '\x1b[33m',
              'red': '\x1b[31m',
              'blue': '\x1b[34m',
              'green': '\x1b[32m',
              'white': '\x1b[37m',
              'black': '\x1b[30m',
              'purple': '\x1b[35m',
              'reset all': '\x1b[0m'}


@decorator
def profile_each_line(func, *args, **kwargs):
    profiler = LineProfiler()
    profiled_func = profiler(func)
    retval = None
    try:
        retval = profiled_func(*args, **kwargs)
    finally:
        profiler.print_stats()
    return retval


def get_supported_apps(apps_path='apps/'):
    """
    Returns a list of strings correspdoning to the app_id's that are fully operational in the learning library.

    Usage: ::\n
      app_id_list = utils.get_supported_apps()
      print app_id_list
      >>> ['StochasticBanditsPureExploration', 'DuelingBanditsPureExploration', 'StochasticLinearBanditsExploreExploit', 'PoolBasedTripletMDS']
    """
    import os
    return [d for d in next(os.walk(os.path.dirname(apps_path)))[1] if d[0] not in {'.', '_'}]


def get_app(app_id, exp_uid, db, ell):
    """
    Returns an object correspoding to the app_id that contains methods like initExp,getQuery,etc.

    Usage: ::\n
      app = utils.get_app(app_id)
      print app
      >>> <next.apps.StochasticBanditsPureExploration.StochasticBanditsPureExploration.StochasticBanditsPureExploration object at 0x103c9dcd0>
    """
    app_id = str(
        app_id)  # soemtimes input is unicode formatted which causes error
    next_path = 'next.apps.App'
    app_module = __import__(next_path, fromlist=[''])
    app_class = getattr(app_module, 'App')
    return app_class(app_id, exp_uid, db, ell)


def get_app_alg(app_id, alg_id):
    """
    Returns an object correspoding to the alg_id that contains methods like initExp,getQuery,etc.
    Note that each algorithm (with an alg_id) is a child of an app (with an app_id), hence the app_id input

    Usage: ::\n
      alg = utils.get_app_alg(app_id,alg_id)
      print alg
      >>> <next.apps.PoolBasedTripletMDS.RandomSampling.RandomSampling.RandomSampling object at 0x103cb7e10>
    """
    app_id = str(
        app_id)  # soemtimes input is unicode formatted which causes error
    # soemtimes input is unicode formatted which causes error
    alg_id = str(alg_id)
    next_path = 'apps.{}.algs.{}'.format(app_id, alg_id, alg_id)
    alg_module = __import__(next_path, fromlist=[''])
    alg_class = getattr(alg_module, 'MyAlg')
    return alg_class()


def getDocUID(exp_uid, alg_uid=None):
    """
    Each instance of an app (with an (app_id,exp_uid) pair) and an algorithm (with an (app_id,exp_uid,alg_id,alg_uid) tuple)
    gets its own namespace. This method defines that namespace given the exp_uid, or (exp_uid,alg_uid)

    Usage::\n
      print utils.getDocUID(exp_uid)
      >>> 'eee9d58c61d580029113ba593446d23a'

      print utils.getDocUID(exp_uid,alg_uid)
      >>> 'eee9d58c61d580029113ba593446d23a-f081d374abac6c009f5a74877f8b9f3c'
    """
    if alg_uid == None:
        return exp_uid
    else:
        return exp_uid + "-" + alg_uid


def getNewUID():
    """
    Returns length 32 string of random hex that is generated from machine state - good enough for cryptography
    Probability of collision is 1 in 340282366920938463463374607431768211456

    Used for unique identifiers all over the system
    """
    uid = os.urandom(16).hex()
    return uid


def datetimeNow(format='datetime'):
    """
    Returns the current datetime in the format used throughout the system.
    For consistency, one should ALWAYS call this method, do not make your own call to datetime.

    Usage: ::\n
      utils.datetimeNow()
      >>> datetime.datetime(2015, 2, 17, 11, 5, 56, 27822)
    """
    date = datetime.now()
    if format == 'string':
        return datetime2str(date)
    else:
        return date


def datetime2str(obj_datetime):
    """
    Converts a datetime string into a datetime object in the system.
    For consistency, one should never use their own method of converting to string, always use this method.

    Usage: ::\n
      date = utils.datetimeNow()
      date_str = utils.datetime2str(date)
      print date_str
      >>> '2015-02-17 11:11:07.489925'
    """
    return str(obj_datetime)


def str2datetime(str_time):
    """
    Converts a datetime object into the string format used in the system.
    For consistency, one should never use their own method of converting to string, always use this method.

    Usage: ::\n
      date = utils.datetimeNow()
      date_str = utils.datetime2str(date)
      utils.str2datetime(date_str)
    """
    try:
        return datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S.%f')
    except:
        return datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')


def _get_filename(target):
    return target['alt_description']


def filenames_to_ids(filenames, targets):
    _to_ids = filenames_to_ids

    if isinstance(filenames[0], list):
        return [_to_ids(files, targets) for files in filenames]
    if isinstance(filenames[0], tuple):
        return tuple([_to_ids(files, targets) for files in filenames])
    if isinstance(filenames[0], dict):
        return {k: _to_ids(v, targets) for k, v in list(filenames.items())}

    ids = {_get_filename(target): target['target_id'] for target in targets}

    not_in_targets = set(filenames) - set(ids)
    if len(not_in_targets) > 0:
        msg = 'Filenames specified in init.yaml "{}" in the not found the list of targets'
        raise ValueError(msg.format(not_in_targets))

    return [ids[filename] for filename in filenames]


def debug_print(*args, **kwargs):
    color = kwargs.get('color', 'yellow')
    for a in args:
        if type(a) in {str}:
            lines = a.split('\n')
            for line in lines:
                pprint_arg = pprint.pformat(line).split('\n')
                for line2 in pprint_arg:
                    print('{}{}{}'.format(color_ansi[color],
                                          line2,
                                          color_ansi['reset all']))
        else:
            pprint_a = pprint.pformat(a).split('\n')
            for line in pprint_a:
                print('{}{}{}'.format(color_ansi[color],
                                      line,
                                      color_ansi['reset all']))
    print('')


def random_string(length=20):
    letters = list('qwertyuiopasdfghkjlzxcvbnm')
    s = [random.choice(letters) for _ in range(length)]
    s = ''.join(s)
    return s


def timeit(f):
    """
    Utility used to time the duration of code execution. This script can be composed with any other script.

    Usage::\n
      def f(n):
        return n**n

      def g(n):
        return n,n**n

      answer0,dt = timeit(f)(3)
      answer1,answer2,dt = timeit(g)(3)
    """
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        # TODO: delete these three lines. Use
        # `grep -Hnri ,.*,.* = .*utils.timeit` to find all locations this function
        # is are used (typically in `a, b, c, dt = utils.timeit(...)(...)`. We want
        # `a, dt = utils.timeit(...)(...)`.
        return result, (te-ts)
    return timed
