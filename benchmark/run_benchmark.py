import os
import sys
import time
import shutil
import logging
import argparse
from pathlib import Path
from dataclasses import dataclass, field

# Add parent directory to sys.path to allow importing from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vector_store import VectorStore
from core.pdf_converter import convert_pdf_to_markdown, get_pdf_native_metadata
from core.metadata_extractor import extract_metadata, ArticleMetadata
from core.chunker import chunk_markdown

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("BENCHMARK")

# ── Directories ──────────────────────────────────────────────────────────────
BENCHMARK_DIR = Path(__file__).parent
TEST_DATA_DIR = BENCHMARK_DIR / "test_data"
DB_DIR        = BENCHMARK_DIR / "qdrant_benchmark_db"
PROJECT_ROOT  = BENCHMARK_DIR.parent

SNOWFLAKE_MODEL = "Snowflake/snowflake-arctic-embed-m"

# ── Experiment Matrix ─────────────────────────────────────────────────────────
# Setiap entry merepresentasikan SATU baris di tabel Hasil Benchmarking.
# Semua eksperimen memakai model Snowflake/snowflake-arctic-embed-m (Dense 768-d).
# Variasi yang diuji: chunk_size, overlap, top_k, filter_metadata, query_type.
# Kolom sesuai BENCHMARK.md: Ukuran Chunk | Overlap | Metode Chunking |
#   Model Embedding | Dukungan Bahasa | Tipe Query Uji | Top-K |
#   Filter Metadata | Hit Rate | Latensi | Ukuran Index DB | Catatan
EXPERIMENT_MATRIX = [
    {
        "chunk_size": 1000, "overlap": 200, "method": "Hybrid",
        "model": SNOWFLAKE_MODEL, "language": "English-focused",
        "query_type": "Semantic/Paraphrased", "top_k": 5,
        "filter_meta": "Tidak",
        "queries": [
            {"query": "semantic retrieval using vector similarity for document search",
             "expected_doi": "10.1016/j.jbusres.2023.114465"},
        ],
        "note": "Baseline: chunk 1000, paraphrased query",
    },
    {
        "chunk_size": 1000, "overlap": 200, "method": "Hybrid",
        "model": SNOWFLAKE_MODEL, "language": "English-focused",
        "query_type": "Factoid/Simple", "top_k": 5,
        "filter_meta": "Tidak",
        "queries": [
            {"query": "What is PLS-SEM robustness check?",
             "expected_doi": "10.1016/j.jbusres.2023.114465"},
        ],
        "note": "Factoid: pertanyaan langsung dan spesifik",
    },
    {
        "chunk_size": 1000, "overlap": 200, "method": "Hybrid",
        "model": SNOWFLAKE_MODEL, "language": "English-focused",
        "query_type": "Reasoning/Complex", "top_k": 5,
        "filter_meta": "Tidak",
        "queries": [
            {"query": "Why do researchers need to validate PLS-SEM models using multiple robustness techniques?",
             "expected_doi": "10.1016/j.jbusres.2023.114465"},
        ],
        "note": "Reasoning: butuh sintesis beberapa bagian",
    },
    {
        "chunk_size": 1000, "overlap": 200, "method": "Hybrid",
        "model": SNOWFLAKE_MODEL, "language": "English-focused",
        "query_type": "Conversational/Noisy", "top_k": 5,
        "filter_meta": "Tidak",
        "queries": [
            {"query": "gimana cara cek kalo hasil SEM kita itu udah bener atau belum?",
             "expected_doi": "10.1016/j.jbusres.2023.114465"},
        ],
        "note": "Bahasa kasual/Indonesia: uji cross-lingual Snowflake",
    },
    {
        "chunk_size": 500, "overlap": 100, "method": "Hybrid",
        "model": SNOWFLAKE_MODEL, "language": "English-focused",
        "query_type": "Semantic/Paraphrased", "top_k": 5,
        "filter_meta": "Tidak",
        "queries": [
            {"query": "cross-validation approach for latent variable model evaluation",
             "expected_doi": "10.1016/j.jbusres.2023.114465"},
        ],
        "note": "Chunk kecil 500 overlap 100, paraphrased query",
    },
    {
        "chunk_size": 500, "overlap": 100, "method": "Hybrid",
        "model": SNOWFLAKE_MODEL, "language": "English-focused",
        "query_type": "Reasoning/Complex", "top_k": 10,
        "filter_meta": "Tidak",
        "queries": [
            {"query": "How does bootstrapping improve validity of partial least squares models?",
             "expected_doi": "10.1016/j.jbusres.2023.114465"},
        ],
        "note": "Chunk 500, Top-K=10: konteks lebih beragam",
    },
    {
        "chunk_size": 500, "overlap": 100, "method": "Hybrid",
        "model": SNOWFLAKE_MODEL, "language": "English-focused",
        "query_type": "Conversational/Noisy", "top_k": 5,
        "filter_meta": "Tidak",
        "queries": [
            {"query": "gimana cara cek kalo hasil SEM kita itu udah bener atau belum?",
             "expected_doi": "10.1016/j.jbusres.2023.114465"},
        ],
        "note": "Chunk kecil, bahasa kasual: uji cross-lingual",
    },
    {
        "chunk_size": 1000, "overlap": 200, "method": "Hybrid",
        "model": SNOWFLAKE_MODEL, "language": "English-focused",
        "query_type": "Semantic/Paraphrased", "top_k": 5,
        "filter_meta": "Ya (DOI)",
        "queries": [
            {"query": "sensitivity analysis in business research methodology",
             "expected_doi": "10.1016/j.jbusres.2023.114465"},
        ],
        "note": "Dengan filter DOI: ekspektasi Hit Rate ~100%",
    },
    {
        "chunk_size": 500, "overlap": 150, "method": "Hybrid",
        "model": SNOWFLAKE_MODEL, "language": "English-focused",
        "query_type": "Factoid/Simple", "top_k": 5,
        "filter_meta": "Tidak",
        "queries": [
            {"query": "recommendations for PLS-SEM applications in business research",
             "expected_doi": "10.1016/j.jbusres.2023.114465"},
        ],
        "note": "Chunk 500 overlap 150, factoid query",
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def setup_directories():
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Initialized benchmark directories.")


def _collection_name(model: str, chunk_size: int, overlap: int) -> str:
    """Generate unique collection name per experiment config."""
    model_short = model.split("/")[-1].replace("-", "_").lower()
    return f"bm_{model_short}_c{chunk_size}_o{overlap}"


def _db_path(model: str, chunk_size: int, overlap: int) -> Path:
    """Separate DB sub-folder per config to avoid data mixing."""
    name = _collection_name(model, chunk_size, overlap)
    return DB_DIR / name


def _get_dir_size_mb(path: Path) -> float:
    total = 0
    if path.exists():
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
    return total / (1024 * 1024)


def _ingest_pdfs(vector_store: VectorStore, pdf_paths: list[str],
                 chunk_size: int, chunk_overlap: int) -> int:
    """Ingest PDFs dengan chunk_size & overlap yang ditentukan oleh eksperimen."""
    logger.info(f"  Ingesting {len(pdf_paths)} PDF(s) [chunk={chunk_size}, overlap={chunk_overlap}]...")
    success = 0
    for pdf_path in pdf_paths:
        try:
            pdf_native_meta = get_pdf_native_metadata(pdf_path)
            md_text         = convert_pdf_to_markdown(pdf_path, write_images=False)
            article_meta    = extract_metadata(pdf_path, md_text, pdf_native_meta)
            chunks          = chunk_markdown(md_text, article_meta,
                                             chunk_size=chunk_size,
                                             chunk_overlap=chunk_overlap)
            chunks          = [c for c in chunks if c.content_type != "references"]
            stored          = vector_store.add_chunks(chunks)
            logger.info(f"  Stored {stored} chunks for: {article_meta.title}")
            success += 1
        except Exception as e:
            logger.error(f"  Failed to process {pdf_path}: {e}")
    return success


def _run_queries(vector_store: VectorStore, queries: list[dict],
                 top_k: int, doi_filter: str | None = None) -> tuple[float, float]:
    """Jalankan daftar query. Return (hit_rate_pct, avg_latency_ms)."""
    hits = 0
    total_latency = 0.0

    for item in queries:
        query        = item["query"]
        expected_doi = item.get("expected_doi")

        t0      = time.time()
        results = vector_store.search(
            query=query,
            n_results=top_k,
            doi_filter=doi_filter,
        )
        latency = (time.time() - t0) * 1000
        total_latency += latency

        hit = False
        if expected_doi:
            found_dois = [r["metadata"].get("doi") for r in results]
            if expected_doi in found_dois:
                hit = True
                hits += 1

        logger.info(f"    Query: '{query[:60]}...' | {latency:.1f}ms | Hit={hit}")

    n = len(queries)
    hit_rate    = (hits / n) * 100 if n else 0.0
    avg_latency = total_latency / n if n else 0.0
    return hit_rate, avg_latency


# ── Per-experiment runner ─────────────────────────────────────────────────────

@dataclass
class ExperimentResult:
    chunk_size:   int
    overlap:      int
    method:       str
    model:        str
    language:     str
    query_type:   str
    top_k:        int
    filter_meta:  str
    hit_rate:     float  = 0.0
    avg_latency:  float  = 0.0
    db_size_mb:   float  = 0.0
    note:         str    = ""
    status:       str    = "OK"


def run_single_experiment(exp: dict, pdf_paths: list[str]) -> ExperimentResult:
    """Jalankan satu eksperimen: ingest (jika belum ada) → evaluasi → return result."""
    model       = exp["model"]
    chunk_size  = exp["chunk_size"]
    overlap     = exp["overlap"]
    top_k       = exp["top_k"]
    queries     = exp["queries"]
    filter_meta = exp["filter_meta"]

    result = ExperimentResult(
        chunk_size  = chunk_size,
        overlap     = overlap,
        method      = exp["method"],
        model       = model,
        language    = exp["language"],
        query_type  = exp["query_type"],
        top_k       = top_k,
        filter_meta = filter_meta,
        note        = exp.get("note", ""),
    )

    col_name = _collection_name(model, chunk_size, overlap)
    db_path  = _db_path(model, chunk_size, overlap)
    db_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"\n{'='*60}")
    logger.info(f"Experiment: {col_name}")
    logger.info(f"  Model={model} | Chunk={chunk_size} | Overlap={overlap} | TopK={top_k}")

    try:
        # Disable offline env so model can download if needed
        os.environ.pop("HF_HUB_OFFLINE", None)
        os.environ.pop("TRANSFORMERS_OFFLINE", None)

        vs = VectorStore(
            qdrant_path      = str(db_path),
            embedding_model  = model,
            collection_name  = col_name,
        )
        vs.ensure_collection()

        # ── Ingest (skip jika sudah ada data) ──
        info = vs.get_collection_info()
        if info["points_count"] == 0:
            if not pdf_paths:
                logger.warning("  No PDFs to ingest. Skipping experiment.")
                result.status = "NO_DATA"
                return result
            _ingest_pdfs(vs, pdf_paths, chunk_size, overlap)
        else:
            logger.info(f"  Collection already has {info['points_count']} points. Skipping ingest.")

        # ── Evaluate ──
        doi_filter = None
        if "doi" in filter_meta.lower():
            # Gunakan DOI pertama dari queries sebagai filter
            doi_filter = queries[0].get("expected_doi")

        hit_rate, avg_latency = _run_queries(vs, queries, top_k, doi_filter)
        result.hit_rate    = hit_rate
        result.avg_latency = avg_latency
        result.db_size_mb  = _get_dir_size_mb(db_path)

        logger.info(f"  → Hit Rate={hit_rate:.1f}% | Latency={avg_latency:.1f}ms | DB={result.db_size_mb:.2f}MB")

    except Exception as e:
        logger.error(f"  Experiment FAILED: {e}")
        result.status = f"ERROR: {e}"

    return result


# ── Export helpers ────────────────────────────────────────────────────────────

def export_articles_to_md(vector_store: VectorStore):
    """Export artikel yang ada di DB ke daftar_artikel.md."""
    articles = vector_store.list_articles()
    if not articles:
        logger.warning("Belum ada artikel di dalam Database Benchmark.")
        return

    md_path = BENCHMARK_DIR / "daftar_artikel.md"
    with open(md_path, mode="w", encoding="utf-8") as f:
        f.write("# Daftar Artikel Benchmark\n\n")
        f.write("| ID / DOI | Judul Artikel | Authors | Total Chunks |\n")
        f.write("|---|---|---|---|\n")
        for a in articles:
            identifier = a["doi"] if a.get("doi") else a["article_id"]
            title      = a.get("title", "Untitled").replace("\n", " ").replace("|", "-")
            authors    = a.get("authors", "").replace("\n", " ").replace("|", "-")
            chunks     = a.get("total_chunks", 0)
            f.write(f"| {identifier} | {title} | {authors} | {chunks} |\n")

    logger.info(f"Tabel daftar artikel diekspor ke: {md_path}")


def export_results_to_benchmark_md(results: list[ExperimentResult]):
    """
    Tulis hasil eksperimen ke tabel 'Hasil Benchmarking' di BENCHMARK.md.
    Hanya baris tabel yang ditimpa; panduan di bawahnya dipertahankan.
    """
    bm_path = PROJECT_ROOT / "BENCHMARK.md"

    # Baca isi lama
    if bm_path.exists():
        with open(bm_path, encoding="utf-8") as f:
            original = f.read()
    else:
        original = ""

    # Bangun baris-baris tabel baru
    header = (
        "| Ukuran Chunk | Overlap | Metode Chunking | Model Embedding "
        "| Dukungan Bahasa | Tipe Query Uji | Top-K "
        "| Filter Metadata | Hit Rate | Latensi | Ukuran Index DB | Catatan |\n"
        "|:---:|:---:|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|\n"
    )

    rows = []
    for r in results:
        if r.status == "OK":
            hit_str  = f"{r.hit_rate:.0f}%"
            lat_str  = f"{r.avg_latency:.1f} ms"
            db_str   = f"{r.db_size_mb:.2f} MB"
        else:
            hit_str  = "-"
            lat_str  = "-"
            db_str   = "-"

        model_short = r.model.split("/")[-1]  # tampilkan hanya nama model saja
        rows.append(
            f"| {r.chunk_size} | {r.overlap} | {r.method} "
            f"| {r.model} "
            f"| {r.language} | {r.query_type} | {r.top_k} "
            f"| {r.filter_meta} | {hit_str} | {lat_str} | {db_str} "
            f"| *{r.note}* |"
        )

    new_table = header + "\n".join(rows) + "\n"

    # Cari bagian "## Hasil Benchmarking" dan ganti tabelnya
    import re
    pattern = re.compile(
        r"(## Hasil Benchmarking\n\n)"         # grup 1 = judul
        r"\|.*?\|\n"                            # header row
        r"\|.*?\|\n"                            # separator row
        r"(?:\|.*?\|\n)*",                     # data rows (0+)
        re.DOTALL,
    )

    if pattern.search(original):
        new_content = pattern.sub(r"\g<1>" + new_table, original)
    else:
        # Tempel di akhir jika bagian tidak ditemukan
        new_content = original.rstrip() + "\n\n## Hasil Benchmarking\n\n" + new_table

    with open(bm_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    logger.info(f"Hasil benchmark diekspor ke: {bm_path}")
    logger.info(f"  Total eksperimen: {len(results)}")
    logger.info(f"  Berhasil       : {sum(1 for r in results if r.status == 'OK')}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Run PEDE Benchmark")
    parser.add_argument("--ingest",     action="store_true",
                        help="Ingest semua PDF di test_data ke DB benchmark (single model)")
    parser.add_argument("--eval",       action="store_true",
                        help="Jalankan evaluasi sederhana (single model, dummy query)")
    parser.add_argument("--list",       action="store_true",
                        help="Ekspor daftar artikel ke daftar_artikel.md")
    parser.add_argument("--run-matrix", action="store_true",
                        help="Jalankan SEMUA eksperimen di EXPERIMENT_MATRIX dan ekspor ke BENCHMARK.md")
    parser.add_argument("--clean",      action="store_true",
                        help="Hapus semua data DB benchmark (mulai bersih)")
    args = parser.parse_args()

    setup_directories()
    os.environ.pop("HF_HUB_OFFLINE", None)
    os.environ.pop("TRANSFORMERS_OFFLINE", None)

    # ── --clean ──────────────────────────────────────────────────────────────
    if args.clean:
        if DB_DIR.exists():
            shutil.rmtree(DB_DIR)
            DB_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("DB benchmark telah dibersihkan.")
        return

    # ── --run-matrix ─────────────────────────────────────────────────────────
    if args.run_matrix:
        pdf_paths = [str(p) for p in TEST_DATA_DIR.glob("**/*.pdf")]
        if not pdf_paths:
            logger.warning(f"Tidak ada PDF di {TEST_DATA_DIR}. Letakkan PDF terlebih dahulu.")

        results: list[ExperimentResult] = []
        for i, exp in enumerate(EXPERIMENT_MATRIX, 1):
            logger.info(f"\n[Eksperimen {i}/{len(EXPERIMENT_MATRIX)}]")
            res = run_single_experiment(exp, pdf_paths)
            results.append(res)

        export_results_to_benchmark_md(results)
        logger.info("\n✅ Benchmark matrix selesai. Cek BENCHMARK.md untuk hasilnya.")
        return

    # ── Mode lama (single-model, backward-compatible) ─────────────────────────
    MODEL_NAME = SNOWFLAKE_MODEL
    logger.info(f"Initializing VectorStore with model: {MODEL_NAME}")
    vs = VectorStore(
        qdrant_path     = str(DB_DIR / "default"),
        embedding_model = MODEL_NAME,
        collection_name = "benchmark_snowflake",
    )
    vs.ensure_collection()

    if args.ingest:
        pdf_paths = [str(p) for p in TEST_DATA_DIR.glob("**/*.pdf")]
        if not pdf_paths:
            logger.warning(f"No PDFs found in {TEST_DATA_DIR}")
        else:
            _ingest_pdfs(vs, pdf_paths,
                         chunk_size=1000, chunk_overlap=200)

    if args.list or args.eval:
        export_articles_to_md(vs)

    if args.eval:
        test_queries = [{"query": "Dummy query for latency test", "expected_doi": None}]
        hit_rate, avg_latency = _run_queries(vs, test_queries, top_k=5)
        db_size = _get_dir_size_mb(DB_DIR / "default")

        logger.info(f"--- Benchmark Results ---")
        logger.info(f"Model          : {MODEL_NAME}")
        logger.info(f"Hit Rate       : {hit_rate:.1f}%")
        logger.info(f"Avg Latency    : {avg_latency:.1f} ms")
        logger.info(f"DB Size        : {db_size:.2f} MB")


if __name__ == "__main__":
    main()
