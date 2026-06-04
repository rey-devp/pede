# AI Workflow Context: PEDE Benchmark Project

**File ini adalah panduan referensi utama untuk agen AI.**
Jika Anda (AI) membaca file ini di masa depan, gunakan informasi di bawah ini untuk memahami secara instan bagaimana proyek ini bekerja, tanpa harus merangkak membaca setiap baris kode dari awal.

## 1. Tentang Proyek "PEDE"
**PEDE (PDF to Model Embedding)** adalah *pipeline ingestion* untuk artikel ilmiah. Ia mengambil PDF, mengekstrak teks ke Markdown (mempertahankan struktur *heading*), merangkum metadata, lalu mengonversinya ke *vector embeddings* untuk disimpan ke **Qdrant Vector Database**.

**Alur Pipeline Default:**
1. **Dedup Check**: Memastikan PDF tidak diproses ganda via DOI hash atau SHA-256.
2. **PDF to Markdown**: Memakai `pymupdf4llm` dengan pembersihan teks pasca-konversi (*page stitching*, *hyphen fix*).
3. **Metadata Extraction**: Menggunakan 3-lapis: (1) Metadata asli PDF, (2) Heuristik Regex, (3) CrossRef API (via DOI).
4. **Smart Chunking**: Menggunakan pendekatan *hybrid 2-tier* (pemotongan berbasis struktur *header markdown*, dengan *fallback* recursive text splitter untuk ukuran >2500 karakter).
5. **Vector Store**: (Standar PEDE) memakai model `BAAI/bge-m3` yang mendukung pencarian semantik ganda (*Dense 1024-d* + *Sparse/Lexical*) dengan *fusion RRF*.

## 2. Benchmark Initiative (Tugas Ekstensi)
Tujuan dari benchmark ini adalah melakukan evaluasi kinerja antara model default (`bge-m3`) dengan model **`Snowflake/snowflake-arctic-embed-m`**.
Eksperimen benchmark ini harus **terisolasi total** dari fungsionalitas asli PEDE.

**Aturan Isolasi Evaluasi:**
- Semua *script* benchmark ada di folder `benchmark/`.
- Dependensi ada pada *virtual environment* lokal di dalam `benchmark/.venv/`.
- Model Snowflake disimpan di `benchmark/qdrant_benchmark_db/`.
- **DILARANG KERAS** memodifikasi file bawaan di dalam `core/` (seperti `core/vector_store.py` atau `core/chunker.py`) dan `api.py`. Penggunaan fungsi asli dilakukan murni via `import`.

## 3. Matriks Evaluasi yang Dihitung
Benchmark harus mengevaluasi metrik-metrik berikut (merujuk pada `BENCHMARK.md`):
1. **Hit Rate (Recall@K)**: Berapa persen dari pertanyaan (*query*) dapat menemukan *chunk* dokumen yang relevan di *Top-K* (misalnya K=5).
2. **Latensi Pencarian**: Durasi (dalam milidetik) sejak kueri dieksekusi model *embedding* hingga *Qdrant* memberikan respons.
3. **Ukuran Database (DB Size)**: Berapa megabyte ukuran indeks lokal di `benchmark/qdrant_benchmark_db/`.

## 4. Model Fokus Benchmark: `Snowflake/snowflake-arctic-embed-m`
- **Tipe**: Dense (Non-hybrid).
- **Dimensi**: 768-d.
- **Support**: *SentenceTransformer* dapat memuat model ini tanpa library khusus. Pada `VectorStore` di PEDE, *fallback* ke `SentenceTransformer` otomatis akan dipanggil jika model tidak memuat unsur nama "m3".
- **Prompt Prefix Query**: `Represent this sentence for searching relevant passages: ` (Jika dibutuhkan oleh library, meski sering otomatis dilampirkan).

---

*(Akhir dari Dokumen Konteks AI)*
