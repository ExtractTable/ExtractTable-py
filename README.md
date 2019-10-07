[![image](https://i.imgur.com/YIHmXue.png?1)](https://extracttable.com?ref=github-ET)

**Latest verions: 1.0.1** [![image](https://img.shields.io/github/license/ExtractTable/ExtractTable-py)]() [![image](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue)]()  
  
# Overview
[ExtractTable](https://extracttable.com) - **API to extract tabular data from images and scanned PDFs**

The motivation is to make it easy for developers to extract tabular data from images or scanned PDF files without worrying about the table area, column coordinates, rotation et al.

# Prerequisite

Before we talk/boast about the service, a developer MUST need an API key to use the ExtractTable service. [FREE credits here](https://extracttable.com/trail.html). 

We beat this market **not just in accuracy also in cost, and expiration**. You are most welcomed to [BUY credits here](https://extracttable.com/#pricing) or email me at saradhi@extracttable.com for assistance.


# Installation

`pip install -U ExtractTable`


# Basic Usage
Ok, enough selling. Let the ease in coding do the talk, and the output encourages you to buy credits - put that timer on and count the LOC.

```python
from ExtractTable import *
et_sess = ExtractTable(api_key=YOUR_API_KEY)        # Replace your VALID API Key here
print(et_sess.check_usage())        # Checks the API Key validity as well as shows associated plan usage 
table_data = et_sess.process_file(filepath=Location_of_Image_with_Tables, output_format="df")
```
[Detail Code Here](ExampleCode.ipynb)


### Woahh, as simple as that ?!

Certainly. Do you know the current ExtractTable users use it on
- Bank Statement
- Medical Records
- Invoice Details
- Tax forms

Its up to you now to explore the ways.


# Explore
**Whatelse** is in the store.
- `ExtractTable._OUTPUT` - check the list of **available output formats**
- `et_sess.ServerResponse.json()` - check the latest Actual **ServerResponse** attached to the session


## Pull Requests & Rewards

Pull requests are most welcome and greatly appreciated. 


## License  
  
This project is licensed under the GNU-3.0 License, see the [LICENSE](https://github.com/extracttable/camelotpro/blob/master/LICENSE) file for details.
