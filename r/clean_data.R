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

if (!require("ggplot2", quietly = TRUE)) install.packages("ggplot2")
if (!require("tidyr", quietly = TRUE)) install.packages("tidyr")
library(ggplot2)
library(tidyr)

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

lib_sizes <- colSums(data_filtered)

# 3. Création du DataFrame avec la métadonnée Condition (le "hue" en Python)
plot_df <- data.frame(
  sample_id = names(lib_sizes),
  library_size = lib_sizes
)

plot_df = plot_df[-c(1,2),]

# 3. Logique IF pour séparer Virgin et Lactation
# On cherche "MCL1-D" pour virgin et "MCL1-L" pour lactation
plot_df$condition <- ifelse(grepl("MCL1-D", plot_df$sample_id), "virgin", 
                            ifelse(grepl("MCL1-L", plot_df$sample_id), "lactation", "unknown"))

# 4. Génération du graphique type "Seaborn" avec ggplot2
cat("Generating Library Size plot with corrected conditions...\n")
p <- ggplot(plot_df, aes(x = sample_id, y = library_size, fill = condition)) +
  geom_bar(stat = "identity") +
  theme_minimal() +
  labs(title = "Library size per sample",
       x = "sample_id",
       y = "library_size",
       fill = "condition") +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1)) + # Rotation 90°
  scale_fill_manual(values = c("virgin" = "#56B4E9", "lactation" = "#E69F00", "unknown" = "#999999"))

# 5. Sauvegarde
output_dir <- "output/plots"
if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

ggsave(filename = paste0(output_dir, "/library_size_R.png"), plot = p, width = 10, height = 6)
cat("Plot saved to:", paste0(output_dir, "/library_size_R.png"), "\n")




