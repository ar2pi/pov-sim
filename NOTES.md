# Notes

```sh
make up
while true; do ./scripts/airlines-loadgen.sh; done
while true; do ./scripts/flights-loadgen.sh; done
```

- [Get OTLP token](https://grafana.com/orgs/arthurpicerna/stacks/1258769/otlp-info)
- [Alloy receiver live debugging](http://localhost:12345/debug/otelcol.receiver.otlp.default)
- [airlines metrics](https://arthurpicerna.grafana.net/a/grafana-metricsdrilldown-app/drilldown?nativeHistogramMetric=&layout=grid&filters-rule=&filters-prefix=&filters-suffix=&from=now-1h&to=now&timezone=browser&var-otel_resources=&var-filters=service_name%7C%3D%7Cairlines&var-otel_and_metric_filters=&var-deployment_environment=undefined&var-labelsWingman=%28none%29&search_txt=&var-metrics-reducer-sort-by=default&var-ds=grafanacloud-prom&var-other_metric_filters=)
- [flights metrics](https://arthurpicerna.grafana.net/a/grafana-metricsdrilldown-app/drilldown?nativeHistogramMetric=&layout=grid&filters-rule=&filters-prefix=&filters-suffix=&from=now-1h&to=now&timezone=browser&var-otel_resources=&var-filters=service_name%7C%3D%7Cflights&var-otel_and_metric_filters=&var-deployment_environment=undefined&var-labelsWingman=%28none%29&search_txt=&var-metrics-reducer-sort-by=default&var-ds=grafanacloud-prom&var-other_metric_filters=)
- [logs](https://arthurpicerna.grafana.net/a/grafana-lokiexplore-app/explore)
- [traces](https://arthurpicerna.grafana.net/a/grafana-exploretraces-app/explore)

- [airlines profiles local](http://localhost:4040/?query=process_cpu%3Acpu%3Ananoseconds%3Acpu%3Ananoseconds%7Bservice_name%3D%22airlines%22%7D)
- [airlines profiles in Grafana Cloud](https://arthurpicerna.grafana.net/a/grafana-pyroscope-app/explore?searchText=&panelType=time-series&layout=grid&hideNoData=off&explorationType=flame-graph&var-serviceName=airlines&var-profileMetricId=process_cpu%3Acpu%3Ananoseconds%3Acpu%3Ananoseconds&var-spanSelector=undefined&var-dataSource=grafanacloud-profiles&var-filters=&var-filtersBaseline=&var-filtersComparison=&var-groupBy=all&maxNodes=16384)

- @TODO: [Link traces and profiles](https://grafana.com/docs/pyroscope/latest/configure-client/trace-span-profiles/java-span-profiles/)
