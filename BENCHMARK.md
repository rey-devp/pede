# Data Ingestion & Vector Retrieval

### A. Strategi Pemotongan Teks (Chunking)
Ini akan sangat memengaruhi apa yang direpresentasikan oleh vektor.

Ukuran (Size): 128, 256, 512, 1024 token.

Tumpang Tindih (Overlap): 0%, 10%, 25%.

Metode: Pemotongan statis (jumlah karakter fix) vs Pemotongan sintaksis (berhenti di titik/akhir paragraf) vs Semantic Chunking (berhenti saat topik berubah).

### B. Representasi Vektor (Embedding Model)
Model embedding menentukan kualitas pemahaman semantik dari database.

Dimensi Vektor: Membandingkan model dimensi kecil (misal: 384 dimensi pada MiniLM) versus dimensi besar (misal: 1536 dimensi pada OpenAI atau 1024 pada BGE-M3).

Tipe Model: Model dense standar vs model multi-bahasa (jika dokumen Anda berbahasa Indonesia).

### C. Variasi Tipe Query (Query Diversity)
Untuk mengevaluasi ketangguhan sistem pencarian secara komprehensif, pengujian (metrik *Hit Rate*) harus menggunakan variasi kueri berikut:

1. **Factoid/Simple Query:** Pertanyaan langsung (Misal: "Berapa dimensi dari model embedding BGE-M3?").
2. **Reasoning/Complex Query:** Pertanyaan yang membutuhkan sintesis konsep (Misal: "Mengapa IVF-PQ lebih hemat memori dibandingkan HNSW?").
3. **Paraphrased/Semantic Query:** Pertanyaan yang sengaja TIDAK menggunakan istilah yang ada di dalam teks, tetapi maknanya sama. Ini adalah ujian sesungguhnya bagi sebuah *Vector Database*.
4. **Conversational/Noisy Query:** Pertanyaan dengan gaya bahasa kasual, tidak baku, atau mengandung sedikit *typo*, menyerupai ketikan pengguna asli di dunia nyata.

## Hasil Benchmarking

| Ukuran Chunk | Overlap | Metode Chunking | Model Embedding | Dukungan Bahasa | Tipe Query Uji | Top-K | Filter Metadata | Hit Rate | Latensi | Ukuran Index DB | Catatan |
|:---:|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Factoid/Simple | 10 | Tidak | 100% | 162.0 ms | 0.15 MB | *Chunk 100* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Factoid/Simple | 10 | Ya (DOI) | 100% | 196.1 ms | 0.15 MB | *Chunk 100, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Reasoning/Complex | 10 | Tidak | 100% | 240.9 ms | 0.15 MB | *Chunk 100* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Reasoning/Complex | 10 | Ya (DOI) | 100% | 231.8 ms | 0.15 MB | *Chunk 100, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Semantic/Paraphrased | 10 | Tidak | 100% | 269.1 ms | 0.15 MB | *Chunk 100* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Semantic/Paraphrased | 10 | Ya (DOI) | 100% | 211.1 ms | 0.15 MB | *Chunk 100, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Conversational/Noisy | 10 | Tidak | 100% | 227.3 ms | 0.15 MB | *Chunk 100* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Conversational/Noisy | 10 | Ya (DOI) | 100% | 200.6 ms | 0.15 MB | *Chunk 100, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Factoid/Simple | 10 | Tidak | 100% | 217.7 ms | 0.15 MB | *Chunk 100, ID* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Factoid/Simple | 10 | Ya (DOI) | 100% | 239.2 ms | 0.15 MB | *Chunk 100, ID, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Reasoning/Complex | 10 | Tidak | 100% | 297.6 ms | 0.15 MB | *Chunk 100, ID* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Reasoning/Complex | 10 | Ya (DOI) | 100% | 238.4 ms | 0.15 MB | *Chunk 100, ID, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Semantic/Paraphrased | 10 | Tidak | 100% | 259.5 ms | 0.15 MB | *Chunk 100, ID* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Semantic/Paraphrased | 10 | Ya (DOI) | 100% | 268.6 ms | 0.15 MB | *Chunk 100, ID, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Conversational/Noisy | 10 | Tidak | 100% | 275.4 ms | 0.15 MB | *Chunk 100, ID* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Conversational/Noisy | 10 | Ya (DOI) | 100% | 226.8 ms | 0.15 MB | *Chunk 100, ID, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Factoid/Simple | 10 | Tidak | 100% | 218.1 ms | 0.15 MB | *Chunk 100, ZH* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Factoid/Simple | 10 | Ya (DOI) | 100% | 189.4 ms | 0.15 MB | *Chunk 100, ZH, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Reasoning/Complex | 10 | Tidak | 100% | 271.7 ms | 0.15 MB | *Chunk 100, ZH* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Reasoning/Complex | 10 | Ya (DOI) | 100% | 246.1 ms | 0.15 MB | *Chunk 100, ZH, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Semantic/Paraphrased | 10 | Tidak | 100% | 241.1 ms | 0.15 MB | *Chunk 100, ZH* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Semantic/Paraphrased | 10 | Ya (DOI) | 100% | 217.5 ms | 0.15 MB | *Chunk 100, ZH, Filtered* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Conversational/Noisy | 10 | Tidak | 100% | 250.4 ms | 0.15 MB | *Chunk 100, ZH* |
| 100 | 20 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Conversational/Noisy | 10 | Ya (DOI) | 100% | 193.8 ms | 0.15 MB | *Chunk 100, ZH, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Factoid/Simple | 5 | Tidak | 100% | 132.2 ms | 1.34 MB | *Chunk 500* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Factoid/Simple | 5 | Ya (DOI) | 100% | 427.1 ms | 1.34 MB | *Chunk 500, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Reasoning/Complex | 5 | Tidak | 100% | 228.8 ms | 1.34 MB | *Chunk 500* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Reasoning/Complex | 5 | Ya (DOI) | 100% | 222.4 ms | 1.34 MB | *Chunk 500, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Semantic/Paraphrased | 5 | Tidak | 100% | 210.6 ms | 1.34 MB | *Chunk 500* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Semantic/Paraphrased | 5 | Ya (DOI) | 100% | 310.9 ms | 1.34 MB | *Chunk 500, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Conversational/Noisy | 5 | Tidak | 100% | 219.0 ms | 1.34 MB | *Chunk 500* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Conversational/Noisy | 5 | Ya (DOI) | 100% | 225.4 ms | 1.34 MB | *Chunk 500, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Factoid/Simple | 5 | Tidak | 100% | 219.6 ms | 1.34 MB | *Chunk 500, ID* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Factoid/Simple | 5 | Ya (DOI) | 100% | 223.0 ms | 1.34 MB | *Chunk 500, ID, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Reasoning/Complex | 5 | Tidak | 100% | 299.2 ms | 1.34 MB | *Chunk 500, ID* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Reasoning/Complex | 5 | Ya (DOI) | 100% | 264.7 ms | 1.34 MB | *Chunk 500, ID, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Semantic/Paraphrased | 5 | Tidak | 100% | 249.7 ms | 1.34 MB | *Chunk 500, ID* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Semantic/Paraphrased | 5 | Ya (DOI) | 100% | 263.1 ms | 1.34 MB | *Chunk 500, ID, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Conversational/Noisy | 5 | Tidak | 100% | 258.6 ms | 1.34 MB | *Chunk 500, ID* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Conversational/Noisy | 5 | Ya (DOI) | 100% | 264.5 ms | 1.34 MB | *Chunk 500, ID, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Factoid/Simple | 5 | Tidak | 100% | 202.6 ms | 1.34 MB | *Chunk 500, ZH* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Factoid/Simple | 5 | Ya (DOI) | 100% | 219.8 ms | 1.34 MB | *Chunk 500, ZH, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Reasoning/Complex | 5 | Tidak | 100% | 283.8 ms | 1.34 MB | *Chunk 500, ZH* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Reasoning/Complex | 5 | Ya (DOI) | 100% | 288.6 ms | 1.34 MB | *Chunk 500, ZH, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Semantic/Paraphrased | 5 | Tidak | 100% | 248.1 ms | 1.34 MB | *Chunk 500, ZH* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Semantic/Paraphrased | 5 | Ya (DOI) | 100% | 250.1 ms | 1.34 MB | *Chunk 500, ZH, Filtered* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Conversational/Noisy | 5 | Tidak | 100% | 217.1 ms | 1.34 MB | *Chunk 500, ZH* |
| 500 | 100 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Conversational/Noisy | 5 | Ya (DOI) | 100% | 209.6 ms | 1.34 MB | *Chunk 500, ZH, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Factoid/Simple | 3 | Tidak | 100% | 140.2 ms | 0.73 MB | *Chunk 1000* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Factoid/Simple | 3 | Ya (DOI) | 100% | 279.9 ms | 0.73 MB | *Chunk 1000, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Reasoning/Complex | 3 | Tidak | 100% | 221.2 ms | 0.73 MB | *Chunk 1000* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Reasoning/Complex | 3 | Ya (DOI) | 100% | 226.0 ms | 0.73 MB | *Chunk 1000, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Semantic/Paraphrased | 3 | Tidak | 100% | 201.8 ms | 0.73 MB | *Chunk 1000* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Semantic/Paraphrased | 3 | Ya (DOI) | 100% | 217.5 ms | 0.73 MB | *Chunk 1000, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Conversational/Noisy | 3 | Tidak | 100% | 214.5 ms | 0.73 MB | *Chunk 1000* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | English-focused | Conversational/Noisy | 3 | Ya (DOI) | 100% | 223.0 ms | 0.73 MB | *Chunk 1000, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Factoid/Simple | 3 | Tidak | 100% | 216.7 ms | 0.73 MB | *Chunk 1000, ID* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Factoid/Simple | 3 | Ya (DOI) | 100% | 220.1 ms | 0.73 MB | *Chunk 1000, ID, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Reasoning/Complex | 3 | Tidak | 100% | 343.3 ms | 0.73 MB | *Chunk 1000, ID* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Reasoning/Complex | 3 | Ya (DOI) | 100% | 274.5 ms | 0.73 MB | *Chunk 1000, ID, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Semantic/Paraphrased | 3 | Tidak | 100% | 262.8 ms | 0.73 MB | *Chunk 1000, ID* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Semantic/Paraphrased | 3 | Ya (DOI) | 100% | 258.5 ms | 0.73 MB | *Chunk 1000, ID, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Conversational/Noisy | 3 | Tidak | 100% | 255.9 ms | 0.73 MB | *Chunk 1000, ID* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ID) | Conversational/Noisy | 3 | Ya (DOI) | 100% | 258.6 ms | 0.73 MB | *Chunk 1000, ID, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Factoid/Simple | 3 | Tidak | 100% | 225.3 ms | 0.73 MB | *Chunk 1000, ZH* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Factoid/Simple | 3 | Ya (DOI) | 100% | 200.6 ms | 0.73 MB | *Chunk 1000, ZH, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Reasoning/Complex | 3 | Tidak | 100% | 272.9 ms | 0.73 MB | *Chunk 1000, ZH* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Reasoning/Complex | 3 | Ya (DOI) | 100% | 272.8 ms | 0.73 MB | *Chunk 1000, ZH, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Semantic/Paraphrased | 3 | Tidak | 100% | 229.6 ms | 0.73 MB | *Chunk 1000, ZH* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Semantic/Paraphrased | 3 | Ya (DOI) | 100% | 220.0 ms | 0.73 MB | *Chunk 1000, ZH, Filtered* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Conversational/Noisy | 3 | Tidak | 100% | 220.6 ms | 0.73 MB | *Chunk 1000, ZH* |
| 1000 | 200 | Hybrid | Snowflake/snowflake-arctic-embed-m | Cross-lingual (ZH) | Conversational/Noisy | 3 | Ya (DOI) | 100% | 216.2 ms | 0.73 MB | *Chunk 1000, ZH, Filtered* |

## Panduan Pengisian Benchmarking

Evaluasi Sistem *Retrieval* (Pengambilan Data) adalah nyawa dari arsitektur RAG. Berikut adalah penjelasan ringkas mengapa kolom-kolom metrik di atas sangat penting untuk dipantau dalam fase eksperimen Anda:

### 1. `Top-K (Limit)`
- **Definisi:** Jumlah *chunk* maksimal yang dikembalikan oleh Qdrant ke Gemini.
- **Insight:** Terkadang, menyetel *Top-K* ke angka 10 dengan ukuran *chunk* yang lebih kecil (misal 500 karakter) justru memberikan konteks yang jauh lebih beragam (berasal dari berbagai halaman) dibandingkan mengambil *Top-K* 3 dengan *chunk* raksasa.

### 2. `Hit Rate (Recall@K)`
- **Definisi:** Persentase keberhasilan sistem menemukan "*Chunk* yang mengandung jawaban yang benar" pada pencarian Top-K.
- **Insight:** Ini adalah metrik paling krusial. Anda bisa membuat 10 pasang pertanyaan-jawaban tes. Jika dari 10 pertanyaan tersebut Qdrant berhasil menemukan paragraf yang tepat sebanyak 8 kali di peringkat atas, maka *Hit Rate (Recall)* Anda adalah 80%. Semakin tinggi nilainya, semakin kecil risiko LLM berhalusinasi.

