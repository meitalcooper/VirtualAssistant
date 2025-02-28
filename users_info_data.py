"""
Database population script for the Voice Assistant system.
Creates test users with culturally appropriate names across different countries.
This script helps in setting up a realistic test environment by:
- Generating unique usernames
- Creating diverse user profiles
- Setting up manager relationships
"""
from utils import generate_password_hasshed
from faker import Faker
from app import create_app, db
from models import User
from datetime import date, timedelta
import random




app = create_app()


# Custom names for Asian, Middle Eastern, and Peruvian countries
CUSTOM_NAMES = {
    # Asia Pacific
    'China': {
        'first': ['Ming', 'Wei', 'Li', 'Hui', 'Xiao', 'Jin', 'Chen', 'Ying', 'Hong', 'Jing', 
                 'Yuan', 'Xiang', 'Mei', 'Lin', 'Jun', 'Yan', 'Yu', 'Hua', 'Ping', 'Yong'],
        'last': ['Zhang', 'Li', 'Wang', 'Chen', 'Liu', 'Yang', 'Huang', 'Zhou', 'Wu', 'Xu']
    },
    'Japan': {
        'first': ['Ken', 'Yuki', 'Taro', 'Hiro', 'Kenji', 'Akiko', 'Yoko', 'Sakura', 'Ryu', 'Kaori',
                 'Daisuke', 'Hiroshi', 'Takashi', 'Yoshi', 'Shin', 'Mai', 'Yui', 'Kenta', 'Sota', 'Yuma'],
        'last': ['Sato', 'Suzuki', 'Tanaka', 'Watanabe', 'Ito', 'Yamamoto', 'Nakamura', 'Kobayashi', 'Kato', 'Yoshida']
    },
    'Korea': {
        'first': ['Min', 'Jin', 'Seo', 'Jun', 'Hyun', 'Sung', 'Ji', 'Hye', 'Soo', 'Young'],
        'last': ['Kim', 'Lee', 'Park', 'Choi', 'Jung', 'Kang', 'Cho', 'Han', 'Yoon', 'Jang']
    },
    'India': {
        'first': ['Raj', 'Amit', 'Arun', 'Priya', 'Neha', 'Rahul', 'Sanjay', 'Deepa', 'Anita', 'Sunil'],
        'last': ['Patel', 'Kumar', 'Singh', 'Shah', 'Sharma', 'Verma', 'Gupta', 'Malhotra', 'Reddy', 'Kapoor']
    },
    'Thailand': {
        'first': ['Somchai', 'Somsak', 'Chai', 'Supaporn', 'Suchada', 'Pitchaya', 'Anong', 'Prasert', 'Chatri', 'Sunee'],
        'last': ['Saetang', 'Srisai', 'Chaiprasit', 'Wongsawat', 'Suntornvit', 'Tansiri', 'Ruangrat', 'Naratap', 'Chaisuwan', 'Sae-tang']
    },
    
    # Middle East
    'Israel': {
        'first': ['David', 'Moshe', 'Yosef', 'Sarah', 'Rachel', 'Daniel', 'Michael', 'Avraham', 'Ruth', 'Esther'],
        'last': ['Cohen', 'Levy', 'Mizrahi', 'Peretz', 'Friedman', 'Shapiro', 'Goldstein', 'Stern', 'Katz', 'Levin']
    },
    'Saudi Arabia': {
        'first': ['Mohammed', 'Ahmed', 'Abdullah', 'Ali', 'Hassan', 'Fatima', 'Aisha', 'Omar', 'Ibrahim', 'Nasser'],
        'last': ['Al-Saud', 'Al-Sheikh', 'Al-Qahtani', 'Al-Ghamdi', 'Al-Rashid', 'Al-Harbi', 'Al-Dossari', 'Al-Shamri', 'Al-Otaibi', 'Al-Zahrani']
    },
    'Turkey': {
        'first': ['Mehmet', 'Mustafa', 'Ahmet', 'Ayse', 'Fatma', 'Emine', 'Ali', 'Ibrahim', 'Can', 'Eren'],
        'last': ['Yilmaz', 'Kaya', 'Demir', 'Sahin', 'Celik', 'Yildiz', 'Arslan', 'Tas', 'Aksoy', 'Ozturk']
    },
    'United Arab Emirates': {
        'first': ['Ahmad', 'Mohammed', 'Rashid', 'Fatima', 'Mariam', 'Sultan', 'Saeed', 'Hamad', 'Omar', 'Ali'],
        'last': ['Al-Maktoum', 'Al-Nahyan', 'Al-Qasimi', 'Al-Mazrouei', 'Al-Shamsi', 'Al-Mansoori', 'Al-Falasi', 'Al-Suwaidi', 'Al-Dhaheri', 'Al-Ali']
    },
    'Qatar': {
        'first': ['Hassan', 'Khalid', 'Mohammed', 'Abdulaziz', 'Noora', 'Maryam', 'Hamad', 'Jassim', 'Abdullah', 'Ali'],
        'last': ['Al-Thani', 'Al-Kuwari', 'Al-Naimi', 'Al-Khater', 'Al-Sulaiti', 'Al-Mannai', 'Al-Hajri', 'Al-Marri', 'Al-Mohannadi', 'Al-Ansari']
    },
    
    # Latin America
    'Peru': {
        'first': ['Carlos', 'Luis', 'Jorge', 'Miguel', 'Jose', 'Maria', 'Ana', 'Rosa', 'Carmen', 'Julia'],
        'last': ['Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Torres', 'Flores', 'Vargas', 'Chavez', 'Ramos', 'Quispe']
    }
}

