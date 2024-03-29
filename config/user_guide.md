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
| Nothing appears if a query has no results | `non_existent_word` |
| Overly generic queries may break things | querying `the` exceeds retrieval limits in large corpora |
| Abbreviations can be tricky with case insensitive searches | `UN` includes `un` - a common word in some languages |
| Searches can include punctuation | `U.N.` works but `;` is prohibited |
| Symbols may need an extra space | `end of a sentence .` (try both with/without spaces to be sure) |
| Possessives may need a space in between | `UN's | UN 's`, `United Nations' | United Nations '` |
| Lemmatization (word forms) isn't always intuitive | `person` gets `persons` but not `people`, `localize` doesn't get `localise` and vice versa |

#### Settings

*Parameters to select*

| Dataset | |
|-|-|
| Corpus | A database of searchable texts. |
| Attribute (aka text type) | A type of metadata for each corpus (`year`, `author`, `id`, ...). If multiple corpora are selected, only attributes defined as "comparable" appear. |
| Attribute value | An attribute (`year`) can have many values (`2000`, `2001`, ...): these can be filtered. Some attributes have many values and only a portion can be displayed. |

| Statistics | | |
|-|-|-|
| frq | Occurrences | How often a query occurs in a corpus |
| rel | Relative density % | How often a query occurs in a text type compared to the whole corpus |
| fpm | Frequency per million | How often a query occurs for every million words in a corpus |
| reltt | Relative density per million in text type | How often a query occurs for every million words in a text type |

| Sorting method* | |
|-|-|
| `frq` | Get results with the highest absolute frequency |
| `rel` | Get results with the highest relative frequency |

\*Sorting applies when an attribute has too many values to show at once (see below warning on limited sample sizes)

| Paging | |
|-|-|
| `1`, `2`, etc. | If an attribute has many values, only a portion can be graphed at once: change the page to see more results |

#### Interpreting data

##### The limits of statistics

This app visualizes frequencies and encourages data exploration. That said, numbers can't tell the whole story: reading source texts is essential for proper interpretation.

Keep in mind that statistics only allow certain types of comparisons. Since this app disaggregates data by text types, consider the following:

- **frq** is an absolute frequency: it doesn't show how *common* queries are relative to corpus size
- **rel** and **fpm** are best for comparing text types ***within*** a single corpus
- **reltt** can be used for comparing text types ***across*** corpora (i.e., why it's the default statistic)

See Sketch Engine's [user guide](https://www.sketchengine.eu/guide/) for more information on interpreting corpus data, particularly the glossary and details on statistics.

##### Limited sample size warning

Only the top N results are retrieved by default (usually 50 or 250) using the sort method (`absolute` or `relative`). If an attribute has N values or fewer, all available data are included in graph. This determines how data samples are collected and has big implications for data interpretation.

###### Example 1

Since the English ReliefWeb corpus has fewer than 50 years, `N<50` and all data is graphed when querying the year attribute. The sort method doesn't matter, since the sample size is the full dataset.

###### Example 2

Since the English ReliefWeb corpus has hundreds of countries, `N>50` and only the top 50 will be graphed based on the sort method:

- if sort is `absolute`, the 50 countries with the highest absolute frequency `frq` will be graphed
- if sort is `relative`, the 50 countries with the highest relative frequency `rel`/`reltt` will be graphed

Only a portion of the dataset can be graphed for the country attribute if there are results for over 50 countries. For instance, in the query `climate resilience`, Grenada has the 2nd highest **reltt** but the 56th highest **frq**. Yet Grenada won't be included when sort is `absolute` and 50 is the maximum number of values displayed.

To correctly interpret data, the sort method and sample size are key factors. The absence of one country (or other text type value) shouldn't be taken as definitive unless the sample size is large enough to include every possible value. The the order of values and which are included can vary according to these settings.

>Limiting the sample size (`N < ∞`) is needed since text types can have millions of values, which can't be graphed effectively with bar charts. Remember: this app explores as much data as possible, but not necessarily everything all at once.

#### Multivalue attributes

While some attributes have a single unique value (e.g., timestamps), others can have several. A `theme` attribute could include a list of topics, like Food, Education, and Sanitation. This could be tagged in a corpus as a single string with a separator between values (`Food|Education|Sanitation`).

Multivalues can include repeated values, like `source.type` = `NGO|NGO`. In this case two organizations of the same type are listed in a related attribute: `source.name` = `UN Environment Programme|UN Office for the Coordination of Humanitarian Affairs`.

When frequencies are calculated for attributes with multivalues, a document is only counted once regardless of any repeated multivalues. If a corpus with one document has `source.type` = `NGO|NGO|NGO|IGO`, the total count for `NGO` documents is always `1`.

Multivalue attributes are unique to each corpus, if they include any.

#### Graphs

Graphs are made with [plotly](https://plotly.com/) and have interactive features:

- Hover over headings to view their descriptions
- Hover the cursor over graph areas to see details
- Select/deselect corpora in the legend
- Other features are shown on the top right of a graph when hovering over it

#### Summary table

The summary table can be shown/hidden with the spreadsheet icon next to the `settings` button.

| Column | Description |
|-|-|
| query | Query as written in the `search` bar |
| cql | CQL representation of the query |
| corpus | Current corpus |
| attribute | Current attribute |
| n attr. | Number of text types collected: if many exist, only the top `N` are shown to prevent the app from freezing |
| frq corp. | Occurrences in the whole corpus: the absolute number of times a query appears|
| frq attr. | Sum of occurrences in each attribute: when an attribute is single-value, the sum of all occurrences across text types generally equals `frq. corp.`; when an attribute is multivalue, this can exceed `freq. corp.` (because an occurrence can be shared by multiple text types) |
| fpm corp. | Frequency per million tokens in the whole corpus |
| M rel % | Mean relative density in text types |
| M reltt | Mean relative density per million in text types |
| M fpm | Mean frequency per million in text types |
| M frq | Mean occurrences in text types |

#### Hyperlinks to concordances

Click a data point on a graph to generate a URL to query concordances. Then click the link icon on the top right of the graph to open a new tab. Multiple links are generated if a data point has several corpora: they're color-coded for easy reference.

#### Crossfilters

First, select a crossfilter attribute in `settings` and then select a data point from a graph. This generates another graph with frequencies for the crossfilter attribute within the main attribute, e.g., the frequency by `year` of `United Nations` in `country=Guatemala`. Selected crossfilter data points don't get saved when a query URL is copied. To disable the crossfilter, select `disable crossfilter` (the first crossfilter option).

#### Attribute filter

Display or hide attribute values with the `attributes filter` option in `settings`. Keep in mind that not all values appear if an attribute has many values and that values with zero occurrences may not be displayed in graphs. These filters don't apply to crossfilter graphs.

#### Advanced queries

*For custom search behaviors*

Queries can also be written in [Corpus Query Language](https://www.sketchengine.eu/documentation/corpus-querying/). In this case, start a query with `q,` and then write the CQL string. Semicolons are still reserved for graphing several queries at once. Prior experience with CQL is advised: ***proceed with caution***.

| Query type | Example |
|-|-|
| Case-sensitive | `q,[word="United"][word="Nations"]|[word="UN"]` (gets these exact patterns) |
| Part-of-speech | `q,[lemma="disaster"][tag="V.*"]` (gets `disasters strike`, `disaster was`, ...) |
| Several CQL searches | `q,[word="UN"]; q,[word="EU"]` |
| Mix of simple and CQL searches | `q,[word="UN"]; EU` |
