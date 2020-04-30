[![image](https://i.imgur.com/2Hihfwwg.png)](https://extracttable.com?ref=github-ET)

[![image](https://img.shields.io/pypi/v/extracttable.svg?maxAge=3600)](https://pypi.org/project/extracttable/) ![image](https://img.shields.io/github/license/ExtractTable/ExtractTable-py) ![image](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue)
  
# Overview
[ExtractTable](https://extracttable.com) - **API to extract tabular data from images and scanned PDFs**

The motivation is to make it easy for developers to extract tabular data from images or scanned PDF files without worrying about the table area, column coordinates, rotation et al.

# Prerequisite

**API Key**: All requests to ExtractTable are authorized by an API Key. [FREE credits here](https://extracttable.com/signup/trial.html). The same API Key can also be used for conversions on the browser at [Web Pro](https://extracttable.com/pro.html).


# Installation

`pip install -U ExtractTable`


# Basic Usage
Ok, enough selling. Let the ease in coding do the talk, and the output encourages you to buy credits; put that timer on and count the LOC.


```python
from ExtractTable import ExtractTable
et_sess = ExtractTable(api_key=YOUR_API_KEY)        # Replace your VALID API Key here
print(et_sess.check_usage())        # Checks the API Key validity as well as shows associated plan usage 
table_data = et_sess.process_file(filepath=Location_of_Image_with_Tables, output_format="df")

# To process PDF, make use of pages ("1", "1,3-4", "all") params in the read_pdf function
table_data = et_sess.process_file(filepath=Location_of_PDF_with_Tables, output_format="df", pages="all")
```

## Detailed Library Usage
 [example-code.ipynb](example-code.ipynb)

<a href="https://colab.research.google.com/github/ExtractTable/ExtractTable-py/blob/master/example-code.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

### Woahh, as simple as that ?!

Certainly. Do you know the current ExtractTable users use it for
- Bank Statement
- Medical Records
- Invoice Details
- Tax forms
- Tender Notices

Its up to you now to explore the ways.


# Explore
check the complete server response of the latest job with `et_sess.ServerResponse.json()`
```json
{
    "JobStatus": <string>,                              # Status of the triggered Process  @ JOB-LEVEL
    "Pages": <integer>,                                 # Number of pages processed in this request @ PAGE-LEVEL
    "Tables": [<list of key-value objects of table>     # List of all tables found @ TABLE-LEVEL
        {
            "Page": <integer>,                              ## Page number in which this table is found
            "CharacterConfidence": <float>,                 ## Accuracy of Characters recognized from the input-page
            "LayoutConfidence": <float>,                    ## Accuracy of table layout's design decision
            "TableJson": <dict>,                            ## Table Cell Text in key-value format with index orientation - {row#: {col#: <str>}}
            "TableCoordinates": <dict>,                     ## Top-left & Bottom-right Cell Coordinates - {row#: {col#: <list(x1,y1,x2,y2)>}}
            "TableConfidence": <dict>                       ## Cell level accuracy of detected characters - {row#: {col#: <float>}}
        },
    {...}                                               ## ... more "Tables" objects
    ],
    "Lines": [<list of key-value objects>               # Pagewise Line details @ PAGE-LEVEL
        {
            "Page": <integer>,                          # Page number in which the lines are found
            "CharacterConfidence": <float>,             # Average Accuracy of all Characters recognized from the input-page
            "LinesArray": [
                <list of key-value objects of line>     # Ordered list of lines in this page @ LINE-LEVEL
                {
                    "Line": <str>,                          ## Detected text of the complete line
                    "WordsArray": [
                        <list of key-value objects>         ## Word level datails in this line @ WORD-LEVEL
                        {
                            "Conf": <float>,                    ### Accuracy of recognized characters of the word
                            "Word": <str>,                      ### Detected text of the word
                            "Loc": [x1, y1, x2, y2]             ### Top-left & Bottom-right coordinates, w.r.t the input-page width-height dimensions
                        },
                    {...}                                   ### More "WordsArray" objects
                    ]
                },
            {...}                                       ## More "LinesArray" objects
            ]
        },
    {...}                                               # More Pagewise "Lines" details
    ]
}
```

## Bug Reports
Bug reports/fixes are most welcome and greatly appreciated with API credits. For support reach us at pydevs@extracttable.com 


## License  
  
This project is licensed under the Apache License 2.0, see the [LICENSE](https://github.com/extracttable/ExtractTable-py/blob/master/LICENSE) file for details.


## Social Media
Follow us on Social media for library updates and free credits.

[![Image](https://cdn3.iconfinder.com/data/icons/socialnetworking/32/linkedin.png)](https://www.linkedin.com/company/extracttable)
&nbsp;&nbsp;&nbsp;&nbsp;
[![Image](https://abs.twimg.com/favicons/twitter.ico)](https://twitter.com/extracttable)
