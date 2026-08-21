library(dplyr)
library(readr)

# Stack ICPSR 226001 with panel_icpsr_compat.csv.
merge_icpsr <- function(icpsr_dir, extension_file) {
  extension_raw <- read_csv(extension_file, show_col_types = FALSE)
  topic_cols <- grep("^icpsr_topic_", names(extension_raw), value = TRUE)
  topic_cols <- topic_cols[!grepl("_home$", topic_cols)]
  topics <- sub("^icpsr_topic_", "", topic_cols)

  complexity <- read_csv(
    file.path(icpsr_dir, "candidates_complexity.csv"),
    show_col_types = FALSE
  ) |>
    filter(stage == 2, data_source == "general_wayback", year <= 2016)

  topic_scores <- read_csv(
    file.path(icpsr_dir, "candidates_topics.csv"),
    show_col_types = FALSE
  ) |>
    filter(stage == 2) |>
    select(candidate, year, state, district, all_of(topics))

  icpsr <- complexity |>
    left_join(topic_scores, by = c("candidate", "year", "state", "district")) |>
    transmute(
      candidate, state, district = as.character(district), year, party,
      office = "house", n_char, n_words, n_tags, n_clean_tags,
      ttr = TTR, mattr = MATTR, entropy,
      across(all_of(topics)), source = "icpsr"
    )

  extension <- extension_raw |>
    transmute(
      candidate = candidate_icpsr, state,
      district = as.character(district_id), year, party, office,
      n_char = icpsr_n_char, n_words = icpsr_n_words,
      n_tags = icpsr_n_tags, n_clean_tags = icpsr_n_clean_tags,
      ttr = icpsr_ttr_approx, mattr = icpsr_mattr_approx,
      entropy = icpsr_entropy_approx,
      across(all_of(topic_cols)), source = "extension"
    ) |>
    rename_with(~ sub("^icpsr_topic_", "", .x), all_of(topic_cols)) |>
    mutate(party = recode(as.character(party),
                          D = "democrat", R = "republican"))

  bind_rows(icpsr, extension) |>
    arrange(office, year, state, candidate)
}

# Example:
# combined <- merge_icpsr("path/to/ICPSR-226001", "panel_icpsr_compat.csv")
