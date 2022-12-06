API
===

This part of the documentation lists the full API reference of all classes and functions.

WSGI
----

.. autoclass:: yretain.wsgi.ApplicationLoader
   :members:
   :show-inheritance:

Config
------

.. automodule:: yretain.config

.. autoclass:: yretain.config.application.Application
   :members:
   :show-inheritance:

.. autoclass:: yretain.config.redis.Redis
   :members:
   :show-inheritance:

.. automodule:: yretain.config.gunicorn

CLI
---

.. automodule:: yretain.cli

.. autofunction:: yretain.cli.cli.cli

.. autofunction:: yretain.cli.utils.validate_directory

.. autofunction:: yretain.cli.serve.serve

App
---

.. automodule:: yretain.app

.. autofunction:: yretain.app.asgi.on_startup

.. autofunction:: yretain.app.asgi.on_shutdown

.. autofunction:: yretain.app.asgi.get_application

.. automodule:: yretain.app.router

Controllers
~~~~~~~~~~~

.. automodule:: yretain.app.controllers

.. autofunction:: yretain.app.controllers.ready.readiness_check

Models
~~~~~~

.. automodule:: yretain.app.models

Views
~~~~~

.. automodule:: yretain.app.views

.. autoclass:: yretain.app.views.error.ErrorModel
   :members:
   :show-inheritance:

.. autoclass:: yretain.app.views.error.ErrorResponse
   :members:
   :show-inheritance:

Exceptions
~~~~~~~~~~

.. automodule:: yretain.app.exceptions

.. autoclass:: yretain.app.exceptions.http.HTTPException
   :members:
   :show-inheritance:

.. autofunction:: yretain.app.exceptions.http.http_exception_handler

Utils
~~~~~

.. automodule:: yretain.app.utils

.. autoclass:: yretain.app.utils.aiohttp_client.AiohttpClient
   :members:
   :show-inheritance:

.. autoclass:: yretain.app.utils.redis.RedisClient
   :members:
   :show-inheritance:
