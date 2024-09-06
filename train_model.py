import joblib
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

# Example labeled dataset (replace with your actual dataset)
sci_fi_texts = [
    ("In the future, detective AI solves crime mysteries on distant planets.", "crime"),
    ("A space crew encounters an ancient alien artifact with mysterious powers.", "mystery"),
    ("In a dystopian society, rebels fight against a totalitarian regime.", "dystopia"),
    ("The discovery of a parallel universe leads to unforeseen consequences.", "science fiction"),
    ("An AI uprising threatens the existence of humanity.", "dystopia"),
    ("A detective investigates a series of murders in a futuristic city.", "crime"),
    ("Explorers uncover a lost civilization buried deep beneath the Martian surface.", "adventure"),
    ("A rogue AI starts eliminating key figures in the human government.", "crime"),
    ("A team of scientists discovers a wormhole that leads to another galaxy.", "mystery"),
    ("In a dystopian future, corporations have more power than governments.", "dystopia"),
    ("The first human colony on Mars faces an unknown threat.", "science fiction"),
    ("A young hacker uncovers a conspiracy that threatens the world.", "dystopia"),
    ("A private investigator with cybernetic enhancements solves cases in a futuristic city.", "crime"),
    ("An expedition to a distant planet uncovers a civilization older than humanity.", "adventure"),
    ("A secret agent with advanced technology must stop a global threat.", "adventure"),
    ("Scientists develop a time machine that leads to paradoxes.", "science fiction"),
    ("A detective with a robotic assistant solves crimes in a utopian society.", "crime"),
    ("In a post-apocalyptic world, survivors fight against mutated creatures.", "dystopia"),
    ("Humans establish contact with a benevolent alien race.", "science fiction"),
    ("A space explorer discovers a planet with a thriving underwater civilization.", "adventure"),
    ("A cybernetic bounty hunter tracks down rogue robots in a megacity.", "crime"),
    ("A group of astronauts find themselves stranded on an unknown planet.", "mystery"),
    ("In a society where memories can be erased, a man fights to remember.", "dystopia"),
    ("A scientist invents a device that can manipulate gravity.", "science fiction"),
    ("A crew aboard a spaceship encounters a derelict vessel with a dark secret.", "mystery"),
    ("A genetically enhanced soldier leads a rebellion against an oppressive regime.", "dystopia"),
    ("An archaeologist uncovers alien technology on Earth.", "adventure"),
    ("A hacker infiltrates a powerful corporation to uncover the truth.", "dystopia"),
    ("An interstellar diplomat negotiates peace between warring alien species.", "science fiction"),
    ("A detective in a virtual reality world solves crimes by navigating different simulations.", "crime"),
    ("A rogue planet threatens to collide with Earth, and scientists race to prevent disaster.", "science fiction"),
    ("A space station crew deals with sabotage from within.", "mystery"),
    ("A future where people upload their consciousness to a digital realm.", "dystopia"),
    ("A team of explorers venture into a black hole to uncover its mysteries.", "adventure"),
    ("A group of survivors in a post-apocalyptic wasteland search for a safe haven.", "dystopia"),
    ("A scientist's experiment with teleportation goes horribly wrong.", "science fiction"),
    ("A detective investigates strange occurrences in a city filled with androids.", "crime"),
    ("A lone astronaut must survive on a distant planet with limited resources.", "adventure"),
    ("A journalist uncovers a cover-up involving extraterrestrial life.", "mystery"),
    ("A rebellion against an AI-controlled society leads to unexpected consequences.", "dystopia"),
    ("A futuristic city where everyone is monitored, and privacy is nonexistent.", "dystopia"),
    ("A space mission to explore a distant star system encounters an alien spacecraft.", "science fiction"),
    ("A young prodigy invents a device that can predict the future.", "science fiction"),
    ("A detective uses advanced forensics to solve crimes in a futuristic world.", "crime"),
    ("An expedition to the outer reaches of the solar system uncovers a hidden base.", "adventure"),
    ("A mysterious signal from deep space leads to a discovery that changes everything.", "mystery"),
    ("A group of rebels fight against a powerful AI overlord.", "dystopia"),
    ("A scientist discovers a new form of energy that could revolutionize the world.", "science fiction"),
    ("A detective unravels a conspiracy involving a powerful megacorp.", "crime"),
    ("A team of astronauts on a mission to Mars encounters unexpected challenges.", "adventure"),
    ("A space mission uncovers an ancient alien relic with immense power.", "mystery"),
    ("A future where humans can transfer their consciousness into different bodies.", "science fiction"),
    ("A detective with a cybernetic brain solves crimes by accessing victims' memories.", "crime"),
    ("A colony on a distant planet faces an unknown alien threat.", "adventure"),
    ("A journalist investigates a series of disappearances linked to a secret experiment.", "mystery"),
    ("A resistance movement fights against a dystopian government's oppressive rules.", "dystopia"),
    ("A scientist's discovery of parallel universes leads to dangerous consequences.", "science fiction"),
    ("A detective in a floating city investigates crimes involving advanced technology.", "crime"),
    ("A team of explorers uncovers a hidden alien city beneath the ocean.", "adventure"),
    ("A mysterious figure sabotages a space station, putting everyone on board at risk.", "mystery"),
    ("A group of rebels plan to overthrow a corrupt regime in a dystopian world.", "dystopia"),
    ("A scientist's invention allows people to communicate with aliens.", "science fiction"),
    ("A detective with a robotic assistant solves crimes in a futuristic utopia.", "crime"),
    ("A post-apocalyptic world where survivors fight for resources.", "dystopia"),
    ("A scientist's time travel experiment leads to unexpected changes in history.", "science fiction"),
    ("A space crew discovers a new element that defies the laws of physics.", "adventure"),
    ("A detective investigates a series of high-tech heists in a future metropolis.", "crime"),
    ("A team of scientists on a mission to explore a newly discovered planet.", "adventure"),
    ("A mysterious artifact on a distant moon holds the key to an ancient civilization.", "mystery"),
    ("A futuristic world where AI governs society, and humans struggle for independence.", "dystopia"),
    ("A scientist's discovery of a cure for aging leads to unforeseen consequences.", "science fiction"),
    ("A detective in a futuristic city solves crimes involving advanced technology.", "crime"),
    ("A team of explorers ventures into uncharted space to uncover its secrets.", "adventure"),
    ("A journalist investigates a shadowy organization with ties to the government.", "mystery"),
    ("A rebellion against a tyrannical AI ruler leads to a fight for freedom.", "dystopia"),
    ("A scientist's experiment creates a parallel universe with different laws of physics.", "science fiction"),
    ("A detective solves crimes in a world where everyone is connected to a central AI.", "crime"),
    ("A team of adventurers uncovers a lost civilization in the depths of space.", "adventure"),
    ("A mysterious signal from space leads to a discovery that could change humanity's fate.", "mystery"),
    ("A dystopian world where people are controlled by an all-seeing AI.", "dystopia"),
    ("A scientist's invention allows people to enter virtual worlds indistinguishable from reality.", "science fiction"),
    ("A detective in a future where memories can be erased, fights to remember the truth.", "crime"),
    ("A team of explorers travels to the edge of the galaxy to discover new worlds.", "adventure"),
    ("A mysterious phenomenon causes people to disappear without a trace.", "mystery"),
    ("A dystopian future where the rich live in luxury while the poor struggle to survive.", "dystopia"),
    ("A scientist's discovery of a new energy source could change the world forever.", "science fiction"),
    ("A detective uses advanced technology to solve crimes in a high-tech city.", "crime"),
    ("A team of adventurers sets out to explore a newly discovered planet.", "adventure"),
    ("A mysterious artifact found in space holds the key to an ancient civilization.", "mystery"),
    ("A dystopian society where free will is suppressed, and everyone follows strict rules.", "dystopia"),
    ("A scientist's invention allows people to travel between parallel universes.", "science fiction"),
    ("A detective in a future world solves crimes using AI and robotics.", "crime"),
    ("A team of explorers ventures into the unknown regions of space.", "adventure"),
    ("A journalist uncovers a hidden conspiracy that threatens humanity's future.", "mystery"),
    ("A rebellion against a corrupt government leads to a fight for freedom.", "dystopia"),
    ("A scientist's experiment with black holes leads to a dangerous discovery.", "science fiction"),
    ("A detective investigates a series of mysterious disappearances in a futuristic city.", "crime"),
    ("A team of astronauts on a deep-space mission encounters an unknown alien species.", "adventure"),
    ("A mysterious signal from deep space reveals the existence of extraterrestrial life.", "mystery"),
    ("A dystopian world where people are controlled by a powerful AI.", "dystopia"),
    ("A scientist's invention of a teleportation device leads to unexpected consequences.", "science fiction"),
    ("A detective solves crimes in a virtual reality world.", "crime"),
    ("A team of adventurers explores an alien planet with unique ecosystems.", "adventure"),
    ("A mysterious artifact found on a distant moon holds the key to an ancient secret.", "mystery"),
    ("A dystopian future where humans live under constant surveillance.", "dystopia"),
    ("A scientist's discovery of a parallel universe leads to a groundbreaking discovery.", "science fiction"),
    ("A detective uses advanced forensics to solve crimes in a futuristic city.", "crime"),
    ("A team of explorers ventures into uncharted space to uncover its mysteries.", "adventure"),
    ("A journalist investigates a series of high-profile disappearances.", "mystery"),
    ("A rebellion against an oppressive regime leads to a fight for justice.", "dystopia"),
    ("A scientist's invention allows people to travel through time.", "science fiction"),
    ("A detective in a future city solves crimes involving advanced technology.", "crime"),
    ("A team of adventurers sets out to explore the far reaches of the galaxy.", "adventure"),
    ("A mysterious signal from space leads to a discovery that changes everything.", "mystery"),
    ("A dystopian world where people are controlled by a powerful corporation.", "dystopia"),
    ("A scientist's experiment with genetic engineering leads to unforeseen consequences.", "science fiction"),
    ("A detective in a high-tech world solves crimes using cutting-edge technology.", "crime"),
    ("A team of explorers uncovers a hidden alien city on a distant planet.", "adventure"),
    ("A mysterious artifact found in space holds the key to an ancient civilization.", "mystery"),
    ("A dystopian future where the government controls every aspect of life.", "dystopia"),
    ("A scientist's invention allows people to enter virtual worlds indistinguishable from reality.", "science fiction"),
    ("A detective in a futuristic city solves crimes by accessing victims' memories.", "crime"),
    ("A team of adventurers explores a newly discovered planet in deep space.", "adventure"),
    ("A mysterious phenomenon causes people to disappear without a trace.", "mystery"),
    ("A dystopian world where the rich live in luxury while the poor struggle to survive.", "dystopia"),
    ("A scientist's discovery of a new energy source could change the world forever.", "science fiction"),
    ("A detective uses advanced technology to solve crimes in a high-tech metropolis.", "crime"),
    ("A team of adventurers sets out to explore the unknown regions of space.", "adventure"),
    ("A mysterious artifact found on a distant moon holds the key to an ancient secret.", "mystery"),
    ("A dystopian society where people are controlled by an all-powerful AI.", "dystopia"),
    ("A scientist's invention allows people to travel between parallel universes.", "science fiction"),
    ("A detective in a future world solves crimes using AI and robotics.", "crime"),
    ("A team of explorers ventures into uncharted space to uncover its mysteries.", "adventure"),
    ("A journalist investigates a hidden conspiracy that threatens humanity's future.", "mystery"),
    ("A rebellion against a tyrannical AI ruler leads to a fight for freedom.", "dystopia"),
    ("A scientist's experiment with black holes leads to a dangerous discovery.", "science fiction"),
    ("A detective investigates a series of mysterious disappearances in a futuristic city.", "crime"),
    ("A team of astronauts on a deep-space mission encounters an unknown alien species.", "adventure"),
    ("A mysterious signal from deep space reveals the existence of extraterrestrial life.", "mystery"),
    ("A dystopian world where people are controlled by a powerful AI.", "dystopia"),
    ("A scientist's invention of a teleportation device leads to unexpected consequences.", "science fiction")
]
   


