# Technical Challenge

For this project, you'll be using a publically available data source of schools in a CSV format. You'll download the data file and write a web service that can manipulate the data.

I expect this challenge to take approximately 2 hours to complete. If you believe it will take significantly longer, please reach out before proceeding to ensure you are not over-engineering the solution.

You may use any programming language or framework of your choice. Your solution will be evaluated based on clarity, correctness, performance, and the originality of your approach.

**You are encouraged to use AI tools to assist you.** However, you may not use any external search or full-text search libraries. The search functionality must be implemented by you, including tokenization, ranking, and scoring logic.

## Part 0: Get the data
- Go to this page [https://nces.ed.gov/ccd/CCDLocaleCode.asp] and download the datasets described as :
  
- Year 2005-2006 (v.1b), States A-I, ZIP (769 KB) CSV File [https://nces.ed.gov/ccd/data/zip/sl051bai_csv.zip].
- Year 2005-2006 (v.1b), States K-N, ZIP (769 KB) CSV File [https://nces.ed.gov/ccd/data/zip/sl051bkn_csv.zip].
- Year 2005-2006 (v.1b), States O-W, ZIP (769 KB) CSV File [https://nces.ed.gov/ccd/data/zip/sl051bow_csv.zip].
- Unzip the files, and merge them together into one file, rename it to school_data.csv, and put it in the directory named seed where you'll write your API.

***Important Considerations:***
- Please double check the urls since they could be broken.
- This is the only file used for the tests cases shown [Year 2005-2006 (v.1b), States A-I, ZIP (769 KB) CSV File]. [https://nces.ed.gov/ccd/pdf/sl051bgen.pdf]
- You may also find it helpful to consult the documentation for this dataset.

Now you have the data you need to get started.

## Part 1: Load data from CSV and compute stats.
- Create an API that should load the data at startup. 
- Populating a DB (please use something like SQLite or any in memory DB).
- Create a controller that allows a CRUD operations for reloading or reseting the dataset.
- Also a controller for cleaning and reading the data.

### Guidelines
- Create a controller that allows CRUD operations to that dataset. 
- Don't over complicate the project by creating more than one entity for it.
- It's ok to have only one entity defined by the definition of the CSV file.
- The JSON response is valid.

  
## Part 2: Define your search algorithm
### Guidelines
- Use any algorithm you want to the search but you can't use a library that already does the implementation.
- Do not use full-text search engines or fuzzy-search libraries (e.g., Elasticsearch/Lucene, SQLite FTS, Whoosh, RapidFuzz/FuzzyWuzzy, etc.). You must implement tokenization + ranking yourself.
- Create a diagram that illustrates the selected search algorithm.
You may use any format, but it must be a visual/graphic representation (e.g., UML, state diagram, flowchart, etc.).
**You are encouraged to use AI tools to generate the diagram.**

## Part 3: Search over school data
We'd like teachers to be able to easily find the school they teach at. In order to do this, we'd like to offer a search feature that lets them search for their school using plain text.

This feature should search over school name, city name, and state name.
The top 3 matching results should be returned (see below for examples).

### Guidelines
- When a query doesn't match exactly, you'll need to come up with a set of rules to rank results. 
In particular, make sure more precise matches show up at the top of the list, and if there isn't an exact match, but there is a close match, some results are returned. There is no perfect set of rules, but you should come up with a set that improves the end user search experience as much as possible.
- Searches should run in real-time, meaning that they should return results to the user in less than 5ms. It's ok to perform data loading and processing up front that takes longer than this if you'd like.
- Create an endpoint search that receives a parameter called query. And write a method that performs the search.

## Evaluation

### Accuracy
- We'll evaluate the accuracy of your search using sample queries. We have included a few below in Test Cases that you can test with (we'll also test with others).
- The following queries should return the results shown below as the top hits. If multiple results are shown below, it doesn't matter if one appears before the other, but they must be the first results returned.
- If you see [Next Best Hit], that means that you should include a reasonable hit for the search query, but that there isn't a specific hit that we'll be looking for.

### Performance
- Search results should ideally be returned within 5ms (server-side search time). Slightly longer response times are acceptable.
- ***Extra Credit: All search results are returned in under 1ms.***

### Code Quality
We're looking for clear, easy to understand code. 
- Write code that makes your thinking algorithm as obvious as possible.
- Prioritize readability over cleverness.
- We care less that you can code a solution to this problem in one line, and more that we are able to easily follow your code.
- Don't worry about documentation for this project. Do your best to make the code readable without requiring reading lots of documentation.

## Test Cases
elementary school highland park
>>> school_search.search_schools("elementary school highland park")
Results for "elementary school highland park" (search took: 0.009s)
1. HIGHLAND PARK ELEMENTARY SCHOOL
MUSCLE SHOALS, AL
2. HIGHLAND PARK ELEMENTARY SCHOOL
PUEBLO, CO
3. [Next Best Hit]

jefferson belleville
>>> school_search.search_schools("jefferson belleville")
Results for "jefferson belleville" (search took: 0.000s)
1. JEFFERSON ELEM SCHOOL
BELLEVILLE, IL
2. [Next Best Hit]
3. [Next Best Hit]

riverside school 44
>>> school_search.search_schools("riverside school 44")
Results for "riverside school 44" (search took: 0.002s)
1. RIVERSIDE SCHOOL 44
INDIANAPOLIS, IN
2. [Next Best Hit]
3. [Next Best Hit]

granada charter school
>>> school_search.search_schools("granada charter school")
Results for "granada charter school" (search took: 0.001s)
1. NORTH VALLEY CHARTER ACADEMY
GRANADA HILLS, CA
2. GRANADA HILLS CHARTER HIGH
GRANADA HILLS, CA
3. [Next Best Hit]

foley high alabama
>>> school_search.search_schools("foley high alabama")
Results for "foley high alabama" (search took: 0.001s)
1. FOLEY HIGH SCHOOL
FOLEY, AL
2. [Next Best Hit]
3. [Next Best Hit]

KUSKOKWIM
>>> school_search.search_schools("KUSKOKWIM")
Results for "KUSKOKWIM" (search took: 0.001s)
1. TOP OF THE KUSKOKWIM SCHOOL
NIKOLAI, AK
(No additional results should be returned)
