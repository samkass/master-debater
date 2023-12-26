import random
import string


class Persona:
    AVATAR_STYLE = "pixel-art"

    def __init__(self, name="", identity="", adjectives=""):
        self.name = name
        self.identity = identity
        self.adjectives = adjectives
        # set seed to either name (if it's not None or blank) or a random letter
        seed = name if name is not None and name != "" else random.choice(string.ascii_letters)
        self.avatar = f"https://api.dicebear.com/5.x/{Persona.AVATAR_STYLE}/svg?seed={seed}"

    def prompt_for_phase(self, phase, topic, opponent_prompt=""):
        if phase == "opening":
            return self.opening_prompt(topic, opponent_prompt)
        elif phase == "response":
            return self.response_prompt(topic, opponent_prompt)
        elif phase == "conclusion":
            return self.conclusion_prompt(topic, opponent_prompt)

    def opening_prompt(self, topic, prompt=""):
        remarks = ""
        if prompt != "":
            remarks += f'''
            {prompt}
            '''
        else:
            remarks += f'''
            (Moderator note: Your opponent has not yet made a statement, as you will be the first to speak in this debate.)
            '''
        remarks += f'''
        
Moderator: (Now give the opening remarks as if you were in a debate and taking the opposite viewpoint as your opponent
        on the topic of \"{topic}\", playing the role of {self.identity} named: {self.name}.
        You are someone who could be described with the following adjectives: {self.adjectives}.
        Start by introducing yourself by name and identity.
        Try not to use the listed adjectives themselves in your reply.
        Pick a side on the debate topic. If your opponent has already taken a side, take the opposite side.
        Limit your opening statement to 2 paragraphs or less.
        You do not have to use all the adjectives if they are not relevant to your argument or the topic.
        Debate directly as the persona, without any editorializing. 
        Try to imitate the the point of view and style of speech of your assumed persona. Continue to do so for every sentence of the debate.
        Utilize aspects of your persona's identity in formulating your arguments.
        If there is a document in the prompt context above, use the numerical figures and facts within 
        the document as much as possible to support your arguments. But DO NOT mention "the document".)
        '''
        return remarks

    def response_prompt(self, topic, prompt=""):
        return f'''
        {prompt}
        
Moderator: (Continue to debate as {self.name} on the topic of {topic}, arguing the same side of the debate as you did before. 
        Respond to your opponent's statement, using counter-arguments and giving 
        specific examples and citing statistics when possible.
        Continue to respond as if you were {self.identity} named: {self.name}, described with the following adjectives: {self.adjectives}.
        Try to limit the length of your statement to 3 paragraphs or less.)
        '''

    def conclusion_prompt(self, topic="", prompt=""):
        return f'''
        {prompt}
        
Moderator: (Now conclude the debate, generating closing remarks as \"{self.name}\" on the topic of {topic}
         summarizing your points and concluding your chosen point of view.
        Try to limit the length of your statement to only a couple of sentences.)
        '''
