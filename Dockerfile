# Image ERPNext 16 + app donasionline
# Pin 2026-11-22 (frappe 16.56.0, erpnext 16.55.0). Perbarui sengaja, jangan rolling.
ARG BASE=frappe/erpnext@sha256:15a1270f7d8d674de5facd16c3390665a12bd632f5abb846bdd67b61d7461d84
FROM ${BASE}
COPY --chown=frappe:root apps/donasionline /home/frappe/frappe-bench/apps/donasionline
RUN cd /home/frappe/frappe-bench && uv pip install --python env/bin/python -e apps/donasionline
