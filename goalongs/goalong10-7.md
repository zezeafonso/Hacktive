# Daily Report

## Goals
To implement correctly our idea to improve the code

### updated Goals
To implement for each method the check if the arguments were already used.
Gather ideas to solve the problem of too much updates. 

### IDEAS

I don't think we need threads for now. Maybe we can just use a single thread and use a visitor *set* that is passed through the functions, whenever we want to call these check_for_state_updates it goes inside the set the function, this way we never have duplicates. 
At the end of the update we can simply call the functions that are inside the set. Until the set is empty. The set is also passed down to those functions. 

### IDEAS for tommorrow

Change the methods and network components updater to receive the context, the context should reference the objects. And not the just the names. Despite this, the methods that were used for it, will be used because when we filter objects from the outputs we receive only the names so we always need these functions that do operations depending on the names and not objects.

## Work
I did the methods to check if the arguments were already used
And I improved the way we were checking if the context had the required values.