texts = [text[0] for text in sci_fi_texts]
labels = [text[1] for text in sci_fi_texts]

# Preprocess text function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

# Apply preprocessing to all texts
texts = [preprocess_text(text) for text in texts]

# TF-IDF vectorization
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')

# Logistic Regression classifier
logistic_clf = LogisticRegression(max_iter=1000)

# Naive Bayes classifier
nb_clf = MultinomialNB()

# SVM classifier
svm_clf = SVC(probability=True)

# Create a voting classifier with soft voting
ensemble_clf = VotingClassifier(
    estimators=[
        ('lr', logistic_clf),
        ('nb', nb_clf),
        ('svm', svm_clf)
    ],
    voting='soft'
)

# Create a pipeline
pipeline = Pipeline([
    ('vectorizer', vectorizer),
    ('classifier', ensemble_clf)
])

# Hyperparameter tuning
param_grid = {
    'vectorizer__max_features': [500, 1000, 1500],
    'classifier__lr__C': [0.1, 1, 10],
    'classifier__svm__C': [0.1, 1, 10]
}

grid_search = GridSearchCV(pipeline, param_grid, cv=2, n_jobs=-1, verbose=2)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Fit the model
grid_search.fit(X_train, y_train)

# Save the best model and vectorizer
best_model = grid_search.best_estimator_
joblib.dump(best_model, 'sci_fi_theme_classifier.pkl')

# Evaluate the model
y_pred = best_model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(f"Classification Report:\n{classification_report(y_test, y_pred)}")