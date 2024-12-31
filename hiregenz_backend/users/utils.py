import re
import spacy
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken

# Preload SpaCy model
nlp = spacy.load("en_core_web_sm")

SKILL_KEYWORDS = [
    # Programming Languages
    "Python", "Java", "C++", "C", "C#", "JavaScript", "TypeScript", "Ruby", "PHP", "Go", "Swift", 
    "Kotlin", "R", "Scala", "Perl", "MATLAB", "Shell Scripting", "Dart", "Rust", "Lua", "Haskell", 
    "COBOL", "Fortran", "VBScript", "Assembly Language", "Erlang", "Elixir", "F#", "Julia", "Solidity",

    # Frontend Frameworks
    "React", "Angular", "Vue.js", "Next.js", "Nuxt.js", "Svelte", "Ember.js", "Gatsby", 
    "Backbone.js", "Alpine.js", "Meteor", "Stencil", "Preact", "LitElement",

    # Backend Frameworks
    "Node.js", "Express.js", "NestJS", "Fastify", "Spring Boot", "Hibernate", "Django", "Flask", 
    "Bottle", "Tornado", "Pyramid", "CherryPy", "Ruby on Rails", "Laravel", "Symfony", "CodeIgniter", 
    "CakePHP", "ASP.NET Core", "ASP.NET MVC", "Koa.js", "Struts", "JHipster", "Micronaut", "Dropwizard", 
    "Gin", "Beego", "Echo", "Fiber (Go)", "Phoenix (Elixir)",

    # Mobile Development Frameworks
    "React Native", "Flutter", "Ionic", "Cordova", "Xamarin", "NativeScript", "SwiftUI", 
    "Jetpack Compose", "Apache Flex",

    # Data Science & Machine Learning Frameworks
    "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "Theano", "MXNet", "Caffe", "Pandas", 
    "NumPy", "Matplotlib", "Seaborn", "Plotly", "Dask", "H2O.ai", "MLlib", "XGBoost", "LightGBM", 
    "CatBoost", "Statsmodels", "Dash", "Streamlit", "Hugging Face Transformers", "OpenCV", "NLTK", "Spacy",

    # Data Engineering & Big Data Frameworks
    "Apache Spark", "Hadoop", "Flink", "Kafka", "Hive", "Storm", "Airflow", "Dask", "Presto", 
    "Apache Beam", "AWS Glue", "Azure Data Factory", "Snowflake", "BigQuery", "ClickHouse",

    # DevOps Frameworks & Tools
    "Docker", "Kubernetes", "Terraform", "Ansible", "Puppet", "Chef", "Vagrant", "Prometheus", 
    "Grafana", "Jenkins", "CircleCI", "Travis CI", "Bamboo", "TeamCity", "Spinnaker", "Helm", "Consul", 
    "Vault", "Istio", "Linkerd", "Elastic Stack (ELK)",

    # Database Frameworks
    "SQLAlchemy", "Hibernate ORM", "Mongoose", "Django ORM", "Sequelize", "Prisma", "ActiveRecord", 
    "TypeORM", "Knex.js", "Alembic",

    # API Development Frameworks
    "FastAPI", "Flask-RESTful", "GraphQL", "Apollo", "Relay", "gRPC", "Swagger", "Postman", 
    "JSON Server", "Hapi.js", "LoopBack", "Feathers.js", "Restify",

    # Security Frameworks
    "OWASP", "Spring Security", "JWT (JSON Web Tokens)", "OAuth2", "Keycloak", "Passport.js", 
    "SAML", "OpenID Connect (OIDC)", "IAM (Identity and Access Management)", "Zero Trust Framework",

    # ERP & CRM Frameworks
    "SAP", "Salesforce", "Zoho CRM", "Odoo", "Microsoft Dynamics 365", "Oracle ERP", "NetSuite", 
    "HubSpot CRM", "Workday", "Tally", "QuickBooks", "JD Edwards", "Deltek", "PeopleSoft", 
    "Epicor", "Sage Intacct", "Infor",

    # Testing Frameworks
    "Selenium", "JUnit", "TestNG", "Cypress", "Playwright", "Puppeteer", "Mocha", "Chai", "Jest", 
    "Enzyme", "Karma", "Protractor", "Appium", "Robot Framework", "Postman", "Pytest", "Unittest", 
    "Allure", "Cucumber", "SpecFlow", "Gauge", "xUnit",

    # UI/UX Design Frameworks
    "Material-UI", "Ant Design", "Tailwind CSS", "Bootstrap", "Foundation", "Chakra UI", 
    "Vuetify", "Bulma", "Quasar", "Metro 4", "PrimeNG", "PrimeReact", "Carbon Design System", 
    "Figma", "Adobe XD", "Sketch",

    # Cloud Frameworks & Services
    "AWS", "Azure", "Google Cloud Platform (GCP)", "OpenStack", "Cloud Foundry", "Heroku", 
    "DigitalOcean", "Firebase", "Kong", "Zuul", "Knative", "Serverless Framework", "AWS Lambda", 
    "Azure Functions", "Google Cloud Functions",

    # Blockchain Frameworks
    "Ethereum", "Hyperledger", "Solidity", "Truffle", "Ganache", "Web3.js", "Ethers.js", 
    "IPFS", "Chaincode", "Corda", "Polygon", "Polkadot", "Solana", "EOS.IO", "Stellar",

    # General Frameworks & Miscellaneous
    "Scrum", "Agile", "Kanban", "Six Sigma", "ITIL", "COBIT", "Lean", "PRINCE2", "SAFe (Scaled Agile)", 
    "DevSecOps", "ISO 27001", "GDPR Compliance", "SOX Compliance", "TOGAF", "Zachman Framework", 
    "Balanced Scorecard", "PESTLE Analysis", "SWOT Analysis", "Business Model Canvas", 
    "Value Stream Mapping", "Kaizen", "RPA Frameworks (Blue Prism, UiPath, Automation Anywhere)", 
    "Unity", "Unreal Engine", "Godot"
]


