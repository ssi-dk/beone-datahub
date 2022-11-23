  -h, --help            show this help message and exit

ReporTree:
  ReporTree input/output file specifications

  -a ALLELE_PROFILE, --allele-profile ALLELE_PROFILE
                        [OPTIONAL] Input allele/SNP profile matrix (tsv format)
  -align ALIGNMENT, --alignment ALIGNMENT
                        [OPTIONAL] Input multiple sequence alignment (fasta format)
  -d_mx DISTANCE_MATRIX, --distance_matrix DISTANCE_MATRIX
                        [OPTIONAL] Input pairwise distance matrix (tsv format)
  -t TREE, --tree TREE  [OPTIONAL] Input tree (newick format)
  -p PARTITIONS, --partitions PARTITIONS
                        [OPTIONAL] Partitions file (tsv format) - 'partition' represents the threshold at which clustering information was obtained
  -m METADATA, --metadata METADATA
                        [MANDATORY] Metadata file (tsv format). To take the most profit of ReporTree functionalities, you must provide this file.
  -vcf VCF, --vcf VCF   [OPTIONAL] Single-column list of VCF files (txt format). This file must comprise the full PATH to each vcf file.
  -var VARIANTS, --variants VARIANTS
                        [OPTIONAL] Input table (tsv format) with sample name in the first column and a comma-separated list of variants in the second column with the following regular expression:
                        '\w(\d+)\w'
  -out OUTPUT, --output OUTPUT
                        [OPTIONAL] Tag for output file name (default = ReporTree)
  --list                [OPTIONAL] If after your command line you specify this option, ReporTree will list all the possible columns that you can use as input in '--columns_summary_report'. NOTE!! The
                        objective of this argument is to help you with the input of '--columns_summary_report'. So, it will not run reportree.py main functions!!

Analysis details:
  Analysis details

  --analysis ANALYSIS   Type of clustering analysis (options: grapetree, HC, treecluster). If you provide a tree, genetic clusters will always be obtained with treecluster. If you provide a distance
                        matrix, genetic clusters will always be obtained with HC. If you provide any other input, it is MANDATORY to specify this argument.
  --subset              Obtain genetic clusters using only the samples that correspond to the filters specified in the '--filter' argument (only valid for analysis == grapetree or HC)
  -d DIST, --dist DIST  Distance unit by which partition thresholds will be multiplied (example: if -d 10 and -thr 5,8,10-30, the minimum spanning tree will be cut at 50,80,100,110,120,...,300. If -d 10
                        and --method-threshold avg_clade-2, the avg_clade threshold will be set at 20). This argument is particularly useful for non-SNP-scaled trees. Currently, the default is 1, which
                        is equivalent to 1 allele distance or 1 SNP distance. [1.0]
  --site-inclusion N_CONTENT
                        [OPTIONAL: Useful to remove informative sites/loci with excess of missing data] Minimum proportion of samples per site without missing data (e.g. '--site-inclusion 1.0' will only
                        keep loci/positions without missing data, i.e. a core alignment/profile; '--site-inclusion 0.0' will keep all loci/positions) NOTE: This argument works on profile/alignment
                        positions/loci (i.e. columns)! [default: 0.0 - content of missing data is not considered during matrix/alignment cleaning].

Processing profiles:
  Processing profiles

  --loci-called LOCI_CALLED
                        [OPTIONAL] Minimum proportion of loci/positions called for SNP/allele matrices (e.g. '--loci-called 0.95' will only keep in the profile matrix samples with > 95% of
                        alleles/positions, i.e. <= 5% missing data). Applied after '--site-inclusion' argument! Code for missing data: 0.

