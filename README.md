# Technical Challenge

For this project, you'll be using a publically available data source of schools in a CSV format. You'll download the data file and write a web service that can manipulate the data.

I expect this challenge to take approximately 2 hours to complete. If you believe it will take significantly longer, please reach out before proceeding to ensure you are not over-engineering the solution.

You may use any programming language or framework of your choice. Your solution will be evaluated based on clarity, correctness, performance, and the originality of your approach.

**You are encouraged to use AI tools to assist you.** However, you may not use any external search or full-text search libraries. The search functionality must be implemented by you, including tokenization, ranking, and scoring logic.

## Part 0: Get the data
Go to this page [https://nces.ed.gov/ccd/CCDLocaleCode.asp] and download the datasets described as :
  
- Year 2005-2006 (v.1b), States A-I, ZIP (769 KB) CSV File [https://nces.ed.gov/ccd/data/zip/sl051bai_csv.zip].
- Year 2005-2006 (v.1b), States K-N, ZIP (769 KB) CSV File [https://nces.ed.gov/ccd/data/zip/sl051bkn_csv.zip].
- Year 2005-2006 (v.1b), States O-W, ZIP (769 KB) CSV File [https://nces.ed.gov/ccd/data/zip/sl051bow_csv.zip].

Unzip the files and merge them into a single CSV file. Rename the merged file to: *school_data.csv*. Place it inside a directory named: *seed* within your project.

***Important Considerations:***
- Please double check the urls since they could be broken.
- The sample test cases provided below reference only the States A–I dataset. [Year 2005-2006 (v.1b), States A-I, ZIP (769 KB) CSV File]. [https://nces.ed.gov/ccd/pdf/sl051bgen.pdf]
- You may also find it helpful to consult the documentation for this dataset.

Now you have the data you need to get started.

## Part 1: Load data from CSV and compute stats.
Build an API that:
- Loads the dataset at application startup.
- Populates a database (SQLite or an in-memory database is acceptable).
- Provides endpoints to reload or reset the dataset.
- Provides endpoints to clean and read the data.

### Guidelines
- Implement CRUD operations for the dataset.
- Don't over complicate the project by creating more than one entity for it.
- It's ok to have only one entity defined by the definition of the CSV file.
- All JSON responses must be valid.

  
## Part 2: Implement your search algorithm
Design and implement your own search algorithm.
### Requirements
- You may choose any search approach.
- You may **not** use full-text search engines or fuzzy-search libraries (e.g., Elasticsearch, Lucene, SQLite FTS, Whoosh, RapidFuzz, FuzzyWuzzy, etc.).
- You must implement tokenization and ranking logic yourself.
### Deliverables
- Implement the search algorithm in code.
- Provide a visual diagram illustrating your algorithm (UML, flowchart, state diagram, etc.).
**You are encouraged to use AI tools to generate the diagram based on your implemented code.** The diagram should accurately reflect your actual implementation and ranking logic.

## Part 3: Implement School Search
We'd like teachers to be able to easily find the school where they teach. To achieve this, we'd like to offer a search feature that allows them to search using plain text.

This feature should search over school name, city name, and state name.
The ***top 3*** matching results should be returned (see examples below).

### Guidelines
- When a query doesn't match exactly, you'll need to come up with a set of rules to rank results. 
In particular, make sure more precise matches show up at the top of the list, and if there isn't an exact match, but there is a close match, some results are returned. There is no perfect set of rules, but you should come up with a set that improves the end user search experience as much as possible.
- Searches should run in real time, meaning they should return results in ***less than 5ms***. It's okay to perform data loading and preprocessing upfront, even if that takes longer.
- Create an endpoint `/search` that receives a parameter called `query`, and write a method that performs the search.

## Evaluation

### Accuracy
- We'll evaluate the accuracy of your search using sample queries. We have included a few below in the Test Cases (we will also test with additional queries), but please note that ***these apply only to the first dataset***.
- The following queries should return the results shown below as the top hits. If multiple results are shown below, the order between them does not matter, but they must appear first.
- If you see [Next Best Hit], that means you should include a reasonable match for the query, but there isn't a specific result we expect.

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