# Faker locale mapping for other countries
LOCALE_MAPPING = {
    # Asia Pacific (English-speaking)
    'Australia': 'en_AU',
    'New Zealand': 'en_NZ',
    'Singapore': 'en_GB',
    'Malaysia': 'en_GB',
    'Philippines': 'en_GB',
    'Indonesia': 'en_GB',
    'Taiwan': 'en_GB',
    
    # Europe
    'Austria': 'de_AT',
    'Belgium': 'fr_BE',
    'Czech Republic': 'cs_CZ',
    'Denmark': 'da_DK',
    'Finland': 'fi_FI',
    'France': 'fr_FR',
    'Germany': 'de_DE',
    'Ireland': 'en_IE',
    'Italy': 'it_IT',
    'Netherlands': 'nl_NL',
    'Norway': 'no_NO',
    'Poland': 'pl_PL',
    'Portugal': 'pt_PT',
    'Spain': 'es_ES',
    'Sweden': 'sv_SE',
    'Switzerland': 'de_CH',
    'Ukraine': 'uk_UA',
    'United Kingdom': 'en_GB',
    
    
    # Latin America
    'Argentina': 'es_AR',
    'Brazil': 'pt_BR',
    'Chile': 'es_CL',
    'Colombia': 'es_CO',
    'Mexico': 'es_MX',
    
    # North America
    'Canada': 'en_CA',
    'United States': 'en_US'
}

def generate_username(first_name, last_name, existing_usernames):
    """Creates unique username with automatic numbering if base username exists"""
    base_username = f"{first_name[0].lower()}{last_name.lower().replace(' ', '').replace('-', '')}"
    if base_username not in existing_usernames:
        existing_usernames.add(base_username)
        return base_username
    
    counter = 1
    while True:
        new_username = f"{base_username}{counter}"
        if new_username not in existing_usernames:
            existing_usernames.add(new_username)
            return new_username
        counter += 1

def generate_hire_date():
    """Generates random hire date from last 10 years (date only, no time)"""
    today = date.today()
    start_date = today - timedelta(days=365 * 10)
    days_between = (today - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)

def get_custom_name(country):
    """Generates a name from custom lists"""
    names = CUSTOM_NAMES[country]
    first_name = random.choice(names['first'])
    last_name = random.choice(names['last'])
    return first_name, last_name

def create_manager_pool():
    """Creates a diverse pool of managers"""
    manager_pool = []
    
    # Add custom-named managers
    for country in CUSTOM_NAMES:
        for _ in range(2):
            first, last = get_custom_name(country)
            manager_pool.append(f"{first} {last}")
    
    # Add Faker-generated managers
    for locale in set(LOCALE_MAPPING.values()):
        faker = Faker(locale)
        for _ in range(1):
            manager_pool.append(faker.name())
    
    return manager_pool



def populate_users():
    """Main function to populate the database"""
    existing_usernames = set()
    manager_pool = create_manager_pool()
    

    with app.app_context():
        # Get existing usernames from database
        existing_db_usernames = set(user.username for user in User.query.all())
        existing_usernames.update(existing_db_usernames)
        
        # Handle countries with custom names
        for country in CUSTOM_NAMES.keys():
            print(f"Creating users for {country}...")
            for _ in range(10):  # 10 users per country
                first_name, last_name = get_custom_name(country)
                username = generate_username(first_name, last_name, existing_usernames)
                user = User(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    manager=random.choice(manager_pool),
                    country=country,
                    hire_date=generate_hire_date()
                )
                db.session.add(user)
                generate_password_hasshed(user)   
            db.session.commit()

        # Handle other countries using Faker
        for country, locale in LOCALE_MAPPING.items():
            print(f"Creating users for {country}...")
            faker = Faker(locale)
            for _ in range(10):  # 10 users per country
                first_name = faker.first_name()
                last_name = faker.last_name()
                username = generate_username(first_name, last_name, existing_usernames)
                user = User(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    manager=random.choice(manager_pool),
                    country=country,
                    hire_date=generate_hire_date()
                )
                db.session.add(user)
                generate_password_hasshed(user)
            db.session.commit()
        
        print("Database populated successfully!")




if __name__ == "__main__":

    populate_users()
    