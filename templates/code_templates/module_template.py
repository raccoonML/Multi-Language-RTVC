"""
Simply and short description of the module's purpose,
in this case the intial characterization of a person.
"""

class Person:
    """
    Short class description.
    """
    def __init__(self, name, age):
        """
        Receives name and age as
        parameters.
        """
        self.name = name
        self.age = age


p1 = Person("John", 36)

print(p1.name)
print(p1.age)
