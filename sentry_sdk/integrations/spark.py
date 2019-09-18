from __future__ import absolute_import

from functools import wraps

from sentry_sdk import configure_scope
from sentry_sdk.integrations import Integration

SCOPE_TAGS = frozenset(("startTime"))

class SparkIntegration(Integration):
    identifier = "spark"

    @staticmethod
    def setup_once():
        # type: () -> None
        patch_spark_context()

def patch_spark_context():
    from pyspark import SparkContext # type: ignore

    spark_context_init = SparkContext._do_init

    def _sentry_patched_spark_context_init(self, *args, **kwargs):
        try:
            return spark_context_init(self, *args, **kwargs)
        finally:
            with configure_scope() as scope:
                scope.set_tag("user", self.sparkUser())
                scope.set_tag("spark_version", self.version)
                scope.set_tag("app_name", self.appName)

                scope.set_extra("start_time", self.startTime)
                scope.set_extra("web_url", self.uiWebUrl)

    SparkContext._do_init = _sentry_patched_spark_context_init