def extract_email(text):
    """Extract email from text using regex."""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None


def extract_phone(text):
    """Extract phone number from text using regex."""
    match = re.search(r'\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{4,10}', text)
    return match.group(0) if match else None


def extract_name(text):
    """Extract name from the first few lines using heuristics."""
    try:
        lines = text.splitlines()[:5]
        for line in lines:
            if re.match(r'^[A-Z][a-z]+\s[A-Z][a-z]+$', line.strip()):  # Matches "First Last"
                return line.strip()
        return None
    except Exception as e:
        print(f"Error extracting name: {str(e)}")
        return None


def extract_skills(text):
    """Extract skills using predefined keywords."""
    doc = nlp(text)
    skills = {token.text for token in doc if token.text in SKILL_KEYWORDS}
    return list(skills)


def extract_section(text, heading):
    """Extract specific sections like certifications or summary."""
    try:
        pattern = rf"{heading}.*?(?=\n[A-Z\s]+:|\Z)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(0).strip() if match else None
    except Exception as e:
        print(f"Error extracting section '{heading}': {str(e)}")
        return None


def calculate_total_experience(work_experience_text):
    """
    Calculate the total work experience in years (floating-point format) from the work experience section.
    """
    if not work_experience_text or work_experience_text.strip() == "Not Found":
        return "0.0"

    try:
        # Match a wide range of date patterns
        date_patterns = [
            r"(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4})",  # e.g., "Jan 2020"
            r"(?:(January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4})",
            r"(\d{4}[-/.]\d{1,2})",
            r"(\d{1,2}[-/.]\d{4})",
            r"(\d{4})"
        ]

        combined_pattern = "|".join(date_patterns)
        matches = re.findall(combined_pattern, work_experience_text)

        dates = []
        for match_group in matches:
            match = next(filter(None, match_group))  # Get the first non-empty match
            try:
                if re.match(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", match):
                    date_obj = datetime.strptime(match, "%b %Y")
                elif re.match(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)", match):
                    date_obj = datetime.strptime(match, "%B %Y")
                elif re.match(r"\d{4}[-/.]\d{1,2}", match):
                    date_obj = datetime.strptime(match, "%Y-%m")
                elif re.match(r"\d{1,2}[-/.]\d{4}", match):
                    date_obj = datetime.strptime(match, "%m/%Y")
                elif re.match(r"\d{4}", match):
                    date_obj = datetime.strptime(match, "%Y")
                else:
                    continue
                dates.append(date_obj)
            except ValueError:
                continue

        if re.search(r"(?i)\b(Present|Now)\b", work_experience_text):
            dates.append(datetime.now())

        dates = sorted(dates)
        total_months = 0
        for i in range(0, len(dates) - 1, 2):
            start_date = dates[i]
            end_date = dates[i + 1] if i + 1 < len(dates) else datetime.now()
            total_months += (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

        return f"{total_months / 12:.1f}"
    except Exception as e:
        print(f"Error calculating total experience: {str(e)}")
        return "0.0"


def extract_resume_data(text):
    """Extract structured data from resume text with robust error handling."""
    try:
        name = extract_name(text) or "Unknown"
        email = extract_email(text) or "Not Found"
        phone = extract_phone(text) or "Not Found"
        skills = extract_skills(text) or []
        certifications = extract_section(text, "CERTIFICATIONS") or "Not Found"
        education = extract_section(text, "EDUCATION") or "Not Found"
        work_experience = extract_section(text, "WORK EXPERIENCE") or "Not Found"
        summary = extract_section(text, "SUMMARY") or "Not Found"
        total_experience = (
            calculate_total_experience(work_experience) if work_experience != "Not Found" else "0.0"
        )

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "certifications": certifications,
            "education": education,
            "work_experience": work_experience,
            "professional_summary": summary,
            "total_experience": total_experience,
        }
    except Exception as e:
        raise ValueError(f"Error in extract_resume_data: {str(e)}")


class TokenUtility:
    @staticmethod
    def get_tokens_for_user(user):
        """
        Generate JWT tokens with additional claims for the user.
        """
        refresh = RefreshToken.for_user(user)
        # Add custom claims
        refresh['role'] = user.role
        refresh['email'] = user.email
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }