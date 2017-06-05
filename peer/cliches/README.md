# Advanced Exam Component

*This exam component is optional -- for those whom feel the component "google-words" is just not enough to demonstrate their own mastery of Python.*

## Objective

Write a Python script that will search a given text string for specific phrases that have become cliche.

A *cliche* is: a phrase or opinion that is overused and betrays a lack of original thought.

I have provided a basic framework with some components missing that you can build from.

Your objective is to write this script so it can be called from another module using the *import* command.

## Constraints

* All components that should have docstrings **must** have docstrings
* A "main" function from your script must be callable from another module
* DRY: Do not repeat yourself
* Keep everything modular: for example, instead of the list of cliches being a variable, consider making it what's returned from a function.
* More in discussion.

## Code Sample

```
# -*- coding: utf-8 -*-

"""
Identify cliches in writing.

Given a very long string of prose as an argument to a function, look
for cliches matched from a list of 681 common cliches. Return the number
of cliches found in the text; return a list of the cliches found in the
text.

.. todo:
    * remember to make the search case insensitive or find a similar
solution.
    * make a main function
    * put the list inside a function
    * this is a prototype
    * the function must be callable from another module
    * all elements that require docstrings must have docstrings
"""

cliches = [
    'a chip off the old block',
    'a clean slate',
    'a dark and stormy night',
    'a far cry',
    'a fine kettle of fish',
    'a good/kind soul',
    'a loose cannon',
    'a pain in the neck/butt',
    'a penny saved is a penny earned',
    'a tough row to hoe',
    'a word to the wise',
    'ace in the hole',

    ...
]

def main(listOfPhrases, text_to_check)
    """
    Provide a count of cliches in a text; provide a list of them.


    Params:
		list of phrases (list)
		text_to_check (string)

    Returns:
		count (str)
		list

    """


if __name__ == "__main__":
    main()
```
