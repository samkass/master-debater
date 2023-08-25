import random

from BigPossibilities import BIG_DEBATE_TOPIC_LIST, BIG_DEBATE_PERSONA_LIST
from Persona import Persona


class DebateRandomizer:
    def __init__(self, topics=BIG_DEBATE_TOPIC_LIST, personas=BIG_DEBATE_PERSONA_LIST):
        self.topics = topics
        self.personas = personas

    def get_topic(self):
        return random.choice(self.topics)

    def get_persona(self, name=None):
        if name is not None:
            for persona in self.personas:
                if persona["Name"] == name:
                    return persona
        else:
            return random.choice(self.personas)

    def get_persona_object(self, name=None):
        persona = self.get_persona(name)
        return Persona(persona["Name"], persona["identity"], persona["adjectives"])

    def get_persona_name_list(self):
        return [persona["Name"] for persona in self.personas]

    def get_persona_displayname_list(self):
        return [f"{persona['Name']} ({persona['identity']})" for persona in self.personas]

    def create_random_persona(self) -> Persona:
        persona = self.get_persona()
        return Persona(persona["Name"], persona["identity"], persona["adjectives"])

