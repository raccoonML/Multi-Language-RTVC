"""
==========
Person Bio
==========
Simply and short description of the module's purpose,
in this case the intial characterization of a person.

@see <link_to_relevant_page>
"""

# Author: Sven Eschlbeck <sven.eschlbeck@t-online.de>
# License: MIT

# Simple person-creating class
class Person:
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
