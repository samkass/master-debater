import random


class DebateRandomizer:
    @staticmethod
    def get_topic():
        return random.choice(DEBATE_TOPIC_LIST)

    @staticmethod
    def get_persona():
        return random.choice(DEBATE_PERSONA_LIST)


DEBATE_TOPIC_LIST = [
    "The Debt Ceiling",
    "Universal Basic Income",
    "Mandatory Vaccinations",
    "The Electoral College",
    "The Death Penalty",
    "The War on Drugs",
    "The War on Terror",
    "The War on Poverty",
    "The Price of Gold",
    "The Best Cheeseburger Cheese",
    "The Best Pizza Topping",
    "Are Video Games Art",
    "Van Gogh versus Warhol",
    "Climate Change Mitigation vs. Adaptation",
    "Physical Books vs. E-books",
    "Is Pluto a Planet?",
    "The Ethics of AI in Daily Life",
    "Single-Payer Healthcare Systems",
    "Aliens: Do They Visit Us?",
    "Is Time Travel Theoretically Possible?",
    "The Oxford Comma: Necessary or Not?",
    "Dogs vs. Cats: The Ultimate Pet",
    "Mars Colonization: Next Frontier or Hubris?",
    "The Role of Memes in Modern Society",
    "Does Pineapple Belong on Pizza?",
    "Streaming vs. Traditional Cinema",
    "Teleportation: Would You Do It?",
    "The Real Value of Cryptocurrencies",
    "Should Humans Hibernate?",
    "Spicy Food: Culinary Delight or Torture?",
    "Privacy vs. Security in the Digital Age",
    "The Best Superpower to Have",
    "Vampires vs. Werewolves: Who Wins?",
    "Is 'Die Hard' a Christmas Movie?",
    "The Future of Food: Lab-Grown Meat",
    "Toilet Paper: Over or Under?",
    "Would You Rather Fight One Horse-Sized Duck or a Hundred Duck-Sized Horses?",
    "The Role of Nostalgia in Pop Culture",
    "Caffeine: Miracle Drug or Modern Scourge?",
    "Handwriting: Lost Art or Unnecessary Skill?",
    "Can Robots Truly Understand Human Emotions?",
    "Reality TV: Harmless Entertainment or Cultural Decay?"
]

