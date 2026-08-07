"""Analiz pipeline'ının aşamaları: separate → pitch → segment → range → confidence.

Her modül ağır bağımlılıklarını (torch/onnx/demucs/...) FONKSİYON İÇİNDE import
eder; böylece bu paket, ağır modeller kurulmadan da import edilebilir (Faz 0).
Aşama gövdeleri Faz 1'de doldurulacaktır — şu an arayüzleri ve sözleşmeleri
tanımlıyorlar.
"""
