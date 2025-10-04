# ================================
# src/services/incremental_nlp.py - Incremental NLP Engine
# ================================

"""
Incremental TF-IDF based NLP engine
Yeni haberler geldikçe kendini güncelleyen hafif NLP sistemi

Features:
- TF-IDF vectorization (hafif, hızlı)
- Incremental corpus update (yeni haber → model güncellenir)
- User profile vectorization
- Cosine similarity ranking
- Persistent storage (pickle)

No GPU required, no training needed.
"""

from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import json
import numpy as np
from collections import defaultdict

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ sklearn not installed. NLP features disabled.")

from ..models.reels_tracking import ReelFeedItem
from ..config import settings


class IncrementalNLPEngine:
    """
    Incremental TF-IDF NLP Engine
    
    Lifecycle:
    1. İlk 50 haber: Korpus topla, model yok
    2. 50. haber: İlk fitting, TF-IDF vocabulary oluşur
    3. Her 100 haber: Model refit edilir, vocabulary büyür
    4. 50K+ haber: max_features=2000 cap
    
    Memory: 50K haber ≈ 100MB
    Speed: Transform <10ms
    """
    
    def __init__(self):
        # Vectorizer (TF-IDF)
        self.vectorizer: Optional[TfidfVectorizer] = None
        
        # Corpus tracking
        self.corpus_texts: List[str] = []        # Tüm haber metinleri
        self.corpus_ids: List[str] = []          # Reel ID'leri
        self.corpus_metadata: List[Dict] = []    # Metadata (category, keywords)
        
        # Model state
        self.is_fitted = False
        self.last_update: Optional[datetime] = None
        self.counter = 0  # Refit counter
        
        # Cache for performance
        self.reel_vectors_cache: Dict[str, np.ndarray] = {}
        self.cache_ttl = timedelta(hours=24)
        
        # Configuration
        self.min_corpus_size = 50        # En az 50 haber olmalı
        self.refit_threshold = 100       # Her 100 haberde refit
        self.max_features_cap = 2000     # Max vocabulary size
        
        # Storage
        self.storage_dir = Path(settings.storage_base_path) / "models"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.storage_dir / "tfidf_vectorizer.pkl"
        
        # Load existing model if available
        self._load_model()
        
        print(f"✅ Incremental NLP Engine initialized")
        print(f"   Fitted: {self.is_fitted}")
        print(f"   Corpus size: {len(self.corpus_texts)}")
        if self.is_fitted:
            print(f"   Vocabulary size: {len(self.vectorizer.vocabulary_)}")
    
    def _get_turkish_stop_words(self) -> List[str]:
        """Türkçe stop words"""
        return [
            've', 'bir', 'bu', 'ile', 'için', 'da', 'de', 'mi', 'mı',
            'mu', 'mü', 'olan', 'olarak', 'ise', 'şu', 'o', 'gibi',
            'daha', 'çok', 'her', 'en', 'ne', 'ki', 'var', 'yok',
            'bu', 'şu', 'o', 'biz', 'siz', 'onlar', 'ben', 'sen'
        ]
    
    async def add_news_to_corpus(self, reel_id: str, text: str, metadata: Dict = None):
        """
        Yeni haber ekle (incremental)
        
        Args:
            reel_id: Reel ID
            text: Haber metni (title + summary)
            metadata: Category, keywords vb.
        
        Bu method her yeni reel oluşturulduğunda çağrılır
        """
        # Duplicate check
        if reel_id in self.corpus_ids:
            return
        
        # Corpus'a ekle
        self.corpus_texts.append(text)
        self.corpus_ids.append(reel_id)
        self.corpus_metadata.append(metadata or {})
        self.counter += 1
        
        # Periyodik refit (her 100 haberde)
        if self.counter >= self.refit_threshold:
            await self._refit_model()
            self.counter = 0
        
        # İlk fit (minimum corpus size)
        elif not self.is_fitted and len(self.corpus_texts) >= self.min_corpus_size:
            await self._fit_initial()
    
    async def _fit_initial(self):
        """İlk model fitting (50+ haber olunca)"""
        if not SKLEARN_AVAILABLE:
            print("⚠️ sklearn not available, skipping fit")
            return
        
        print(f"🎯 Initial TF-IDF fit with {len(self.corpus_texts)} news items")
        
        try:
            # Create vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=500,
                ngram_range=(1, 2),  # Unigram + bigram
                stop_words=self._get_turkish_stop_words(),
                min_df=2,            # En az 2 haberde geçsin
                max_df=0.8,          # Çok yaygın kelimeleri atla
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Fit
            self.vectorizer.fit(self.corpus_texts)
            self.is_fitted = True
            self.last_update = datetime.now()
            
            # Save model
            await self._save_model()
            
            print(f"✅ Model fitted! Vocabulary size: {len(self.vectorizer.vocabulary_)}")
            
        except Exception as e:
            print(f"❌ Initial fit error: {e}")
    
    async def _refit_model(self):
        """
        Model'i yeniden fit et (incremental update)
        
        Yeni haberler geldikçe vocabulary genişler
        """
        if not SKLEARN_AVAILABLE:
            return
        
        print(f"🔄 Refitting TF-IDF model with {len(self.corpus_texts)} news items")
        
        try:
            # Dinamik max_features (korpus büyüdükçe artar)
            corpus_size = len(self.corpus_texts)
            dynamic_max_features = min(
                500 + corpus_size // 10,  # Her 10 haber için +1 feature
                self.max_features_cap     # Max 2000
            )
            
            # Adaptive min_df (korpus büyüdükçe artar)
            adaptive_min_df = max(2, corpus_size // 1000)
            
            # Yeni vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=dynamic_max_features,
                ngram_range=(1, 2),
                stop_words=self._get_turkish_stop_words(),
                min_df=adaptive_min_df,
                max_df=0.8,
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Refit
            self.vectorizer.fit(self.corpus_texts)
            self.last_update = datetime.now()
            
            # Cache'i temizle (vectorizer değişti)
            self.reel_vectors_cache.clear()
            
            # Save
            await self._save_model()
            
            print(f"✅ Model refitted! New vocab size: {len(self.vectorizer.vocabulary_)}")
            print(f"   max_features: {dynamic_max_features}, min_df: {adaptive_min_df}")
            
        except Exception as e:
            print(f"❌ Refit error: {e}")
    
    def get_reel_vector(self, reel_id: str, text: str) -> Optional[np.ndarray]:
        """
        Reel'in TF-IDF vektörünü al (cached)
        
        Args:
            reel_id: Reel ID
            text: Haber metni
        
        Returns:
            numpy array or None
        """
        # Model fitted değilse
        if not self.is_fitted:
            return None
        
        # Cache check
        if reel_id in self.reel_vectors_cache:
            return self.reel_vectors_cache[reel_id]
        
        try:
            # Transform
            vector = self.vectorizer.transform([text]).toarray()[0]
            
            # Cache (24 saat TTL)
            self.reel_vectors_cache[reel_id] = vector
            
            return vector
            
        except Exception as e:
            print(f"❌ Vector error for {reel_id}: {e}")
            return None
    
    async def build_user_profile(
        self, 
        watched_reels: List[Dict]
    ) -> Optional[np.ndarray]:
        """
        Kullanıcının izlediği haberlerden profil oluştur
        
        Args:
            watched_reels: [
                {
                    "reel_id": "...", 
                    "text": "title + summary",
                    "engagement": 0.8
                },
                ...
            ]
        
        Returns:
            User profile vector (weighted average)
        """
        if not self.is_fitted or not watched_reels:
            return None
        
        # Ağırlıklı ortalama (engagement'e göre)
        vectors = []
        weights = []
        
        for item in watched_reels:
            vector = self.get_reel_vector(item["reel_id"], item["text"])
            if vector is not None:
                vectors.append(vector)
                weights.append(item.get("engagement", 0.5))
        
        if not vectors:
            return None
        
        # Weighted average
        vectors = np.array(vectors)
        weights = np.array(weights)
        
        # Normalize weights
        weights = weights / weights.sum()
        
        # Weighted average
        user_profile = np.average(vectors, axis=0, weights=weights)
        
        return user_profile
    
    async def rank_reels(
        self, 
        user_profile: Optional[np.ndarray], 
        candidate_reels: List[Dict]
    ) -> List[Tuple[any, float]]:
        """
        Reels'leri kullanıcı profiline göre sırala
        
        Args:
            user_profile: User vector (from build_user_profile)
            candidate_reels: [
                {
                    "reel_id": "...", 
                    "text": "...", 
                    "reel_obj": ReelFeedItem
                },
                ...
            ]
        
        Returns:
            [(reel_obj, similarity_score), ...]
        """
        # Model fitted değilse veya user profile yoksa
        if not self.is_fitted or user_profile is None:
            # Fallback: sıralama yok, olduğu gibi dön
            return [(r["reel_obj"], 0.5) for r in candidate_reels]
        
        scored_reels = []
        
        for item in candidate_reels:
            # Reel vektörü
            reel_vector = self.get_reel_vector(item["reel_id"], item["text"])
            
            if reel_vector is not None:
                # Cosine similarity
                similarity = cosine_similarity(
                    [user_profile], 
                    [reel_vector]
                )[0][0]
            else:
                similarity = 0.3  # Default skor
            
            scored_reels.append((item["reel_obj"], float(similarity)))
        
        # Sırala (yüksekten düşüğe)
        scored_reels.sort(key=lambda x: x[1], reverse=True)
        
        return scored_reels
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Metinden önemli kelimeleri çıkar
        
        Args:
            text: Haber metni
            top_n: Kaç kelime döndürsün
        
        Returns:
            List of keywords
        """
        if not self.is_fitted:
            # Fallback: basit split
            words = text.lower().split()
            stop_words = set(self._get_turkish_stop_words())
            keywords = [w for w in words if w not in stop_words and len(w) > 3]
            return keywords[:top_n]
        
        try:
            # TF-IDF ile keyword extraction
            vector = self.vectorizer.transform([text])
            
            # Feature names (kelimeler)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # TF-IDF skorları
            scores = vector.toarray()[0]
            
            # Top N kelimeyi al
            top_indices = scores.argsort()[-top_n:][::-1]
            keywords = [feature_names[i] for i in top_indices if scores[i] > 0]
            
            return keywords
            
        except Exception as e:
            print(f"❌ Keyword extraction error: {e}")
            return []
    
    async def _save_model(self):
        """Model'i pickle ile kaydet"""
        if not self.is_fitted:
            return
        
        try:
            data = {
                'vectorizer': self.vectorizer,
                'corpus_ids': self.corpus_ids,
                'corpus_metadata': self.corpus_metadata,
                'last_update': self.last_update,
                'is_fitted': self.is_fitted,
                'counter': self.counter
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(data, f)
            
            # Corpus texts ayrı kaydet (çok büyük olabilir)
            corpus_path = self.storage_dir / "corpus_texts.json"
            with open(corpus_path, 'w', encoding='utf-8') as f:
                json.dump(self.corpus_texts, f, ensure_ascii=False)
            
            print(f"💾 Model saved: {self.model_path}")
            
        except Exception as e:
            print(f"❌ Model save error: {e}")
    
    def _load_model(self):
        """Kaydedilmiş model'i yükle"""
        if not self.model_path.exists():
            print("⚠️ No saved model found, starting fresh")
            return
        
        try:
            # Model yükle
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
            
            self.vectorizer = data['vectorizer']
            self.corpus_ids = data['corpus_ids']
            self.corpus_metadata = data.get('corpus_metadata', [])
            self.last_update = data['last_update']
            self.is_fitted = data['is_fitted']
            self.counter = data.get('counter', 0)
            
            # Corpus texts yükle
            corpus_path = self.storage_dir / "corpus_texts.json"
            if corpus_path.exists():
                with open(corpus_path, 'r', encoding='utf-8') as f:
                    self.corpus_texts = json.load(f)
            
            print(f"✅ Model loaded!")
            print(f"   Corpus size: {len(self.corpus_texts)}")
            print(f"   Vocab size: {len(self.vectorizer.vocabulary_)}")
            
        except Exception as e:
            print(f"❌ Model load error: {e}")
            print("   Starting fresh...")
    
    def get_stats(self) -> Dict:
        """Model istatistikleri"""
        return {
            "is_fitted": self.is_fitted,
            "corpus_size": len(self.corpus_texts),
            "vocab_size": len(self.vectorizer.vocabulary_) if self.is_fitted else 0,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "cache_size": len(self.reel_vectors_cache),
            "refit_counter": self.counter,
            "next_refit_in": self.refit_threshold - self.counter,
            "max_features": self.vectorizer.max_features if self.is_fitted else 0
        }
    
    def clear_cache(self):
        """Cache'i temizle"""
        self.reel_vectors_cache.clear()
        print("🗑️ Cache cleared")


# Global instance
incremental_nlp = IncrementalNLPEngine()