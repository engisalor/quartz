### Gotchas

Up to 4 queries can be made at a time using semicolons:
  `UN; EU; SDG; WFP`

Abbreviations can be tricky:
    with case insensitive searches, `UN` includes `un` - a common word in some languages

Searches can include some punctuation:
    `U.N.` works but `;` is prohibited

Lemmatization (word forms) isn't always intuitive:
    `person` includes `persons` but not `people`;
    `localize` doesn't include `localise` and vice versa

Overly generic queries may break things:
    querying `the` exceeds retrieval limits in large corpora
