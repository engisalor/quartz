## User guide

#### Syntax

*How searches behave*

| | |
|-|-|
| One or more words | `united` or `united nations` |
| Case insensitive | `united nations` is the same as `United Nations` |
| Semicolons to compare several searches (each gets its own graph) | `united nations; european union` |
| Pipes `|` to search for `X` OR `Y` (combines both into one graph) | `United Nations Development Programme | UNDP` |
| Base verb forms retrieve multiple tenses | `unite` gets `united`, `unites`, `uniting`, ... |
| Singular nouns retrieve plural forms | `nation` gets `nations` |
| Single hyphens are space-friendly | `evidence-based` gets `evidence - based` |
| Double hyphens are more inclusive | `evidence--based` gets with/without hyphen/spaces |
| Question marks `?` for any character | `?ased` gets `based`, `eased`, `cased`, ... |
| Asterisks `*` for any combinations | `*ased` gets `based`, `increased`, `purchased`, ... |
| Asterisks `*` for any word | `evidence *` gets `evidence of`, `evidence shows`, ... |

#### Gotchas

*Things to keep in mind*

| | |
|-|-|
| Keep queries simple and specific | ... and take results with a grain of salt |
| Up to 4 queries can be made at a time using semicolons | `UN; EU; SDG; WFP` |
| Nothing appears if there are missing results | `UN; non_existent_word` won't work (try again with just `UN`) |
| Overly generic queries may break things | querying `the` exceeds retrieval limits in large corpora |
| Abbreviations can be tricky with case insensitive searches | `UN` includes `un` - a common word in some languages |
| Searches can include some punctuation | `U.N.` works but `;` is prohibited |
| Punctuation may need an extra space | `end of a sentence .` (try both with/without spaces to be sure) |
| Possessives may need a space in between | `UN's | UN 's`, `United Nations' | United Nations '` |
| Lemmatization (word forms) isn't always intuitive | `person` gets `persons` but not `people`, `localize` doesn't get `localise` and vice versa |

#### Settings

*Parameters to choose from*

| Data set | |
|-|-|
| [Corpus](/corpora) | A database of searchable texts. |
| Attribute | A type of metadata for each corpus (`year`, `author`, `id`, ...). If multiple corpora are selected, only comparable attributes appear. |
| Attribute value (aka text type) | An attribute (`year`) can have many values (`2000`, `2001`, ...): these can be filtered. Some attributes have many values and only a portion can be displayed. |

| Statistics | | |
|-|-|-|
| **frq** | Occurrences | How often a query occurs in a corpus |
| **rel** | Relative density % | How often a query appears in a text type compared to the whole corpus |
| **fpm** | Frequency per million | How often a query appears for every million words in a corpus |
| **reltt** | Relative density per million in text type | How often a query appears for every million words in a text type |

- See Sketch Engine's [user guide](https://www.sketchengine.eu/guide/) for more information on interpreting corpus data, particularly the glossary and details on statistics.

#### Multivalue attributes

While some attributes have a single unique value (e.g., timestamps), others can have several. A `theme` attribute could include a list of topics, like Food, Education, and Sanitation. This could be tagged in a corpus as a single string with a separator between values (`Food|Education|Sanitation`).

Multivalues can include repeated values, like `source.type` = `NGO|NGO`. In this case  two organizations of the same type are listed in another attribute: `source.name` = `UN Environment Programme|UN Office for the Coordination of Humanitarian Affairs`.

When frequencies are calculated for attributes with multivalues, a document is only counted once regardless of any repeated multivalues. If a corpus with one document has `source.type` = `NGO|NGO|NGO|IGO`, the total count for `NGO` documents is always `1`.

Multivalue attributes are unique to each corpus, if they include any.

#### Graphs

Graphs are made with [plotly](https://plotly.com/) and have interactive features:

- Hover over headings to view their descriptions
- Hover the cursor over graph areas to see details
- Select/deselect corpora in the legend
- Other features are shown on the top right of a graph when hovering over it
