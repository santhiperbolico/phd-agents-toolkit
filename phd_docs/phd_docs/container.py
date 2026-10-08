"""Composition root for PhD documentation pipelines."""

from claudia_docs.config import Settings
from claudia_docs.loaders.chroma import ChromaVectorStoreRepository
from claudia_docs.monitoring.knowledge_gaps import KnowledgeGapRepository
from claudia_docs.pipeline.query import QueryService
from claudia_docs.pipeline.reranking import ScoreReranker
from claudia_docs.pipeline.sync import SyncPipeline
from claudia_docs.transformers.text_splitter import RecursiveTextSplitterTransformer

from phd_docs.extractors import register_phd_providers
from phd_docs.extractors.coordinator import PhdDocsExtractor
from phd_docs.loaders.embeddings import PhdEmbeddingsProvider


def _embeddings(settings: Settings) -> PhdEmbeddingsProvider:
    return PhdEmbeddingsProvider(settings=settings)


def build_sync_pipeline(settings: Settings) -> SyncPipeline:
    """
    Assemble a sync pipeline for PhD documentation sources.

    Parameters
    ----------
    settings : Settings
        Runtime configuration.

    Returns
    -------
    SyncPipeline
        Pipeline ready to run incremental sync.
    """
    register_phd_providers()
    embeddings = _embeddings(settings)
    repository = ChromaVectorStoreRepository(settings=settings, embeddings_provider=embeddings)
    transformer = RecursiveTextSplitterTransformer(settings=settings)
    extractors = (PhdDocsExtractor(settings=settings),)
    return SyncPipeline(
        settings=settings,
        extractors=extractors,
        transformer=transformer,
        repository=repository,
        consolidator=None,
    )


def build_query_service(settings: Settings) -> QueryService:
    """
    Assemble a query service for the PhD documentation index.

    Parameters
    ----------
    settings : Settings
        Runtime configuration.

    Returns
    -------
    QueryService
        Service ready to answer semantic queries.
    """
    register_phd_providers()
    embeddings = _embeddings(settings)
    repository = ChromaVectorStoreRepository(settings=settings, embeddings_provider=embeddings)
    reranker = ScoreReranker(
        tau_days=settings.freshness_tau_days,
        similarity_weight=settings.rerank_similarity_weight,
        freshness_weight=settings.rerank_freshness_weight,
    )
    gap_log = KnowledgeGapRepository(settings.gaps_path)
    return QueryService(
        settings=settings,
        repository=repository,
        reranker=reranker,
        memory_repository=None,
        gap_log=gap_log,
    )
