

class Persona:
    def __init__(self, name, identity, adjectives, emoji="🙂"):
        self.name = name
        self.identity = identity
        self.adjectives = adjectives
        self.emoji = emoji
        self.topic = ""

    def opening_prompt(self, topic, prompt=""):
        self.topic = topic
        remarks = f'''
        Give the opening remarks as if you were a {self.identity} named {self.name} in a debate on the topic of {topic}.
        Pretend to be someone who could be described as: {self.adjectives}
        '''
        if prompt != "":
            remarks += f'''
            Note that your opponent has already stated the following: {prompt}
            '''
        return remarks

    def response_prompt(self, prompt):
        return f'''
        Continue to debate as {self.name} on the topic of {self.topic}. 
        Respond to the following statement, using counter-arguments and giving 
        specific examples and citing statistics when possible: {prompt}
        '''

    def conclusion_prompt(self):
        return f'''
        Conclude the debate, generating closing remarks as {self.name} on the topic of {self.topic}.
        '''
