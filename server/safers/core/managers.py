import logging
from collections import UserList
from typing import Any

from django.core.cache import caches
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models, ProgrammingError
from django.utils.functional import cached_property

logger = logging.getLogger(__name__)


class TransientModelQuerySet(UserList):
    """
    A QuerySet for a TransientModels which aren't stored in the db.
    """
    model = None  # (required for drf-spectacular schema generation)

    def filter(self, **kwargs):
        """
        Allow simple (ie: no lookup expressions) filtering on TransientModels
        """
        matching_models = [
            model for model in self
            if all((getattr(model, k) == v for k, v in kwargs.items()))
        ]
        return self.__class__(matching_models)

    def exclude(self, **kwargs):
        """
        Allow simple (ie: no lookup expressions) exclusions on TransientModels
        """
        matching_models = [
            model for model in self
            if not all((getattr(model, k) == v for k, v in kwargs.items()))
        ]
        return self.__class__(matching_models)

    def get(self, **kwargs):

        matching_models = self.filter(**kwargs)

        n_matching_models = len(matching_models)
        if n_matching_models == 0:
            raise ObjectDoesNotExist()
        elif n_matching_models > 1:
            raise MultipleObjectsReturned()

        return matching_models[0]

    def first(self):
        try:
            return self[0]
        except IndexError:
            pass

    def last(self):
        try:
            return self[-1]
        except IndexError:
            pass


class CachedTransientModelManager(models.Manager):
    """
    A manager for TransientModels which aren't stored in the db.  Also
    allows for queryset_class to be cached.
    """
    queryset_class = TransientModelQuerySet

    cache_key = None
    cache_name = "default"
    cache_sentinel = object()
    cache_timeout = (
        60 * 60
    )  # number of seconds before value expires; None means no expiry, 0 means no caching

    def __init__(self, **kwargs) -> None:
        super().__init__()
        assert self.cache_key is not None
        self._model_class = kwargs.get("model_class")

    @cached_property
    def cache(self):
        return caches[self.cache_name]

    @property
    def model_class(self):
        return self.model or self._model_class

    def get_queryset(self) -> TransientModelQuerySet:
        try:
            queryset_data = self.cache.get(self.cache_key, self.cache_sentinel)
        except ProgrammingError as exception:
            # cache is not yet setup...
            logger.error("unable to access '%s' from cache", self.cache_key)
            queryset_data = []

        if queryset_data is self.cache_sentinel:
            logger.info("caching '%s'", self.cache_key)
            queryset_data = self.get_transient_queryset_data()
            self.cache.set(self.cache_key, queryset_data, self.cache_timeout)

        return self.queryset_class([
            self.model_class(**data) for data in queryset_data
        ])
