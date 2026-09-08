# Data provenance

[LITERATURE] CSV públicos del repositorio de Canchola, preservados por commit y SHA256. El subconjunto descargado contiene NP Entry ID, Study ID, Year, material y perfiles humanos. El artículo describe una base más amplia; no se presenta el subconjunto como los 817 registros completos.

[LITERATURE / PLAN] REF01: reproducción del baseline RF desde parámetros y outputs publicados, sin reoptimizar. REF04: datos interlaboratorio como contexto externo de detección/batch; no se afirma validación experimental de afinidad. Estudios retenidos no equivalen a un nuevo laboratorio prospectivo.

Cada evidencia original se preserva en evidence/ o data/raw/. No se derivaron parámetros numéricos de conocimiento implícito. No hay resultados de simulación. Licencias de cada fuente deben conservarse separadas: acceso público no significa licencia de redistribución.

## Inspección realizada

[COMPUTED] `audit/data_audit.json` registra 597 muestras humanas, 52 Study ID y 581 filas en el archivo preparado para predicción publicado. El artículo describe 817 entradas de varias especies; la descarga no se presenta como la base completa. Los 597 IDs de metadata y perfiles coinciden mediante unión explícita por NP Entry ID. Cada Study ID tiene un título y un año consistentes.

[COMPUTED] No hay NP Entry ID duplicados. Hay 94 filas que participan en coincidencias exactas de perfil proteómico completo y ocho features; todas están dentro del mismo estudio. Se preservan como observaciones potencialmente repetidas, no se eliminan arbitrariamente. GROUP/LOSO/material/temporal impiden el cruce de esos grupos. RANDOM mide deliberadamente la partición por muestra.

[COMPUTED] A17 y A36 contienen DOI distintos para un único título de estudio. `audit/doi_anomalies.csv` conserva cada celda; los primeros DOI se verificaron en Crossref y concuerdan con los títulos (`audit/study_doi_checks.json`). El agrupamiento usa Study ID/título, nunca cada cadena DOI defectuosa como un estudio nuevo. No se reparó el original.

[COMPUTED] Protein IDs: 2497 accesiones únicas; 598 tienen espacios periféricos. Se conserva una tabla original→normalizada y la comprobación de sintaxis tras retirar espacios. Solo se verificaron externamente las cuatro accesiones del panel, todas humanas: APOE P02649, APOB P04114, C3 P01024, CLUS P10909. No se afirma verificación individual de las restantes.

[COMPUTED] Se conservaron como desconocidos dos valores de APOB y cuatro de C3 no numéricos en metadata, aunque la matriz preparada de frecuencias los codifica como cero. Detalle de corrección y primer resultado invalidado: `audit/SOURCE_CONSISTENCY_CORRECTION.md`. La tabla de modelado usa ambos orígenes para excluir desconocidos; no confunde no detección con ausencia física de afinidad.

[COMPUTED] El archivo preparado publicado etiqueta C3 como Present en 290/581 filas, mientras el perfil cuantitativo incluye C3 positivo en 563/597. No se resolvió la semántica exacta de esa etiqueta preparada; se usa exclusivamente para reproducir el software publicado. El nuevo benchmark emplea detección cuantitativa documentada, no esos rótulos. No se afirma que los dos experimentos sean la misma tarea.

[COMPUTED] `audit/schema.json` conserva nombres, dimensiones y columnas; `audit/missingness.csv` conserva conteos por columna de tokens ausentes. La última fecha disponible del subconjunto es 2023 y solo comprende dos filas: reserva temporal sin evaluación, insuficiente para conclusión temporal robusta. Desarrollo: 595 filas de 51 estudios, con exclusión específica de etiquetas desconocidas.

## Licencia y uso

[LITERATURE] El XML del artículo PC-DB declara CC-BY-NC-ND 4.0. Los dos árboles GitHub inspeccionados no contienen LICENSE y sus metadatos API dan license=null. El artículo y README señalan disponibilidad de datos/código, pero no especifican una licencia independiente de redistribución de esos archivos. Se conservan copias locales para análisis con atribución; no se publicaron, relicenciaron ni enviaron a terceros. No se declara licencia MIT/CC0 por suponerla.

[COMPUTED] Proveniencia de descarga por commit, URL, timestamp y SHA256 en `evidence/data_download_manifest.json`; el notebook añadido después también queda cubierto por `splits/pretraining_freeze.json`. Los originales permanecen inalterados. Outputs actuales: `runs/first_split_comparison/`; outputs anteriores corregidos: `runs/first_split_comparison_superseded_v1/`.

## Confirmatory provenance — 2026-09-06

Original inputs were preserved. LABEL_PROVENANCE.md documents the official supplement, code/history evidence and unresolved prepared labels. Supplemental downloads and their hashes are stored in evidence/label_audit. Confirmatory input freeze, split IDs, predictions, computed tables and current artifact hashes are in runs/confirmatory. No synthetic labels or observations were generated; training bootstrap resamples original study records. Figures derive solely from the recorded CSVs.

## Final robustness provenance — 2026-09-06

FINAL ROBUSTNESS preserved original raw inputs and labels. Entire log-unit studies excluded in a separate derived cohort before refits. Official PROTCROWN XLSX/HTML/metadata/SI downloaded read-only; URLs, UTC times, hashes and access failures in evidence/protcrown. No RPA sample-position join or external training. Source-level overlap in runs/final_robustness/protcrown_source_deduplication.csv. See EXTERNAL_VALIDATION_FEASIBILITY.md for license scope and unresolved mapping.
