"""PubMed API Integration Module"""
import aiohttp
import asyncio
import time
from typing import List, Dict, Optional
from .config import settings
import logging

logger = logging.getLogger(__name__)

class PubMedAPI:
    """Interface for PubMed REST API"""
    
    # Type 2 Diabetes + Clinical Trials Query
    BASE_QUERY = '''(
  ("type 2 diabetes"[Title/Abstract] OR
   "type II diabetes"[Title/Abstract] OR
   "T2DM"[Title/Abstract] OR
   "T2D"[Title/Abstract] OR
   "non-insulin-dependent diabetes"[Title/Abstract] OR
   "NIDDM"[Title/Abstract] OR
   "adult-onset diabetes"[Title/Abstract] OR
   "diabetes mellitus, type 2"[MeSH Terms])
 )
 AND
 (
  "adaptive clinical trial"[Publication Type] OR
  "clinical trial"[Publication Type] OR
  "clinical trial phase ii"[Publication Type] OR
  "clinical trial phase iii"[Publication Type] OR
  "clinical trial phase iv"[Publication Type] OR
  "randomized controlled trial"[Publication Type] OR
  "controlled clinical trial"[Publication Type]
 )'''
    
    def __init__(self):
        self.base_url = settings.PUBMED_BASE_URL
        self.db = settings.PUBMED_DB
        self.email = settings.PUBMED_EMAIL
        self.api_key = settings.PUBMED_API_KEY
        self.batch_size = settings.PUBMED_BATCH_SIZE
        self.max_results = settings.PUBMED_MAX_RESULTS
    
    async def search(self, query: str = None, max_results: int = None) -> Dict:
        """Search PubMed for relevant studies"""
        if query is None:
            query = self.BASE_QUERY
        if max_results is None:
            max_results = self.max_results
        
        try:
            async with aiohttp.ClientSession() as session:
                # Phase 1: Search (returns UIDs)
                search_url = f"{self.base_url}/esearch.fcgi"
                search_params = {
                    'db': self.db,
                    'term': query,
                    'rettype': 'json',
                    'retmax': min(max_results, 10000),
                    'email': self.email,
                }
                if self.api_key:
                    search_params['api_key'] = self.api_key
                
                logger.info(f"Searching PubMed with query: {query[:100]}...")
                async with session.get(search_url, params=search_params) as resp:
                    if resp.status != 200:
                        raise Exception(f"PubMed search failed: {resp.status}")
                    search_result = await resp.json()
                
                uids = search_result.get('esearchresult', {}).get('idlist', [])
                total_count = int(search_result.get('esearchresult', {}).get('count', 0))
                
                logger.info(f"Found {total_count} studies, fetching details for {len(uids)} records")
                
                # Phase 2: Fetch full records
                if uids:
                    studies = await self._fetch_studies(session, uids)
                    return {
                        'total_count': total_count,
                        'retrieved_count': len(uids),
                        'studies': studies
                    }
                else:
                    return {
                        'total_count': 0,
                        'retrieved_count': 0,
                        'studies': []
                    }
        except Exception as e:
            logger.error(f"PubMed API error: {str(e)}")
            raise
    
    async def _fetch_studies(self, session: aiohttp.ClientSession, uids: List[str]) -> List[Dict]:
        """Fetch full study records from PubMed"""
        fetch_url = f"{self.base_url}/efetch.fcgi"
        studies = []
        
        # Process in batches
        for i in range(0, len(uids), self.batch_size):
            batch = uids[i:i + self.batch_size]
            fetch_params = {
                'db': self.db,
                'id': ','.join(batch),
                'rettype': 'json',
                'retmode': settings.PUBMED_RETMODE,
                'email': self.email,
            }
            if self.api_key:
                fetch_params['api_key'] = self.api_key
            
            try:
                async with session.get(fetch_url, params=fetch_params, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        articles = data.get('result', {}).get('articles', data.get('PubmedArticleSet', []))
                        if isinstance(articles, dict):
                            articles = articles.get('articles', [])
                        studies.extend(self._parse_articles(articles))
                    time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.warning(f"Error fetching batch {i}: {str(e)}")
                continue
        
        return studies
    
    def _parse_articles(self, articles: List[Dict]) -> List[Dict]:
        """Parse PubMed article JSON response"""
        parsed_studies = []
        
        for article in articles:
            try:
                if isinstance(article, dict):
                    pmid = article.get('uid') or article.get('MedlineCitation', {}).get('PMID', {}).get('content')
                    title = article.get('title', article.get('MedlineCitation', {}).get('Article', {}).get('ArticleTitle', ''))
                    abstract = article.get('abstract', article.get('MedlineCitation', {}).get('Article', {}).get('Abstract', {}).get('AbstractText', ''))
                    
                    if isinstance(abstract, list):
                        abstract = ' '.join(abstract)
                    
                    year = article.get('pubdate', '').split('-')[0] if 'pubdate' in article else ''
                    journal = article.get('journal', article.get('MedlineCitation', {}).get('Article', {}).get('Journal', {}).get('Title', ''))
                    
                    parsed_studies.append({
                        'pmid': str(pmid),
                        'title': title,
                        'abstract': abstract,
                        'year': year,
                        'journal': journal,
                        'source': 'pubmed'
                    })
            except Exception as e:
                logger.warning(f"Error parsing article: {str(e)}")
                continue
        
        return parsed_studies

async def fetch_pubmed_studies(query: str = None, max_results: int = None) -> Dict:
    """Utility function to fetch studies from PubMed"""
    api = PubMedAPI()
    return await api.search(query, max_results)