### 3. `Filter Metadata`
- **Definisi:** Apakah pencarian menggunakan *pre-filtering* (seperti membatasi pencarian hanya pada DOI atau *Section Header* tertentu)?
- **Insight:** Filter DOI bisa meningkatkan *Hit Rate* menjadi nyaris 100% secara instan karena sistem secara eksplisit "membuang" gangguan teks (*noise*) dari jurnal lain yang tidak relevan.

### 4. `Rata-rata Latensi (ms)`
- **Definisi:** Waktu komputasi komprehensif dari saat kueri dikirim hingga Qdrant mengembalikan hasilnya.
- **Insight:** Sangat krusial untuk lingkungan *Production*. Jika Anda beralih menggunakan model *embedding* raksasa, latensi pencarian bisa melambung tinggi. Harus diperhitungkan jika aplikasi akan diakses ratusan pengguna serentak.

### 5. `Ukuran Index DB (MB)`
- **Definisi:** Ukuran total folder *database* lokal (contoh: `qdrant_db/`) untuk jumlah kumpulan jurnal uji tertentu.
- **Insight:** Berhubungan langsung dengan konsumsi *Storage* dan *RAM/VRAM* di *Cloud*. Apakah mengorbankan akurasi sebesar 2% sepadan dengan penghematan penyimpanan sebesar 50%? Jawabannya dapat dievaluasi di sini.

### 6. `Dukungan Bahasa (Language Support)`
- **Definisi:** Kemampuan model untuk memetakan bahasa yang berbeda ke dalam ruang semantik yang berdekatan (*Cross-Lingual Information Retrieval*).
- **Insight:** Sangat krusial jika *database* Anda berisi jurnal Bahasa Inggris, tetapi *user* memasukkan pencarian (*query*) dalam Bahasa Indonesia. Model *Multi-bahasa* seperti BGE-M3 dapat mempertemukan *query* Bahasa Indonesia dengan teks jurnal Bahasa Inggris secara cerdas, sedangkan model *Hanya Inggris* (seperti MiniLM) akan gagal total dalam skenario lintas-bahasa ini.
