import os
import sys
import time
import logging
import argparse
from pathlib import Path

# Add parent directory to sys.path to allow importing from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vector_store import VectorStore
from core.pdf_converter import convert_pdf_to_markdown, get_pdf_native_metadata
from core.metadata_extractor import extract_metadata, ArticleMetadata
from core.chunker import chunk_markdown, CHUNK_SIZE, CHUNK_OVERLAP

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("BENCHMARK")

# Setup Directories specific to benchmark
BENCHMARK_DIR = Path(__file__).parent
TEST_DATA_DIR = BENCHMARK_DIR / "test_data"
DB_DIR = BENCHMARK_DIR / "qdrant_benchmark_db"

MODEL_NAME = "Snowflake/snowflake-arctic-embed-m"

def setup_directories():
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Initialized benchmark directories.")

def run_ingestion(vector_store: VectorStore, pdf_paths: list[str]):
    """Ingest a list of PDFs using the PEDE pipeline logic but with the custom vector store."""
    logger.info(f"Starting ingestion of {len(pdf_paths)} PDFs...")
    success_count = 0
    for pdf_path in pdf_paths:
        try:
            logger.info(f"Processing: {os.path.basename(pdf_path)}")
            # 1. Native Meta
            pdf_native_meta = get_pdf_native_metadata(pdf_path)
            
            # 2. Markdown Conversion
            md_text = convert_pdf_to_markdown(pdf_path, write_images=False)
            
            # 3. Meta Extraction
            article_meta = extract_metadata(pdf_path, md_text, pdf_native_meta)
            
            # 4. Chunking
            chunks = chunk_markdown(md_text, article_meta, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            chunks = [c for c in chunks if c.content_type != "references"]
            
            # 5. Embedding & Store
            stored = vector_store.add_chunks(chunks)
            logger.info(f"Stored {stored} chunks for {article_meta.title}.")
            success_count += 1
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")
    
    return success_count

def run_evaluation(vector_store: VectorStore, test_queries: list[dict]):
    """Run search queries and measure Latency and Hit Rate."""
    if not test_queries:
        logger.warning("No test queries defined. Skipping evaluation.")
        return

    logger.info("Starting Evaluation...")
    total_latency = 0
    hits = 0
    
    for item in test_queries:
        query = item["query"]
        expected_doi = item.get("expected_doi")
        
        start_time = time.time()
        # Ensure we run search against our Snowflake model
        results = vector_store.search(query=query, n_results=5)
        latency = (time.time() - start_time) * 1000  # ms
        total_latency += latency
        
        # Check Hit (if the expected DOI is in the top 5 results)
        hit = False
        if expected_doi:
            found_dois = [res["metadata"].get("doi") for res in results]
            if expected_doi in found_dois:
                hit = True
                hits += 1
                
        logger.info(f"Query: '{query}' | Latency: {latency:.1f}ms | Hit: {hit}")
        
    avg_latency = total_latency / len(test_queries)
    hit_rate = (hits / len(test_queries)) * 100
    
    logger.info(f"--- Benchmark Results ---")
    logger.info(f"Model          : {MODEL_NAME}")
    logger.info(f"Total Queries  : {len(test_queries)}")
    logger.info(f"Hit Rate       : {hit_rate:.1f}%")
    logger.info(f"Avg Latency    : {avg_latency:.1f} ms")
    
def get_db_size():
    """Calculate the total size of the Qdrant DB directory in MB."""
    total_size = 0
    if DB_DIR.exists():
        for f in DB_DIR.rglob('*'):
            if f.is_file():
                total_size += f.stat().st_size
    return total_size / (1024 * 1024)

def export_articles_to_md(vector_store: VectorStore):
    """Export all articles in the benchmark DB to a Markdown file."""
    articles = vector_store.list_articles()
    if not articles:
        logger.warning("Belum ada artikel di dalam Database Benchmark.")
        return

    md_path = BENCHMARK_DIR / "daftar_artikel.md"
    with open(md_path, mode='w', encoding='utf-8') as f:
        f.write("# Daftar Artikel Benchmark\n\n")
        f.write("| ID / DOI | Judul Artikel | Authors | Total Chunks |\n")
        f.write("|---|---|---|---|\n")
        
        for a in articles:
            identifier = a['doi'] if a.get('doi') else a['article_id']
            title = a.get('title', 'Untitled')
            # Clean up newlines in title and authors to prevent breaking the MD table
            title = title.replace('\\n', ' ').replace('|', '-')
            authors = a.get('authors', '').replace('\\n', ' ').replace('|', '-')
            chunks = a.get('total_chunks', 0)
            
            f.write(f"| {identifier} | {title} | {authors} | {chunks} |\n")
            
    logger.info(f"Tabel daftar artikel berhasil diekspor ke: {md_path}")

def main():
    parser = argparse.ArgumentParser(description="Run Benchmark with Snowflake Model")
    parser.add_argument("--ingest", action="store_true", help="Ingest all PDFs in test_data folder")
    parser.add_argument("--eval", action="store_true", help="Run evaluation metrics")
    parser.add_argument("--list", action="store_true", help="Ekspor daftar artikel yang ada di DB ke file Markdown (.md)")
    args = parser.parse_args()

    setup_directories()

    # Disable Offline mode for huggingface just in case it's not downloaded
    os.environ.pop("HF_HUB_OFFLINE", None)
    os.environ.pop("TRANSFORMERS_OFFLINE", None)

    logger.info(f"Initializing VectorStore with model: {MODEL_NAME}")
    vector_store = VectorStore(
        qdrant_path=str(DB_DIR),
        embedding_model=MODEL_NAME,
        collection_name="benchmark_snowflake"
    )
    vector_store.ensure_collection()

    if args.ingest:
        pdf_paths = [str(p) for p in TEST_DATA_DIR.glob("**/*.pdf")]
        if not pdf_paths:
            logger.warning(f"No PDFs found in {TEST_DATA_DIR}")
        else:
            run_ingestion(vector_store, pdf_paths)
            
    if args.list or args.eval:
        export_articles_to_md(vector_store)
            
    if args.eval:
        # NOTE: You can populate this list with actual test queries for your specific PDFs.
        test_queries = [
            # Example:
            # {"query": "What is neurosymbolic AI?", "expected_doi": "10.1234/example.1"},
            # {"query": "How does RAG improve LLM?", "expected_doi": "10.5678/example.2"}
        ]
        
        # If no queries are added, we just run a basic dummy query to test latency
        if not test_queries:
            test_queries = [{"query": "Dummy query for latency test", "expected_doi": None}]
            
        run_evaluation(vector_store, test_queries)
        
        db_size = get_db_size()
        logger.info(f"DB Size        : {db_size:.2f} MB")

if __name__ == "__main__":
    main()
