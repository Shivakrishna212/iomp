from django.test import TestCase
import nltk
from nltk import word_tokenize
from nltk.metrics import jaccard_distance
from nltk.corpus import stopwords



def text_similarity_nltk(answer1, answer2):
    stop_words = set(stopwords.words("english"))
    # Tokenize the answers into individual words
    tokenized_answers = [word_tokenize(answer) for answer in [answer1, answer2]]
    print(tokenized_answers)

    # Remove stop words from the tokenized answers
    filtered_answers = [[word for word in answer if word.lower() not in stop_words] for answer in tokenized_answers]
    print(filtered_answers)
    # Calculate the Jaccard similarity between the two answers
    similarity = 1 - jaccard_distance(set(filtered_answers[0]), set(filtered_answers[1]))

    print("Jaccard Similarity: ", similarity)
    return similarity


answer1 = "Urbanization, the growth of cities and increased urban development, often leads to increased pollution in the form of air pollution, water pollution, and noise pollution. Cities are often filled with cars, factories, and other sources of emissions that contribute to smog and other harmful air pollutants, while runoff from urban areas can carry pollutants into waterways and harm aquatic life. Noise pollution from traffic, construction, and other sources can be loud and disruptive, causing stress and health problems. To minimize these environmental impacts and protect the health of people and the environment, it's crucial to manage urban growth in a responsible and sustainable way."
answer2 = "The growth of cities and urbanization can lead to numerous environmental problems, including air pollution, water pollution, and noise pollution. The increased presence of cars, factories, and other sources of emissions in cities can contribute to the formation of smog and other harmful air pollutants. Meanwhile, runoff from urban areas can carry pollutants into nearby waterways, causing harm to aquatic life. The loud and disruptive noise pollution from traffic, construction, and other sources can also cause health problems and stress. To reduce these environmental impacts and ensure the well-being of both people and the environment, it's critical to approach urban growth in a sustainable and responsible manner."

text_similarity_nltk(answer1,answer2)

# # time zone 
# import pytz
# from django.utils import timezone
# from datetime import datetime

# naive_datetime = datetime.now()
# timezone_aware_datetime = timezone.make_aware(naive_datetime, pytz.timezone("India/Mumbai"))
# print(timezone_aware_datetime)


# import nltk
# from nltk.tokenize import word_tokenize
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity


# # Create your tests here.

# # text similarity using sklearn

# def cosine_similarity_text(text1, text2):
#     vectorizer = CountVectorizer().fit_transform([text1, text2])
#     similarity = cosine_similarity(vectorizer[0], vectorizer[1])
#     print("Cosine similarity:", similarity)
#     return similarity[0][0]

# # text1 = "Online exams offer several benefits over traditional pen and paper assessments. They allow for increased flexibility in terms of time and location, as well as the ability to grade and analyze results immediately. This can save time and resources for both students and educators. Additionally, online exams can also include multimedia elements, such as videos and interactive simulations, which can enhance the overall learning experience. Answers assessments online provide a more accurate representation of students' understanding and can reduce the potential for cheating. Overall, online exams provide a convenient, efficient, and effective way to assess students' knowledge."


# # text2 = "Compared to traditional pen and paper tests, online exams offer a range of advantages. The flexibility of time and location makes it easier for both students and educators, and the instant grading and analysis capabilities saves precious time and resources. Furthermore, the integration of multimedia elements, such as videos and interactive simulations, enriches the overall learning experience. Assessing students' understanding through online answers assessments provides a more reliable evaluation and decreases the risk of cheating. In conclusion, online exams provide an efficient, convenient, and effective method of evaluating student knowledge."

# # similarity = cosine_similarity_text(text1, text2)









# # text similarity using nltk
# def text_similarity_nltk(answer1,answer2):
#     # answer1 = "Online exams offer several benefits over traditional pen and paper assessments. They allow for increased flexibility in terms of time and location, as well as the ability to grade and analyze results immediately. This can save time and resources for both students and educators. Additionally, online exams can also include multimedia elements, such as videos and interactive simulations, which can enhance the overall learning experience. Answers assessments online provide a more accurate representation of students' understanding and can reduce the potential for cheating. Overall, online exams provide a convenient, efficient, and effective way to assess students' knowledge.;          chane the wording of the above text but keep the meaning same"
#     # answer2 = "The use of plastic has become a widespread issue due to its negative impact on the environment, including pollution of land and oceans and harm to wildlife. There is growing consensus that reducing the use of single-use plastic items such as bags, straws, and water bottles is necessary to mitigate these impacts. Banning plastic altogether is a complex issue, as it is a versatile material that has many benefits, including being lightweight and durable, making it ideal for various products and packaging. However, there are alternative materials that can be used to replace single-use plastic items, and governments and industries can take steps to promote the use of these alternatives and reduce plastic waste through recycling and waste management programs. Ultimately, a balance between the benefits and drawbacks of plastic use must be found to protect the environment and promote sustainability."

#     answers = [answer1, answer2]

#     # Tokenize the answers into individual words
#     tokenized_answers = [word_tokenize(answer) for answer in answers]

#     # Convert the tokenized answers into a bag-of-words representation
#     vectorizer = CountVectorizer()
#     vectorized_answers = vectorizer.fit_transform(answers).toarray()

#     # Calculate the cosine similarity between the two answers
#     similarity = cosine_similarity(vectorized_answers[0].reshape(1, -1), vectorized_answers[1].reshape(1, -1))

#     print("Cosine Similarity: ", similarity[0][0])
#     return similarity[0][0]
