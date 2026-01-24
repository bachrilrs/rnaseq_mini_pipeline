# Data Preprocessing
input_path  <- 'data/GSE60450_Lactation-GenewiseCounts.txt'
output_path <- 'data/GSE60450_Lactation-GenewiseCounts_filtered.txt'

# Dependencies
suppressPackageStartupMessages({
  if (!require("BiocManager", quietly = TRUE)) install.packages("BiocManager", repos = "https://cloud.r-project.org/")
  for (pkg in c("edgeR", "limma")) {
    if (!require(pkg, character.only = TRUE)) BiocManager::install(pkg, update = FALSE, ask = FALSE)
  }
  library(edgeR)
})

# Loading and Cleaning
data_raw <- read.table(input_path, header = TRUE, sep = "\t" , check.names = FALSE) # This will prevent the error that change '-' into . because R 
#colnames(data_raw)
# Keep only numeric columns
data <- data_raw[, sapply(data_raw, is.numeric)]


# Optimal Threshold Calculation (Jaccard Logic)
jaccard_test <- function(df, threshold) {
  A <- which(df[,1] >= threshold)
  B <- which(df[,2] >= threshold)
  if (length(union(A, B)) == 0) return(0)
  return(length(intersect(A, B)) / length(union(A, B)))
}

thresholds <- c(2, 5, 10, 20, 50)
scores <- sapply(thresholds, function(s) jaccard_test(data, s))
names(scores) <- thresholds



best_s <- as.numeric(names(which.max(scores)))



cat("Applying Filter\n")

# Keep genes with at least 'best_s' reads in at least 3 samples
keep <- rowSums(data >= best_s) >= 3
data_filtered <- data[keep, ]
#colnames(data_filtered)

# Output Statistics
n_initial <- nrow(data)
n_final   <- nrow(data_filtered)
cat("Filtering Summary:\n")
cat("Genes before:", n_initial, "\n")
cat("Genes after:", n_final, "\n")
cat("Genes removed:", n_initial - n_final, " (", round((1 - n_final/n_initial)*100, 1), "%)\n")

# Export
write.table(data_filtered, output_path, sep = "\t", quote = FALSE, col.names = NA)
cat("Filtered file ready for Python pipeline.\n")