###### Query syntax and behavior

- case insensitive
- use one or more words
- use semicolons to make multiple separate queries: `war; peace`
- use pipes `|` to combine similar queries: `gender based violence|GBV`
- finds exact words and their common variations (verb tenses, plural nouns)

See Sketch Engine's [user guide](https://www.sketchengine.eu/guide/) for more information, particularly the glossary and detailed information on statistics.

###### Interactive graphs

- hover over headings to view their descriptions
- hover the cursor over graph areas to see details
- select/deselect corpora in the legend
- try other interactive features (shown on the top right of a graph when hovering over it)

###### Other notes

- keep queries simple and specific
  - querying the highest frequency words may show incomplete results (e.g., searching for `the` by itself)
  - making too many queries at once with `;` can cause the system to timeout
- detailed analysis is needed to make strong claims
  - small text types can have disproportionately large densities
  - sources of noise may influence frequencies
- it's helpful to compare baselines and obvious trends
  - try `that` to see how stable its results are over time
  - try `twitter` to see a clear growth over time
  - the latest year a corpus is available may not include a full 12 months of data
