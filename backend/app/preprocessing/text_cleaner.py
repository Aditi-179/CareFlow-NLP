import re
from typing import List, Dict, Any

try:
    import nltk
    from nltk.tokenize import word_tokenize
    try:
        nltk.data.find('tokenizers/punkt')
    except (LookupError, OSError):
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except (LookupError, OSError):
        nltk.download('punkt_tab', quiet=True)
    NLTK_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False


# Medically critical negation words that must NEVER be stripped
MEDICAL_NEGATIONS = {
    "not", "no", "never", "without", "none", "neither", "nor", 
    "non", "negative", "denies", "absent", "free"
}

# Standard English stop words to filter out ONLY if they are NOT in MEDICAL_NEGATIONS
BASE_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", 
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", 
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", 
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", 
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", 
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", 
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", 
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", 
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", 
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", 
    "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", 
    "the", "their", "theirs", "them", "themselves", "then", "there", "there's", 
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", 
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", 
    "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", 
    "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", 
    "you're", "you've", "your", "yours", "yourself", "yourselves"
} - MEDICAL_NEGATIONS


class PreprocessingPipeline:
    """
    Healthcare Query Preprocessing Pipeline:
    1. Lowercase normalization
    2. Medical negation preservation
    3. Noise & punctuation handling
    4. Tokenization (NLTK with regex fallback)
    5. Clean query reconstruction
    """

    def __init__(self):
        self.negations = MEDICAL_NEGATIONS
        self.stop_words = BASE_STOP_WORDS

    def clean_text(self, text: str) -> str:
        """Removes extraneous whitespace, non-printable characters, and formatting noise."""
        if not text:
            return ""
        # Remove URLs or email artifacts if any
        text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes text using NLTK word_tokenize with fallback to regex."""
        if NLTK_AVAILABLE:
            try:
                return word_tokenize(text)
            except Exception:
                pass
        # Fallback regex tokenizer (preserves words with hyphens or apostrophes)
        return re.findall(r"\b\w+(?:[-']\w+)*\b|[^\w\s]", text)

    def process(self, query: str) -> Dict[str, Any]:
        """
        Executes the full preprocessing pipeline on a user query.
        Returns cleaned text, normalized tokens, identified negations, and metadata.
        """
        raw_text = self.clean_text(query)
        lower_text = raw_text.lower()

        # Tokenize
        raw_tokens = self.tokenize(lower_text)

        # Detect negations present in the query
        detected_negations = [token for token in raw_tokens if token in self.negations]

        # Filter out standalone punctuation for the token stream while keeping word tokens
        word_tokens = [re.sub(r"[^\w\-]", "", token) for token in raw_tokens]
        word_tokens = [t for t in word_tokens if t]

        # Filtered tokens for keyword extraction (preserves negations)
        informative_tokens = [t for t in word_tokens if t not in self.stop_words]

        # Reconstructed normalized query string
        normalized_query = " ".join(word_tokens)

        return {
            "original_query": query,
            "normalized_query": normalized_query if normalized_query else lower_text,
            "tokens": word_tokens,
            "informative_tokens": informative_tokens,
            "has_negation": len(detected_negations) > 0,
            "negations_found": list(set(detected_negations)),
            "token_count": len(word_tokens),
        }


# Global singleton instance
pipeline = PreprocessingPipeline()

def preprocess_query(query: str) -> Dict[str, Any]:
    return pipeline.process(query)

