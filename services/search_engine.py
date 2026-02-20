import re
import time
from typing import List, Dict, Set
from collections import defaultdict
from models import School, SearchResult

class SearchEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchEngine, cls).__new__(cls)
            cls._instance.index = defaultdict(set) # Token -> Set[SchoolID]
            cls._instance.documents = {} # SchoolID -> School
        return cls._instance

    def index_data(self, schools: List[School]):
        print("Building In-Memory Index...")
        start_time = time.time()
        
        # Reset
        self.index.clear()
        self.documents.clear()
        
        for school in schools:
            self.documents[school.id] = school
            
            # Tokenize fields
            tokens = set()
            tokens.update(self._tokenize(school.name))
            tokens.update(self._tokenize(school.city))
            tokens.update(self._tokenize(school.state))
            
            # Add to index
            for token in tokens:
                self.index[token].add(school.id)
                
        print(f"Index built in {time.time() - start_time:.4f}s. Documents: {len(self.documents)}")

    def search(self, query: str, limit: int = 3) -> List[SearchResult]:
        if not query:
            return []
            
        q_tokens = self._tokenize(query)
        if not q_tokens:
            return []
            
        # --- Divide and Conquer Strategy: Tiered Search ---
        # Tier 1: Intersection (AND) - Precise, fast, small candidate set
        # OPTIMIZATION: Sort tokens by frequency (rarest first).
        # starting with the smallest set makes the intersection check O(small_set_size).
        # "school" (100k docs) vs "highland" (50 docs). Starting with "highland" is 2000x faster.
        
        # 1. Get posting lists
        token_lists = []
        for token in q_tokens:
            if token in self.index:
                size = len(self.index[token])
                token_lists.append((size, self.index[token]))
            else:
                return []
        
        # 2. Sort by size ASC (Smallest first)
        token_lists.sort(key=lambda x: x[0])
        
        if not token_lists:
             return []
             
        # 3. Intersect
        candidate_ids = set(token_lists[0][1])
        
        for size, postings in token_lists[1:]:
            # Skip intersection if candidate set is small and next set is huge
            if len(candidate_ids) < 200 and size > len(candidate_ids) * 50:
                 continue
                
            candidate_ids.intersection_update(postings)
            if not candidate_ids:
                break
        
        # Tier 2: Union (OR) - Fallback
        if len(candidate_ids) < limit:
            for size, postings in token_lists:
                 if size < 5000:
                    candidate_ids.update(postings)
        
        if not candidate_ids:
            return []
            
        candidate_list = list(candidate_ids)
        scored_results = []
        query_lower = query.lower()
        
        # --- Parallelism Strategy ---
        PARALLEL_THRESHOLD = 5000 
        
        if len(candidate_list) > PARALLEL_THRESHOLD:
            import concurrent.futures
            
            def score_batch(batch_ids):
                res = []
                for sid in batch_ids:
                    s = self.documents[sid]
                    scr = self._calculate_score(s, query_lower, q_tokens)
                    if scr > 0:
                        res.append(SearchResult(school=s, score=scr))
                return res

            chunk_size = len(candidate_list) // 4 + 1
            chunks = [candidate_list[i:i + chunk_size] for i in range(0, len(candidate_list), chunk_size)]
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(score_batch, chunk) for chunk in chunks]
                for future in concurrent.futures.as_completed(futures):
                    scored_results.extend(future.result())
        else:
            for school_id in candidate_list:
                school: School = self.documents[school_id]
                score = self._calculate_score(school, query_lower, q_tokens)
                if score > 0:
                    scored_results.append(SearchResult(school=school, score=score))
                
        # Sort and Return Top N (Heap Queue)
        # Optimization: Use a Heap (O(N log K)) instead of sorting the whole list (O(N log N))
        # We use nsmallest because we want:
        # 1. Highest Score (represented as -score for min-heap logic)
        # 2. Alphabetical Name (normal string comparison)
        import heapq
        return heapq.nsmallest(limit, scored_results, key=lambda x: (-x.score, x.school.name))

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        # Split by non-alphanumeric, keep only valid parts
        # "High-School" -> ["high", "school"]
        return [t for t in re.split(r'[^a-zA-Z0-9]', text.lower()) if t]

    def _calculate_score(self, school: School, query_phrase: str, query_tokens: List[str]) -> float:
        score = 0
        
        school_name = school.name.lower()
        school_city = school.city.lower()
        school_state = school.state.lower()
        
        # --- Phrase Matching ---
        # Exact Phrase in Name (+50)
        if query_phrase in school_name:
            score += 50
            if query_phrase == school_name: # Exact Match Bonus
                score += 10
                
        # Exact City Match (+30)
        if query_phrase == school_city:
            score += 30
            
        # --- Token Matching ---
        for token in query_tokens:
            token_matched = False
            
            # Name Match
            if token in school_name:
                score += 10
                token_matched = True
                # Prefix Bonus (starts with token)
                if school_name.startswith(token) or (" " + token) in school_name:
                     score += 5
            
            # City Match
            if token == school_city: # Exact token matches city
                score += 8
                token_matched = True
            elif token in school_city:
                score += 4
                token_matched = True
                
            # State Match
            if token == school_state:
                score += 5
                token_matched = True

        return score

search_engine = SearchEngine()
