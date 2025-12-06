# web/channel_layers.py
"""
Channel Layer Configuration for Django Channels
This enables communication between REST API and WebSocket consumers
"""

# For production with Redis
CHANNEL_LAYERS_REDIS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# For development/testing with in-memory channel layer
CHANNEL_LAYERS_MEMORY = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# For production with Redis using environment variables
import os

CHANNEL_LAYERS_REDIS_ENV = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(
                os.environ.get('REDIS_HOST', '127.0.0.1'), 
                int(os.environ.get('REDIS_PORT', 6379))
            )],
            "prefix": "meylordrive",
        },
    },
}

# Default configuration (use in-memory for development)
CHANNEL_LAYERS = CHANNEL_LAYERS_MEMORY

# To use Redis instead, change the above line to:
# CHANNEL_LAYERS = CHANNEL_LAYERS_REDIS