# Approach and Thought-Process:

## Iteration 1:

* It is a counting problem with results in particular order.

* Best suited data structure will be dictionary.

* occupations_dictionary = { SOC_name: counts } and states_dictionary = {State: counts}.

**My code was wrong, data parsing failed** 

### Change in approach resulting in,

## Iteration 2:

* Debugged issue and found data format is incorrect for few records.

* Few records have separator tokens in between the text of a single column.

* Accommodated logic to recover those few records and parse correctly -- `The double quotation pattern`.

* I understood my custom parsing function would decrease performance greatly as it is written in python as opposed to the python built-in function written in C. So I applied my function only to the records that fails the default parsing.

All good so far. Now how to improve my solution keeping accuracy-runtime tradeoff in mind?

**SOC_name column data are not so clean, handling them would result in more accurate counts!**

### Change in approach resulting in,

## Iteration 3:

* Incorporated logic to clean `SOC_name` column data.

* Checked performance, still good!

Again, how could I further improve my solution?

**SOC_name has different strings even though they intuitively mean the same ('R&D' == 'R&AMP;D')**

### **Major Change in approach resulting in,**

## Iteration 4:

* Hmm, `SOC_name` column is **not unique enough.**

* Use `SOC_code` column instead!

* Change in data structure. Maintain dictionary with key `SOC_code` and value as a dictionary with key `SOC_name` and value as `counts`.

* Reducing the inner dictionary - Pick `SOC_name` with highest counts and `counts` as sum of `counts` of all `SOC_name` for a particular `SOC_code`.

* *Assumption - Only a fraction of total data will have simple errors (spelling errors, noun forms) which implies name with highest counts is correct name.*

Wow! more accurate counts with acceptable run time.

But, *My code was wrong!*, **`SOC_code` does not have clean data**.

Change in approach resulting in,

## Iteration 5:

* Incorporated logic to clean `SOC_code` column data.

* checked performance, acceptable!


# Points of Optimization:

* We need only the counts of **certified jobs**, *so filter before any computation*. `Analogy is basic principle in SQL to filter before join.`

* Applying my custom data parsing function to every record would be inefficient. So I applied the custom data parsing function to only the records that were inconsistent with the schema.

* I know I would need data only from few columns for my computation. So, Instead of understanding each column, I captured the information of what is necessary.

* There is no point in inserting missing values into the dictionary. So again, **filter!**.

* I found scope to improve accuracy in counts when cleaning columns and using SOC code as keys.

# Enhancement ideas after time-out:

### Logging functionality:

    I had the idea of developing the logging functionality which would make debugging easier.

### Unit Tests:
Nathan's presentation on design principles where he talks about the input space we expect and the actual input space that arrives in production made much more sense when I had to clean the column data.
So my next enhancement would be testing.

### Distributed Environment:
    To improve scalability, this solution has to be deployed in a distributed environment.
