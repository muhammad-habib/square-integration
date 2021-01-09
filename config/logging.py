import sys


class Logging:
    CONF = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s - (%(name)s)[%(levelname)s]: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'access': {
                'format': '%(asctime)s - (%(name)s)[%(levelname)s][%(host)s]: ' +
                          '%(request)s %(message)s %(status)d %(byte)d',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'simpleFile': {
                'class': 'logging.FileHandler',
                'formatter': 'simple',
                'filename': "logs/simple.log"
            },
            'errorFile': {
                'class': 'logging.FileHandler',
                'formatter': 'simple',
                'filename': "logs/error.log"
            },
            'simpleStream': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': sys.stderr
            },
            'errorStream': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': sys.stderr
            }
        },
        'loggers': {
            'sanic': {
                'level': 'ERROR',
                'handlers': ['errorFile', 'errorStream']
            },
            'network': {
                'level': 'ERROR',
                'handlers': ['errorStream', 'errorFile']
            }
        }
    }