Alignment processing:
  Alignment processing

  --sample-ATCG-content ATCG_CONTENT
                        [OPTIONAL] Minimum proportion (0 to 1) of ATCG in informative sites of the alignment per sample (e.g. '--sample-ATCG-content 1.0' will only keep samples without N's or any non-
                        ATCG code in informative sites)
  --remove-reference    Set only if you want to remove the reference sequence of the alignment (reference name must be provided with the argument '--reference').
  --use-reference-coords
                        Set only if you want that column names in the final alignment matrix represent the reference coordinates (reference name must be provided with the argument '--reference') Note:
                        Depending on the alignment size, this argument can make alignment processing very slow!
  -r REFERENCE, --reference REFERENCE
                        [OPTIONAL] Name of reference sequence. Required if '--remove-reference' and/or '--use-reference-coords' specified.

Partitioning with GrapeTree:
  Specifications to get and cut minimum spanning trees

  --method GRAPETREE_METHOD
                        "MSTreeV2" [DEFAULT] Alternative:"MSTree (goeBURST)"
  --missing HANDLER     ONLY FOR MSTree. 0: [DEFAULT] ignore missing data in pairwise comparison. 1: remove column with missing data. 2: treat missing data as an allele. 3: use absolute number of
                        allelic differences.
  --n_proc NUMBER_OF_PROCESSES
                        Number of CPU processes in parallel use. [5]
  -thr THRESHOLD, --threshold THRESHOLD
                        Partition threshold for clustering definition. Different thresholds can be comma-separated (e.g. 5,8,16). Ranges can be specified with a hyphen (e.g. 5,8,10-20). If this option
                        is not set, the script will perform clustering for all the values in the range 0 to max. Note: Threshold values are inclusive, i.e. '-thr 7' will consider samples with <= 7
                        differences as belonging to the same cluster!
  --matrix-4-grapetree  Output an additional allele profile matrix with the header ready for GrapeTree visualization. Set only if you WANT the file!
  --wgMLST              [EXPERIMENTAL] a better support of wgMLST schemes (check GrapeTree github for details).

Partitioning with HC:
  Specifications to genetic clusters with hierarchical clustering

  --HC-threshold HCMETHOD_THRESHOLD
                        List of HC methods and thresholds to include in the analysis (comma-separated). To get clustering at all possible thresholds for a given method, write the method name (e.g.
                        single). To get clustering at a specific threshold, indicate the threshold with a hyphen (e.g. single-10). To get clustering at a specific range, indicate the range with a hyphen
                        (e.g. single-2-10). Note: Threshold values are inclusive, i.e. '--HC-threshold single-7' will consider samples with <= 7 differences as belonging to the same cluster! Default:
                        single (Possible methods: single, complete, average, weighted, centroid, median, ward)

Partitioning with TreeCluster:
  Specifications to cut the tree with TreeCluster

  --method-threshold METHOD_THRESHOLD
                        List of TreeCluster methods and thresholds to include in the analysis (comma-separated). To get clustering at all possible thresholds for a given method, write the method name
                        (e.g. root_dist). To get clustering at a specific threshold, indicate the threshold with a hyphen (e.g. root_dist-10). To get clustering at a specific range, indicate the range
                        with a hyphen (e.g. root_dist-2-10). Default: root_dist,avg_clade-1 (List of possible methods: avg_clade, leaf_dist_max, leaf_dist_min, length, length_clade, max, max_clade,
                        root_dist, single_linkage, single_linkage_cut, single_linkage_union) Warning!! So far, ReporTree was only tested with avg_clade and root_dist!
  --support SUPPORT     [OPTIONAL: see TreeCluster github for details] Branch support threshold
  --root-dist-by-node   [OPTIONAL] Set only if you WANT to cut the tree with root_dist method at each tree node distance to the root (similar to root_dist at all levels but just for informative
                        distances)

