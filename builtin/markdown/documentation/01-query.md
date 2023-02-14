### Gotchas

Up to 4 queries can be made at a time using semicolons:
  `UN; EU; SDG; WFP`

Overly generic queries may break things:
    querying `the` exceeds retrieval limits in large corpora

Abbreviations can be tricky with case insensitive searches:
    `UN` includes `un` - a common word in some languages

Searches can include some punctuation:
    `U.N.` works but `;` is prohibited;

Most punctuation requires a space in between words:
    `end of sentence .` (try both with/without spaces to be sure)

Possessives can also require a space in between words:
    use both `<word>'s` and `<word> 's` to retrieve all cases,
    e.g., `UN's | UN 's` or `United Nations' | United Nations '`

Lemmatization (word forms) isn't always intuitive:
    `person` includes `persons` but not `people`;
    `localize` doesn't include `localise` and vice versa
