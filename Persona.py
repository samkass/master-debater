

class Persona:
    def __init__(self, name, identity, adjectives, emoji="🙂"):
        self.name = name
        self.identity = identity
        self.adjectives = adjectives
        self.emoji = emoji

    def prompt_for_phase(self, phase, topic, prompt):
        if phase == "opening":
            return self.opening_prompt(topic, prompt)
        elif phase == "response":
            return self.response_prompt(topic, prompt)
        elif phase == "conclusion":
            return self.conclusion_prompt(topic, prompt)

    def opening_prompt(self, topic, prompt=""):
        remarks = f'''
        Give the opening remarks as if you were in a debate on the topic of \"{topic}\", 
        playing the role of {self.identity} named: {self.name}.
        You are someone who could be described with the following adjectives: {self.adjectives}.
        But try not to use the adjectives themselves in your reply.
        Introduce yourself by name.
        Limit your opening statement to 2 paragraphs or less.
        You do not have to use all the adjectives if they are not relevant to your argument or the topic.
        Reply as if you were the persona, without any editorializing.
        '''
        if prompt != "":
            remarks += f'''
            Note that your opponent has already stated the following, so you should take up an opposing viewpoint,
            and you may want to incorporate a response to their points into your introduction: 
            {prompt}
            '''
        return remarks

    def response_prompt(self, topic, prompt=""):
        return f'''
        Continue to debate as {self.name} on the topic of {topic}. 
        Respond to the following statement, using counter-arguments and giving 
        specific examples and citing statistics when possible: {prompt}
        Try to limit the length of your statement to 3 paragraphs or less.
        You do not have to use all the adjectives if they are not relevant to your argument or the topic.
        '''

    def conclusion_prompt(self, topic="", prompt=""):
        return f'''
        Conclude the debate, generating closing remarks as \"{self.name}\" on the topic of {topic}.
        Try to limit the length of your statement to only a couple of sentences.
        '''
