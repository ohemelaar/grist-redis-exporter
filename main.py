from prometheus_client import start_http_server
from prometheus_client.core import (
    GaugeMetricFamily,
    CounterMetricFamily,
    REGISTRY,
    InfoMetricFamily,
)
from prometheus_client.registry import Collector
import redis
import json
import os

r = redis.Redis(
    host="localhost",
    port=6379,
    password=os.environ.get("REDIS_PASSWORD"),
    decode_responses=True,
)


class CustomCollector(Collector):
    def collect(self):
        doc_metrics = GaugeMetricFamily(
            "doc_assignments",
            "Documents assigned to doc workers",
            labels=["doc_wk_ip", "doc_id"],
        )

        keys = r.keys("doc-*")
        for key in keys:
            if key.endswith("-checksum"):
                continue
            data = r.hgetall(key)
            doc_wk_ip = json.loads(data["docWorker"])["id"].replace("-", ".")
            doc_id = key.removeprefix("doc-")
            doc_metrics.add_metric([doc_wk_ip, doc_id], 1)

        yield doc_metrics


REGISTRY.register(CustomCollector())

_, t = start_http_server(8888)
print("Started server")
t.join()
