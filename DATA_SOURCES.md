# Public Data Sources for Feature Testing

This repository's notebooks are intended for exploratory experiments using publicly available speech and language datasets. Please obtain the data directly from the original providers as it is **not** distributed in this repository.

- **DementiaBank**: <https://dementia.talkbank.org>
  - English transcripts and corresponding audio files in `.cha` and `.wav` format
  - Widely used for research on cognitive decline and dementia
- **ADReSS / ADReSSo Challenge**
  - Balanced dataset of 156 speech samples for detecting Mild Cognitive Impairment vs. healthy controls
  - See <https://www.isca-speech.org/iscapad/2020-05/ISCApad.html#conferences>

When you have downloaded the datasets, place the `.wav` files and transcripts under `neurotone-feature-tests/data/raw/` and `neurotone-feature-tests/data/transcripts/` respectively. Update `samples_list.csv` with the file names, language information, and labels.
