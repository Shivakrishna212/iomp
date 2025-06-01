import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.metrics import jaccard_distance
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# Load SBERT model once
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Ensure required NLTK resources are available
nltk.download('punkt')
nltk.download('stopwords')


def cosine_similarity_text(text1, text2):
    vectorizer = CountVectorizer().fit_transform([text1, text2])
    similarity = cosine_similarity(vectorizer[0], vectorizer[1])
    return similarity[0][0]


def tfidf_cosine_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
        return similarity[0][0]
    except ValueError:
        return 0.0


def text_similarity_nltk(answer1, answer2):
    stop_words = set(stopwords.words("english"))
    tokenized_answers = [word_tokenize(answer) for answer in [answer1, answer2]]
    filtered_answers = [[word for word in answer if word.lower() not in stop_words] for answer in tokenized_answers]
    similarity = 1 - jaccard_distance(set(filtered_answers[0]), set(filtered_answers[1]))
    return similarity


def sbert_similarity(text1, text2):
    embeddings = sbert_model.encode([text1, text2], convert_to_tensor=True)
    return float(util.pytorch_cos_sim(embeddings[0], embeddings[1]))


def get_combined_similarity_score(text1, text2):
    similarity_scores = []
    
    try:
        # Ensure texts are not empty
        if not text1 or not text2:
            return 0.0
            
        # Calculate similarity using different methods
        try:
            cosine_score = cosine_similarity_text(text1, text2)
            similarity_scores.append(cosine_score)
        except Exception as e:
            print(f"Error in cosine similarity: {str(e)}")
            
        try:
            tfidf_score = tfidf_cosine_similarity(text1, text2)
            similarity_scores.append(tfidf_score)
        except Exception as e:
            print(f"Error in TF-IDF similarity: {str(e)}")
            
        try:
            nltk_score = text_similarity_nltk(text1, text2)
            similarity_scores.append(nltk_score)
        except Exception as e:
            print(f"Error in NLTK similarity: {str(e)}")
            
        try:
            sbert_score = sbert_similarity(text1, text2)
            similarity_scores.append(sbert_score)
        except Exception as e:
            print(f"Error in SBERT similarity: {str(e)}")
        
        # Calculate average score only if we have at least one valid score
        if similarity_scores:
            average_score = sum(similarity_scores) / len(similarity_scores)
            print(similarity_scores)
            return round(average_score, 4)
        else:
            return 0.0
            
    except Exception as e:
        print(f"Error calculating combined similarity: {str(e)}")
        return 0.0
