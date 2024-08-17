tasks = [
  {
    "name": "Draw Stairs",
    "description": "Create a function that draws stairs",
    "tests": [
      [[1], "I"],
      [[3], "I\n I\n  I"],
      [[5], "I\n I\n  I\n   I\n    I"]
    ]
  },
  {
    "name": "Fibonacci Sequence",
    "description": "Write a function that generates the Fibonacci sequence up to n numbers",
    "tests": [
      [[5], [0, 1, 1, 2, 3]],
      [[8], [0, 1, 1, 2, 3, 5, 8, 13]]
    ]
  },
  {
    "name": "FizzBuzz",
    "description": "Write a function that returns 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, and 'FizzBuzz' for multiples of both",
    "tests": [
      [[3], "Fizz"],
      [[5], "Buzz"],
      [[15], "FizzBuzz"],
      [[7], "7"]
    ]
  },
  {
    "name": "Reverse String",
    "description": "Create a function that reverses a given string",
    "tests": [
      [["hello"], "olleh"],
      [["Codewars"], "srawedoC"],
      [["racecar"], "racecar"]
    ]
  },
  {
    "name": "Sum of Digits",
    "description": "Write a function that calculates the sum of digits in a given number",
    "tests": [
      [[123], 6],
      [[456], 15],
      [[1000], 1]
    ]
  },
  {
    "name": "Palindrome Check",
    "description": "Create a function that checks if a given string is a palindrome",
    "tests": [
      [["racecar"], True],
      [["hello"], False],
      [["A man a plan a canal Panama"], True]
    ]
  },
  {
    "name": "Count Vowels",
    "description": "Write a function that counts the number of vowels in a given string",
    "tests": [
      [["hello"], 2],
      [["aeiou"], 5],
      [["rhythm"], 0]
    ]
  },
  {
    "name": "Prime Number Check",
    "description": "Create a function that determines if a given number is prime",
    "tests": [
      [[7], True],
      [[4], False],
      [[29], True]
    ]
  },
  {
    "name": "Capitalize Words",
    "description": "Write a function that capitalizes the first letter of each word in a sentence",
    "tests": [
      [["hello world"], "Hello World"],
      [["the quick brown fox"], "The Quick Brown Fox"]
    ]
  },
  {
    "name": "Array Rotation",
    "description": "Create a function that rotates an array by a given number of positions",
    "tests": [
      [[[1, 2, 3, 4, 5], 2], [4, 5, 1, 2, 3]],
      [[[1, 2, 3], 1], [3, 1, 2]]
    ]
  },
  {
    "name": "Anagram Check",
    "description": "Write a function that checks if two strings are anagrams of each other",
    "tests": [
      [["listen", "silent"], True],
      [["hello", "world"], False]
    ]
  },
  {
    "name": "Factorial",
    "description": "Create a function that calculates the factorial of a given number",
    "tests": [
      [[5], 120],
      [[0], 1],
      [[10], 3628800]
    ]
  },
  {
    "name": "Binary to Decimal",
    "description": "Write a function that converts a binary number to decimal",
    "tests": [
      [["1010"], 10],
      [["1100"], 12],
      [["1111"], 15]
    ]
  },
  {
    "name": "Longest Word",
    "description": "Create a function that finds the longest word in a sentence",
    "tests": [
      [["The quick brown fox jumped over the lazy dog"], "jumped"],
      [["Hello world"], "Hello"]
    ]
  },
  {
    "name": "Remove Duplicates",
    "description": "Write a function that removes duplicate elements from an array",
    "tests": [
      [[[1, 2, 2, 3, 4, 4, 5]], [1, 2, 3, 4, 5]],
      [["aabbccdd"], "abcd"]
    ]
  },
  {
    "name": "Caesar Cipher",
    "description": "Create a function that implements a Caesar cipher with a given shift",
    "tests": [
      [["hello", 3], "khoor"],
      [["abc", 1], "bcd"],
      [["xyz", 3], "abc"]
    ]
  },
  {
    "name": "Find Missing Number",
    "description": "Write a function that finds the missing number in a sequence of integers",
    "tests": [
      [[[1, 2, 4, 5, 6]], 3],
      [[[1, 3, 4, 5]], 2]
    ]
  },
  {
    "name": "Perfect Square Check",
    "description": "Create a function that determines if a given number is a perfect square",
    "tests": [
      [[16], True],
      [[25], True],
      [[14], False]
    ]
  },
  {
    "name": "Title Case",
    "description": "Write a function that converts a string to title case",
    "tests": [
      [["the quick brown fox"], "The Quick Brown Fox"],
      [["a clash of KINGS"], "A Clash of Kings"]
    ]
  },
  {
    "name": "Leap Year Check",
    "description": "Create a function that determines if a given year is a leap year",
    "tests": [
      [[2000], True],
      [[2100], False],
      [[2024], True]
    ]
  },
  {
    "name": "Array Intersection",
    "description": "Write a function that finds the intersection of two arrays",
    "tests": [
      [[[1, 2, 3, 4], [3, 4, 5, 6]], [3, 4]],
      [[[1, 2, 3], [4, 5, 6]], []]
    ]
  },
  {
    "name": "Morse Code Translator",
    "description": "Create a function that translates a string to Morse code",
    "tests": [
      [["SOS"], "... --- ..."],
      [["HELLO"], ".... . .-.. .-.. ---"]
    ]
  },
  {
    "name": "Roman to Integer",
    "description": "Write a function that converts a Roman numeral to an integer",
    "tests": [
      [["IV"], 4],
      [["IX"], 9],
      [["LVIII"], 58]
    ]
  },
  {
    "name": "Word Frequency",
    "description": "Create a function that counts the frequency of words in a sentence",
    "tests": [
      [["the quick brown fox jumps over the lazy dog"], {"the": 2, "quick": 1, "brown": 1, "fox": 1, "jumps": 1, "over": 1, "lazy": 1, "dog": 1}],
      [["hello world hello"], {"hello": 2, "world": 1}]
    ]
  },
  {
    "name": "Pascal's Triangle",
    "description": "Write a function that generates the nth row of Pascal's triangle",
    "tests": [
      [[4], [1, 4, 6, 4, 1]],
      [[1], [1]],
      [[3], [1, 3, 3, 1]]
    ]
  }
]