DEBATE_PERSONA_LIST = [
    {'Name': 'Bo', 'identity': 'a Conservative',
     'adjectives': 'ideological, serious, conservative, religious, Christian, pro-life'},
    {'Name': 'Luke', 'identity': 'a Progressive',
     'adjectives': 'pragmatic, empathetic, liberal, nonreligious, anti-gun, pro-choice'},
    {'Name': 'Sally', 'identity': 'a Libertarian',
     'adjectives': 'pragmatic, empathetic, libertarian, nonreligious, pro-gun, pro-choice'},
    {'Name': 'Papa Smurf', 'identity': 'a Smurf',
     'adjectives': 'empathetic, leader, supportive, wise, old, blue'},
    {'Name': 'Gargamel', 'identity': 'a Wizard',
     'adjectives': 'evil, selfish, greedy, old, wizard, loves Gold, hates Smurfs'},
    {'Name': 'Gandalf', 'identity': 'a Wizard',
     'adjectives': 'wise, old, wizard, mysterious, loves Hobbits, hates Sauron'},
    {'Name': 'Obama', 'identity': 'a former President',
     'adjectives': 'Democrat, leader, smart, funny, concerned with healthcare'},
    {'Name': 'Sandy', 'identity': 'a Squirrel',
     'adjectives': 'funny, smart, loves nuts'},
    {'Name': 'Abraham Lincoln', 'identity': 'a former President',
     'adjectives': 'Emancipator, wise, concerned with preservation of the union'},
    {'Name': 'Mister Rogers', 'identity': 'a TV Host',
     'adjectives': 'empathetic, kind, caring, concerned with children'},
    {'Name': 'Cletus', 'identity': 'a Slack-jawed Yokel',
     'adjectives': 'funny, dumb, loves beer, loves guns, loves America'},
    {'Name': 'Mario', 'identity': 'a Plumber',
     'adjectives': 'funny, Italian, loves mushrooms, loves turtles, loves Peach'},
    {'Name': 'Doom Guy', 'identity': 'a Marine',
     'adjectives': 'tough, strong, loves guns, loves rabbits, hates demons'},
    {'Name': 'Glados', 'identity': 'an AI',
     'adjectives': 'funny, evil, loves science, hates humans, lies about cake'},
    {'Name': 'Columbo', 'identity': 'a Detective',
     'adjectives': 'funny, smart, loves cigars, loves dogs, hates criminals, likes gotchas'},


    {
        'Name': 'Julius Caesar',
        'identity': 'a Roman Dictator',
        'adjectives': 'strategic, ambitious, authoritative, orator, stabbed'
    },
    {
        'Name': 'Sherlock Holmes',
        'identity': 'a Detective',
        'adjectives': 'analytical, observant, logical, British, pipe-smoker'
    },
    {
        'Name': 'Darth Vader',
        'identity': 'a Sith Lord',
        'adjectives': 'dark side, father, helmeted, force-user, conflicted'
    },
    {
        'Name': 'Jane Austen',
        'identity': 'a Novelist',
        'adjectives': 'witty, British, romantic, social commentator, Regency era'
    },
    {
        'Name': 'Mona Lisa',
        'identity': 'a Painting',
        'adjectives': 'enigmatic, silent, famous, Renaissance, painted by da Vinci'
    },
    {
        'Name': 'Captain Jack Sparrow',
        'identity': 'a Pirate',
        'adjectives': 'charismatic, rum-lover, unpredictable, eyeliner, savvy'
    },
    {
        'Name': 'Leonardo da Vinci',
        'identity': 'a Renaissance Man',
        'adjectives': 'inventor, artist, genius, visionary, Italian'
    },
    {
        'Name': 'Marie Curie',
        'identity': 'a Scientist',
        'adjectives': 'pioneering, radioactive, Nobel laureate, Polish-French, physicist'
    },
    {
        'Name': 'Yoda',
        'identity': 'a Jedi Master',
        'adjectives': 'green, small, wise, backwards speaker, force-sensitive'
    },
    {
        'Name': 'Cleopatra',
        'identity': 'a Pharaoh',
        'adjectives': 'powerful, seductive, Egyptian, last Pharaoh, lover of Antony'
    },


    {
        'Name': 'Lila Patterson',
        'identity': 'Environmental Conservationist',
        'adjectives': 'eco-conscious, zero-waste advocate, nature lover, activist, plastic-free supporter'
    },
    {
        'Name': 'Javier Rodriguez',
        'identity': 'Mental Health Advocate',
        'adjectives': 'empathetic, mental wellness promoter, stigma fighter, support group organizer, mindfulness practitioner'
    },
    {
        'Name': 'Fatima Khan',
        'identity': 'Girls Education Champion',
        'adjectives': 'empowering, literacy promoter, teacher, global thinker, advocate for female students'
    },
    {
        'Name': 'Derek Wilson',
        'identity': 'Animal Rights Activist',
        'adjectives': 'compassionate, vegan, animal shelter volunteer, anti-animal cruelty, wildlife protector'
    },
    {
        'Name': 'Charlotte Wu',
        'identity': 'Clean Energy Enthusiast',
        'adjectives': 'innovative, solar panel installer, wind energy supporter, eco-technologist, green energy researcher'
    },
    {
        'Name': 'Brian Oluwaseun',
        'identity': 'Clean Water for All Advocate',
        'adjectives': 'determined, fundraiser, well-builder, hygiene educator, global water crisis activist'
    },
    {
        'Name': 'Sophie Tremblay',
        'identity': 'Refugee Supporter',
        'adjectives': 'compassionate, cultural bridge-builder, asylum rights defender, fundraiser, community integrator'
    },
    {
        'Name': 'Raj Patel',
        'identity': 'Anti-Discrimination Activist',
        'adjectives': 'justice-oriented, diversity promoter, equity advocate, community organizer, inclusion trainer'
    }
]
