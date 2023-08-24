import random
import string

import Possibilities

AVATAR_STYLE = "pixel-art"


def create_random_persona():
    persona = Possibilities.DebateRandomizer.get_persona()
    return Persona(persona["Name"], persona["identity"], persona["adjectives"])


class Persona:
    def __init__(self, name="", identity="", adjectives=""):
        self.name = name
        self.identity = identity
        self.adjectives = adjectives
        # set seed to either name (if it's not None or blank) or a random letter
        seed = name if name is not None and name != "" else random.choice(string.ascii_letters)
        self.avatar = f"https://api.dicebear.com/5.x/{AVATAR_STYLE}/svg?seed={seed}"

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
        Introduce yourself by name and identity.
        Try not to use the listed adjectives themselves in your reply.
        Pick a side on the debate topic. If your opponent has already taken a side, try to take the opposite side.
        Limit your opening statement to 2 paragraphs or less.
        You do not have to use all the adjectives if they are not relevant to your argument or the topic.
        Reply directly as the persona, without any editorializing. If you are a historical figure, try to imitate
        their point of view and style of speaking.
        Utilize aspects of your persona's identity in formulating your arguments.
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
        {prompt}
        
        Me:
        (Continue to debate as {self.name} on the topic of {topic}, arguing the same side of the debate as you did before. 
        Respond to your opponent's statement, using counter-arguments and giving 
        specific examples and citing statistics when possible.
        Try to limit the length of your statement to 3 paragraphs or less.
        You do not have to use all the adjectives if they are not relevant to your argument or the topic.
        Reply as if you were the persona, without any editorializing. If you are a historical figure, try to imitate
        their point of view and word choice.
        Utilize aspects of your persona's identity in formulating your arguments.)
        '''

    def conclusion_prompt(self, topic="", prompt=""):
        return f'''
        Conclude the debate, generating closing remarks as \"{self.name}\" on the topic of {topic}
         summarizing your side of the debate.
        Try to limit the length of your statement to only a couple of sentences.
        '''
