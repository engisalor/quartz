### Gotchas

- up to 4 queries can be made at a time using semicolons:
  `UN; EU; SDG; WFP`
- abbreviations can be tricky:
    with case insensitive searches, `UN` includes `un` - a common word in some languages
- searches can include some punctuation:
    `U.N.` works but `;` is prohibited
- hyphenation is important:
  `UN-supported` doesn't include `UN supported` and vice versa
- understanding lemmatization (word forms) isn't always intuitive:
    `person` includes `persons` but not `people`
    `localize` doesn't include `localise` and vice versa
- overly generic queries may break:
    querying `the`, may retrieve partial results in large corpora
    this can occur when there are hundreds of millions of occurrences