ReporTree metadata report:
  Specific parameters to report clustering/grouping information associated to metadata

  --columns_summary_report COLUMNS_SUMMARY_REPORT
                        Columns (i.e. variables of metadata) to get statistics for the derived genetic clusters or for other grouping variables defined in --metadata2report (comma-separated). If the
                        name of the column is provided, the different observations and the respective percentage are reported. If 'n_column' is specified, the number of the different observations is
                        reported. For example, if 'n_country' and 'country' are specified, the summary will report the number of countries and their distribution (percentage) per cluster/group.
                        Exception: if a 'date' column is in the metadata, it can also report first_seq_date, last_seq_date, timespan_days. Check '--list' argument for some help. Default =
                        n_sequence,lineage,n_country,country,n_region,first_seq_date,last_seq_date,timespan_days [the order of the list will be the order of the columns in the report]
  --partitions2report PARTITIONS2REPORT
                        Columns of the partitions table to include in a joint report (comma-separated). Other alternatives: 'all' == all partitions; 'stability_regions' == first partition of each
                        stability region as determined by comparing_partitions_v2.py. Note: 'stability_regions' can only be inferred when partitioning TreeCluster or GrapeTree is run for all possible
                        thresholds or when a similar partitions table is provided (i.e. sequential partitions obtained with the same clustering method) [all]. Check '--list' argument for some help
  --metadata2report METADATA2REPORT
                        Columns of the metadata table for which a separated summary report must be provided (comma-separated)
  -f FILTER_COLUMN, --filter FILTER_COLUMN
                        [OPTIONAL] Filter for metadata columns to select the samples to analyze. This must be specified within quotation marks in the following format 'column< >operation< >condition'
                        (e.g. 'country == Portugal'). When more than one condition is specified for a given column, they must be separated with commas (e.g 'country == Portugal,Spain,France'). When
                        filters include more than one column, they must be separated with semicolon (e.g. 'country == Portugal,Spain,France;date > 2018-01-01;date < 2022-01-01'). White spaces are
                        important in this argument, so, do not leave spaces before and after commas/semicolons.
  --sample_of_interest SAMPLE_OF_INTEREST
                        Comma-separated list of samples of interest for which summary reports will be created. If none provided, only the summary reports comprising all samples will be generated.
  --frequency-matrix FREQUENCY_MATRIX
                        [OPTIONAL] Metadata column names for which a frequency matrix will be generated. This must be specified within quotation marks in the following format 'variable1,variable2'.
                        Variable1 is the variable for which frequencies will be calculated (e.g. for 'lineage,iso_week' the matrix reports the percentage of samples that correspond to each lineage per
                        iso_week). If you want more than one matrix you can separate the different requests with semicolon (e.g. 'lineage,iso_week;country,lineage'). If you want a higher detail in your
                        variable2 and decompose it into two columns you use a colon (e.g. lineage,country:iso_week will report the percentage of samples that correspond to each lineage per iso_week in
                        each country)
  --count-matrix COUNT_MATRIX
                        [OPTIONAL] Same as '--frequency-matrix' but outputs counts and not frequencies
  --mx-transpose        [OPTIONAL] Set ONLY if you want that the variable1 specified in '--frequency-matrix' or in '--count-matrix' corresponds to the matrix first column.

Stability regions:
  Congruence analysis of cluster composition at all possible partitions to determine regions of cluster stability (automatically run if you set --partitions2report 'stability_regions'). WARNING! This option is planned to handle sequential partitions obtained with the same clustering method, such as a partitions table derived from cg/wgMLST data (from 1 to max allele threshold). Use it at your own risk, if you provide your own partitions table.

  -AdjW ADJUSTEDWALLACE, --AdjustedWallace ADJUSTEDWALLACE
                        Threshold of Adjusted Wallace score to consider an observation for method stability analysis [0.99]
  -n N_OBS, --n_obs N_OBS
                        Minimum number of sequencial observations that pass the Adjusted Wallace score to be considered a 'stability region' (i.e. a threshold range in which cluster composition is
                        similar) [5]
  -o ORDER, --order ORDER
                        [Set only if you provide your own partitions table] Partitions order in the partitions table (0: min -> max; 1: max -> min) [0]
  --keep-redundants     Set ONLY if you want to keep all samples of each cluster of the most discriminatory partition (by default redundant samples are removed to avoid the influence of cluster size)