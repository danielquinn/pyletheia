import logging


class LoggingMixin:
    """
    Handy logging mixin that allows me to use a logger without having to
    declare it globally.
    """

    _logger = None

    @property
    def logger(self):

        if self._logger:
            return self._logger

        self._logger = logging.getLogger(
            ".".join(["pyletheia", __name__, self.__class__.__name__]))

        return self.logger
