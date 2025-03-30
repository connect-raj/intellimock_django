import re
import spacy
import PyPDF2

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Predefined skills list
SKILLS_LIST = [
    "Python", "Jupyter", "Pandas", "NumPy", "SciPy", "Flask", "Django", "Pytest", "PyTorch",
    "Java", "Spring", "Spring Boot", "Hibernate", "JavaFX", "JSP",
    "C++", "STL", "Boost", "CMake", "Qt",
    "JavaScript", "ES6", "Node.js", "TypeScript", "jQuery", "Express.js",
    "SQL", "PostgreSQL", "MariaDB", "SQLite", "T-SQL", "NoSQL", "MongoDB", "Cassandra",
    "Machine Learning", "Scikit-learn", "XGBoost", "LightGBM", "Keras", "OpenCV",
    "Deep Learning", "Neural Networks", "CNNs", "RNNs", "GANs", "Reinforcement Learning",
    "NLP", "SpaCy", "NLTK", "Hugging Face Transformers", "NER", "Sentiment Analysis",
    "Data Analysis", "Matplotlib", "Seaborn", "Tableau", "Power BI",
    "TensorFlow", "TensorFlow Lite", "TensorFlow.js", "Keras", "TensorFlow Extended",
    "PyTorch", "TorchVision", "TorchText", "TorchAudio", "PyTorch Lightning",
    "Django", "Django REST Framework", "Django Channels", "Celery",
    "Flask", "Flask RESTful", "Flask-SQLAlchemy", "Flask-JWT", "Flask-WTF",
    "ReactJS", "React Native", "Redux", "React Router", "Next.js", "JSX",
    "Angular", "AngularJS", "Angular Material", "NgRx",
    "Node.js", "Express.js", "NestJS", "Fastify", "Socket.io",
    "AWS", "EC2", "S3", "Lambda", "RDS", "AWS Amplify", "DynamoDB", "AWS CloudFormation",
    "Azure", "Azure Functions", "Azure Blob Storage", "Azure SQL Database", "Azure Kubernetes Service", "Azure Active Directory",
    "GCP", "Google App Engine", "Google Compute Engine", "BigQuery", "Firebase", "Google Kubernetes Engine",
    "HTML", "HTML5", "Semantic HTML", "Web Components",
    "CSS", "CSS3", "Flexbox", "CSS Grid", "SASS", "LESS", "Bootstrap",
    "MySQL", "MariaDB", "PostgreSQL", "MongoDB", "SQLite",
    "DevOps", "Docker", "Kubernetes", "Jenkins", "Terraform", "Ansible", "CI/CD",
    "Cloud Computing", "AWS", "Google Cloud", "Microsoft Azure", "IBM Cloud", "Oracle Cloud",
    "Containerization", "Docker", "Kubernetes", "OpenShift", "Docker Compose",
    "Big Data", "Apache Hadoop", "Apache Spark", "Apache Kafka", "Hive", "Pig",
    "Blockchain", "Ethereum", "Solidity", "Hyperledger", "Cryptocurrency Development",
    "UI/UX Design", "Figma", "Sketch", "Adobe XD", "InVision", "Wireframing",
    "Cybersecurity", "Ethical Hacking", "Penetration Testing", "SIEM", "Firewalls and Network Security", "SSL/TLS Encryption",
    "Mobile App Development", "Android", "Java", "Kotlin", "iOS", "Swift", "Flutter", "React Native", "Xamarin",
    "Game Development", "Unity", "Unreal Engine", "C#", "Blender", "Cocos2d",
    "Version Control", "Git", "GitHub", "GitLab", "Bitbucket",
    "Automation", "Selenium", "Robot Framework", "AutoHotkey", "Cypress",
    "Test Automation", "JUnit", "TestNG", "Mocha", "Jest", "Cypress",
    "IoT", "Raspberry Pi", "Arduino", "MQTT", "Zigbee", "PHP"
]


def extract_text_from_pdf(file_obj):
    """
    Extract text from a PDF file uploaded via Django's request.FILES.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading PDF: {e}")

def extract_skills(text):
    """
    Extract skills from the text using a predefined list.
    """
    extracted_skills = set()
    for skill in SKILLS_LIST:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            extracted_skills.add(skill)
    return list(extracted_skills)

def extractSkills(file_obj):
    """
    Extract skills from a PDF uploaded via Django request.FILES.
    """
    text = extract_text_from_pdf(file_obj)
    return extract_skills(text)