######################################################
### SOCKS Project - Corpus Analysis of TINTIN Data ###
######################################################


### Clear console and load libraries ###
rm(list=ls(all=TRUE))
#library(languageR)
library(corrplot)
library(gplots)
library(lme4)
library(lmerTest)
#library(sjPlot)
#library(car)
library(readxl)
library(dplyr)
library(stringr)
library(ggplot2)


#say whether or not you are plotting shapes or layout for manual checks
plotting_shapes_check = 1 #1 for plotting and 0 for no plotting
plotting_layout = 1 # 1 for plotting and 0 for no plotting


### Set directories ###
maindir = '//files/shared/Labs/Coderre/Studies/SOCKS project - comic complexity rating scale'
maindir = 'L:/Labs/Coderre/Studies/SOCKS project - comic complexity rating scale'
#datadir = '//files/shared/Labs/Coderre/Studies/Visual Ease Assumption DOD project/DATA/Behavioral comprehension tests'


###########################
### Load in TINTIN data ###
###########################

setwd(maindir)

# This comes from Neil's giant Excel file

# the read_excel() function can load in Excel files directly, but it also has all sort of weird fields
# alldata = read_excel('TINTIN_Corpus.xlsx')


# What I usually do is load it as a text file. But first there's some cleanup that has to happen.
# First, open it in Excel and use Find and Replace to:
# - replace all blank cells with NAs 
# - replace all spaces with underscores 
# - change # to Num
# - change & to and
# - change " to [nothing] <- leave 'replace with' field empty

# Then save as txt file.
# If/when we get updated data from Neil, will need to do this and resave.

# this loads it as a text file
alldata = read.table('TINTIN_Corpus_Complexity.txt',header=TRUE)
#alldata = read.table('MAST test annotations.txt', header=TRUE)



######################################
### Pull out variables of interest ###
######################################

# See section at the end of this script called 'Methods we propose in the grant' for a full list of everything we said we'd do

# Ultimately what we want to end up with here is a data frame with one row per title, with columns for all the variables of interest.

# get list of all titles in the corpus
alltitles = levels(as.factor(alldata$Document_Name))

# build the giant data frame we will plug all these variables into
# (Note: come up with a better name than 'bigdata' or 'variablesbytitle')
variablesbytitle = array(dim=c(length(alltitles),20))
colnames(variablesbytitle) = c('title','NumPages','TotalPanels','avPanelsPerPage','PanelShapes','Borders',
'Directionality','PanelOrg','LayoutComplexity','FramingComplexity','ImageSequence','BackgroundComplexity',
'SituationalCoherence','CompositionalStructure','PerspectiveTaking','ConventionalPaneling','AvCharactersPerPanel',
'Arousal', 'Valence', 'audience')

# use just the first title for now but eventually we'll open this up to the rest of the loop
t = 654
#for (t in 1:length(alltitles)){

	title = alltitles[t]
	titledata = alldata[alldata$Document_Name == title,]

	variablesbytitle[t,1] = title


	### Length ###------------------------------------------------------
	# Should this be number of pages? Or total number of panels? Putting both in for now.

	# get total number of pages and save as new variables, we will need this later for loops
	numpages = max(titledata$Page_Number,na.rm=TRUE)		

	variablesbytitle[t,2] = numpages
	variablesbytitle[t,3] = as.numeric(as.character(titledata$TotalPanels[nrow(titledata)]))	# total panels in entire title


	### Panels per page ###-----------------------------------------------------
	# This will be an average over all pages in the title
	# But cannot just average over MaxPagePanels because this has multiple rows per page and will throw off the averaging
	
	# create new little data frame of number of panels per page
	pagepanels = vector()
	for (p in 1:numpages){
		pagedata = titledata[titledata$Page_Number == p,]

		pagepanels = rbind(pagepanels,max(pagedata$PanelNum,na.rm=TRUE))
	}
	
	# then average over this to calculate average panels per page
	variablesbytitle[t,4] = mean(pagepanels)


	### Panel Shapes ###------------------------------------
	#averages the type of panels by page by assigning a 0 to Rectangles and a 1 to anything else

	#create a new little data frame of panel shapes

	panelshapes <- data.frame(
					Panel = titledata$PanelNum,
					vertices = titledata$Region_Vertices,
					ShapeType = NA,
					shapetool = titledata$Region_Type,
					shapecomplexity = NA,
					stringsAsFactors = FALSE
					)
	panelshapes$shapetool <- titledata$Region_Type

	#set up manual checking
	quad_diagnostics <- data.frame(
	Panel = integer(),
	ComicPanel = integer(),
	Page_number = integer(),
	coords = character(),
	edges = character(),
	side_lengths = character(),
	dot_products = character(),
	right_angles = logical(),
	equal_sides = logical(),
	shape_type = character(),
	corner_angles = character(),
	stringsAsFactors = FALSE
	)

	for (p in seq_len(nrow(titledata))) {
		edges <- NULL
		dot_products <- NA
		side_lengths <- NA
		corner_angles <- NA
		right_angles <- NA
		equal_sides <- NA
		shape_type <- NA
		
		# Skip non-polygons
  		if (panelshapes$shapetool[p] != "POLYGON") {
			panelshapes$ShapeType[p] <- panelshapes$shapetool[p]

			quad_diagnostics <- rbind(quad_diagnostics, data.frame(
			Panel = titledata$PanelNum[p],
			Page_number = titledata$Page_Number[p],
			ComicPanel = titledata$ComicPanel[p],
			coords = NA,
			edges = NA,
			side_lengths = NA,
			dot_products = NA,
			right_angles = NA,
			equal_sides = NA,
			shape_type = panelshapes$shapetool[p],
			corner_angles = NA
		))
    		next
  			}
			#extract coordinates
			coords_str <- as.character(titledata$Region_Vertices[p])

			# skip NA or empty strings
			if (is.na(coords_str) || coords_str == "") {

			panelshapes$ShapeType[p] <- "NO_COORDS"

			quad_diagnostics <- rbind(quad_diagnostics, data.frame(
				Panel = titledata$PanelNum[p],
				ComicPanel = titledata$ComicPanel[p],
				Page_number = titledata$Page_Number[p],
				coords = NA,
				edges = NA,
				side_lengths = NA,
				dot_products = NA,
				right_angles = NA,
				equal_sides = NA,
				shape_type = "NO_COORDS",
				corner_angles = NA
			))

			next
			}


			# Regex to capture negative numbers and decimals and convert numbeers ot numeric
			matches <- regmatches(coords_str, gregexpr("-?[0-9]+\\.?[0-9]*", coords_str))
			nums <- if (length(matches[[1]]) > 0) as.numeric(matches[[1]]) else numeric(0)
			nums <- as.numeric(nums)

			# Ensure even number of coordinates
			if(length(nums) %% 2 != 0 || length(nums) == 0) {

				panelshapes$ShapeType[p] <- "PARSE_FAILED"

				quad_diagnostics <- rbind(quad_diagnostics, data.frame(
					Panel = titledata$PanelNum[p],
					ComicPanel = titledata$ComicPanel[p],
					Page_number = titledata$Page_Number[p],
					coords = coords_str,
					edges = NA,
					side_lengths = NA,
					dot_products = NA,
					right_angles = NA,
					equal_sides = NA,
					shape_type = "PARSE_FAILED",
					corner_angles = NA
				))

				next
				}

			#reshape numeric vector to matrix of coordinates
			coords <- matrix(nums, ncol = 2, byrow = TRUE)
			colnames(coords) <- c("x","y")
			n_pts <- nrow(coords)

			# Order coordinates

			#calculate center of polygon
			centroid_x <- mean(coords[,1])
			centroid_y <- mean(coords[,2])

			#calculate angle of each vertex relative to central point
			angles <- numeric(n_pts)
			for (i in 1:n_pts) {
			angles[i] <- atan2(coords[i,2] - centroid_y,
								coords[i,1] - centroid_x)
			}

			order_idx <- order(angles) #counterclockwise order
			coords <- coords[order_idx, ]
			
			# Calculate sides and slopes
			n <- nrow(coords)

			sides <- numeric(n)
			slopes <- numeric(n)

			for (i in 1:n) {
				j <- ifelse(i == n, 1, i + 1)
				
				dx <- coords[j,1] - coords[i,1]
				dy <- coords[j,2] - coords[i,2]
				
				sides[i] <- sqrt(dx^2 + dy^2)
				
				if (is.na(dx) || is.na(dy)) {
					slopes[i] <- NA
					} else if (dx == 0) {
					slopes[i] <- Inf
					} else {
					slopes[i] <- dy / dx
					}
			}

			#Classification
			shape_type <- ""
			if (n_pts == 2) {
				dx <- coords[2,1] - coords[1,1]
				dy <- coords[2,2] - coords[1,2]
				
				length <- sqrt(dx^2 + dy^2)   # line length
				
				# Optional: orientation
				if (abs(dy) < 1e-6) {
					shape_type <- "Horizontal line"
				} else if (abs(dx) < 1e-6) {
					shape_type <- "Vertical line"
				} else {
					shape_type <- "Diagonal line"
				}

				# Store in panelshapes
				panelshapes$ShapeType[p] <- shape_type
			}

			if (n == 3) {
			shape_type <- "TRIANGLE"
			} else if (n == 4) {
			# Compute vectors for edges
				edges <- matrix(0, nrow = 4, ncol = 2)

				for (i in 1:4) {
					j <- ifelse(i == 4, 1, i + 1)
					edges[i, ] <- coords[j, ] - coords[i, ]
					}
					# Tolerance parameters (adjust as needed)
					angle_tol <- 2       # for right angles
					side_tol  <- 10       # for side length equality
					
					#Calculate internal corner angles in degrees
					corner_angles <- rep(NA, 4)
					for (i in 1:4) {
						prev_idx <- ifelse(i == 1, 4, i - 1)
						next_idx <- ifelse(i == 4, 1, i + 1)
						v1 <- coords[prev_idx, ] - coords[i, ]
						v2 <- coords[next_idx, ] - coords[i, ]
						cos_theta <- sum(v1 * v2) / (sqrt(sum(v1^2)) * sqrt(sum(v2^2)))
						cos_theta <- min(max(cos_theta, -1), 1)  # clamp to [-1,1]
						corner_angles[i] <- acos(cos_theta) * 180 / pi
					}

					# Compute side lengths
					side_lengths <- sqrt(rowSums(edges^2)) #calculated using euclidian distance

					# Check right angles using dot product
					right_angles <- TRUE
					dot_products <- numeric(4)

					for (i in 1:4) {
						j <- ifelse(i == 4, 1, i + 1)
						
						dot_products[i] <- sum(edges[i, ] * edges[j, ])
						
						# Only check if not NA
						right_angles <- all(!is.na(corner_angles) &
                    abs(corner_angles - 90) <= angle_tol)
						
						# If dot_product is NA, mark right_angles as FALSE (optional)
						if (is.na(dot_products[i])) right_angles <- FALSE
					}

				# Check if all sides equal
				equal_sides <- (max(side_lengths) - min(side_lengths)) <= side_tol

				# Classification
				if (right_angles && equal_sides) {
					shape_type <- "SQUARE"
				} else if (right_angles) {
					shape_type <- "RECTANGLE"
				} else {
					shape_type <- "QUADRILATERAL"
				}
				
			} else {
			# Circle detection for n >= 5
			centroid_x <- mean(coords[,1])
			centroid_y <- mean(coords[,2])
			distances <- sqrt((coords[,1] - centroid_x)^2 + (coords[,2] - centroid_y)^2)
			tolerance <- 0.02  # adjust based on how close points need to be
			if (max(distances) - min(distances) <= tolerance * mean(distances)) {
				shape_type <- "CIRCLE"
			} else {
				shape_type <- paste(n, "-SIDED POLYGON")
				}
			
		
		}
	
		#Store in the data frame
		panelshapes$ShapeType[p] <- shape_type
			edges_str <- NA
			if (!is.null(edges) && is.matrix(edges) && nrow(edges) > 0) {
			edges_str <- paste(apply(edges, 1, function(x) paste(x, collapse=",")), collapse=" | ")
			}
		quad_diagnostics <- rbind(quad_diagnostics, data.frame(
			Panel = titledata$PanelNum[p],
			ComicPanel = titledata$ComicPanel[p],
			Page_number = titledata$Page_Number[p],
			coords = paste(apply(coords, 1, paste, collapse=","), collapse=" | "),
			edges = edges_str,
			side_lengths = paste(round(side_lengths, 4), collapse=","),
			dot_products = NA,
			right_angles = right_angles,
			equal_sides = equal_sides,
			shape_type = shape_type,
			corner_angles = paste(round(corner_angles, 2), collapse=",")
			))
}
		#create a data frame that will hold complexity values
  	panelshapes$shapecomplexity <- ifelse(
  		panelshapes$ShapeType == "SQUARE", 0,
  		ifelse(panelshapes$ShapeType == "RECTANGLE", 0.5, 1)
		)
			
	variablesbytitle[t,5] = mean(panelshapes$shapecomplexity, na.rm = TRUE)

	### Borders ###---------------------------------------------------------
	# Panels with defined borders will be simpler to understand, whereas panels without clearly defined edges 
	# will require additional processing by the reader to understand where the edges of each panel lie. 
	# Normative or not: normal border (line) = 0; no border = 0.33 (should be a little harder); non-meaningful decorative border (thicker, ornate) = 0.66; border with meaning (e.g., thought bubble) = 1

	bordercomplexity <- data.frame (BorderComplexity = titledata$BorderComplexity)
	variablesbytitle[t,6]=mean(bordercomplexity$BorderComplexity, na.rm = TRUE)

	### Directionality ###------------------------------------------------------
	# Left-to-right “Z-paths”, which mimic alphabetic writing systems, are simpler for readers familiar with alphabetic writing systems to understand than up-and-down columns or more complex paths in which panels are read.  
	#In the TINTIN Corpus, some books use a right-to-left S-path order, where that complexity metric would be flipped.


	#create small data frame to hold angle and directionality variables
	directionality  <- data.frame (
		Angle = titledata$Angle,
		AngleFromPrevious = titledata$AngleFromPrevious,
		AngleNum = NA_real_
	)

	#create normalized values for angle types
	directionality$AngleNum = ifelse(directionality$AngleFromPrevious %in% c("Left", "Down-Right"), 0,
                           ifelse(directionality$AngleFromPrevious == "Down", 0.5,
                           ifelse(directionality$AngleFromPrevious %in% c("Right", "Up",
						    "Down-Left", "Up-Left", "Up-Right"), 1,
                           NA)))
	
	#NA dependency on Angle value
	#if NA but has angle, check if angle is within 5 degrees of 180 
	#and then give value of 1
	directionality$AngleNum <- ifelse(
    is.na(directionality$AngleNum) &
        !is.na(directionality$Angle) &
        abs(directionality$Angle - 180) <= 5,
		1,
		directionality$AngleNum
		)

	#input to variablesbytitle
	variablesbytitle[t,7]=mean(directionality$AngleNum, na.rm = TRUE)

##############################################################
##################################################################
##################################################################
	### Panel Layout / Organization ###-------------------------------------
	# Layouts using pure grids or whole rows tend to be simplest, whereas staggers add another level of complexity, and embedded columns (“blockages”) tend to be more complex.
	# Could incorporate Borders into this too. Also panel shapes, although we didn't code that overtly.
	# Can derive arrangements (row, column, blockage, staggering) from Directionality but will be redundant with it. Could use coordinates of panels in Python - for each panel region, find midpoint and then find midpoint of next panel and create a vector between them. Can also do distance between panels. 

# calculation of rows and columns: extract from directionality data -- if two rights in a row before a down left (row of 3 panels) similar idea to up and down
# if we think that number of panels in a row or column is an interesting variable for
# blockage if down and then an up-right or down and up-left reverse blockage up-right and then a down
# normalize across layouts and treate right and left as laterals
# staggering - figure out a way to calculate that from the coordinates (take relative coordinates)
# calculate the gutter and alignment (panel vs rows)

#pull out whole rows and columns and blockages being more complex

#panel shape: square 1 rectangle 2 all 3
#lateral 1 down angle 2 downward 3 upward 4
#grid/horiztonal rows 1 vertical columns 2 inset 3
#normal gutters 1 no or wide gutters 2 overlapping 3
#sum and divide by 13 / averaged

#Page 90 and 91 from  his comic book

#calculate rows and columns from directionality

#separate panels by page

#for each page 
	#1: identify the index of a down(-) or up(-) direction and put into a data.frame
	#2: row number = number of down or up directions
	#3 column number = number of panels divided by the row
	#plot panel shapes per page to manually check this if plotting_layout =1 then plot

#create final output list
panel_layout_list <- list()

#extract all unique comic pages
pages <- unique(titledata$Page_Number)

for (page in pages) { #iterate each page independently
	#get panels for one page
  subset_data <- titledata[titledata$Page_Number == page, ]
	
  # -----------------------------
  # 1. EXTRACT CENTROIDS
  # -----------------------------
  
  #initialize empty table for spatial representation
  centroids <- data.frame(
		Panel = integer(),
		x = numeric(),
		y = numeric()
		)

  for (i in seq_len(nrow(subset_data))) { #iterate over each panel per page

    #extract coordinate string for panel geometry
	coords_str <- subset_data$Region_Vertices[i]

	#skip missing or empty string for panel geometry
    if (is.na(coords_str) || coords_str == "") next

	#extract all numeric values
    matches <- regmatches(coords_str, gregexpr("-?[0-9]+\\.?[0-9]*", coords_str))
    
	#convert extracted strings into vector
	nums <- as.numeric(matches[[1]])

	#require at least 2 coordinate pairs (x,y); or it is invalid
    if (length(nums) < 4 || length(nums) %% 2 != 0) next

    #reshape into (x,y) coordinate matrix
	coords <- matrix(nums, ncol = 2, byrow = TRUE)
    
	#ensure at least 2 points for valid shape
	if (nrow(coords) < 2) next

    centroids <- rbind(
					centroids,
					data.frame(
						Panel = subset_data$PanelNum[i],
						x = mean(coords[,1]),
						y = mean(coords[,2])
					)
					)
  }

  # -----------------------------
  # CLEANING
  # -----------------------------
  #remove any NA centroid entries
  centroids <- centroids[complete.cases(centroids), ]
  
  # remove duplicate centroids
  centroids <- centroids %>%
  distinct(Panel, .keep_all = TRUE)

  # get number of valid panels on page after filtering
  n <- nrow(centroids)

 # do not infer spatial structure from fewer than 2 panels
  if (n < 2) {
    panel_layout_list[[length(panel_layout_list) + 1]] <- data.frame(
      Page_Number = page,
      layout_type = "INSUFFICIENT_DATA",
      grid_score = NA,
      stagger_score = NA,
      blockage_score = NA,
      flow_score = NA
    )
    next
  }

  # -----------------------------
  # 2. ROW STRUCTURE (Y CLUSTERING VIA BANDS)
  # -----------------------------
  # sort vertical positions to detect rows
  y_sorted <- sort(centroids$y)

  # compute vertical spacing between consecutive panels
  y_diff <- diff(y_sorted)

  #detect unsually large vertical gaps (new rows)
  row_breaks <- sum(y_diff > median(y_diff, na.rm = TRUE) * 1.5)
  row_score <- 1 / (1 + row_breaks)   # fewer breaks = stronger grid rows

  # -----------------------------
  # 3. COLUMN STRUCTURE (X ALIGNMENT)
  # -----------------------------
  #sort horizontal positions to detect columns
  x_sorted <- sort(centroids$x)

  #compute horizontal spacing between panels
  x_diff <- diff(x_sorted)

  #detect structural column shifts
  col_breaks <- sum(x_diff > median(x_diff, na.rm = TRUE) * 1.5)

  #normalize column regularity
  col_score <- 1 / (1 + col_breaks)

  # -----------------------------
  # 4. FLOW REGULARITY (DIRECTIONAL READING FLOW)
  # -----------------------------

	# extract direction sequence
	dirs <- directionality$AngleFromPrevious

	# treat NA as page/sequence breaks
	page_sequences <- split(
	dirs,
	cumsum(is.na(dirs))
	)

	# remove empty groups
	page_sequences <- page_sequences[
	sapply(page_sequences, function(x)
		any(!is.na(x)))
	]

	# initialize counters
	total_lateral <- 0
	total_vertical <- 0
	total_diagonal <- 0
	total_upward <- 0
	total_reversals <- 0
	total_transitions <- 0

	# analyze each independent sequence
	for (seq in page_sequences) {

	# remove NA values
	seq <- na.omit(seq)

	# skip tiny sequences
	if (length(seq) < 2) next

	# normalize direction labels
	seq <- toupper(trimws(seq))

	# count movement categories
	lateral <- sum(seq %in% c("Right", "Left"))

	vertical <- sum(seq %in% c("Down", "Up"))

	diagonal <- sum(seq %in% c(
		"Down-Left", "Down-Right",
		"Up-Left", "Up-Right"
	))

	upward <- sum(seq %in% c(
		"Up",
		"Up-Left",
		"Up-Right"
	))

	# transition analysis
	prev <- seq[-length(seq)]
	next <- seq[-1]

	# left-right reversals
	reversals <- sum(
		(prev == "Right" & next == "Left") |
		(prev == "Left" & next == "Right")
	)

	# accumulate totals
	total_lateral <- total_lateral + lateral
	total_vertical <- total_vertical + vertical
	total_diagonal <- total_diagonal + diagonal
	total_upward <- total_upward + upward
	total_reversals <- total_reversals + reversals
	total_transitions <- total_transitions + length(prev)
	}

	# avoid divide-by-zero
	if (total_transitions == 0) {
	flow_score <- NA

	} else {

	# normalize components
	diagonal_rate <- total_diagonal / total_transitions
	upward_rate <- total_upward / total_transitions
	reversal_rate <- total_reversals / total_transitions

	# regular flow:
	# low diagonals
	# low upward motion
	# low reversals
	irregularity <- (
		diagonal_rate +
		upward_rate +
		reversal_rate
	) / 3

	# higher score = smoother reading flow
	flow_score <- 1 - irregularity
	}

  # -----------------------------
  # 5. BLOCKAGE / INSET SCORE (SPACING DISCONTINUITIES)
  # -----------------------------
  #pairwise distance matrix between all panels
  dist_mat <- as.matrix(dist(centroids))

  #extract unique pairwise distances (avoid duplicaiton)
  upper <- dist_mat[upper.tri(dist_mat)]

  #variability in spacing (high = uneven layout)
  gap_sd <- sd(upper, na.rm = TRUE)
  #average spacing baseline
  gap_mean <- mean(upper, na.rm = TRUE)

  #normalized dispersion, detect inset panels/separated blocks
  blockage_score <- gap_sd / (gap_mean + 1e-6)

  # -----------------------------
  # 6. OVERALL STRUCTURE CLASSIFICATION
  # -----------------------------

  layout_type <- if (row_score > 0.7 & col_score > 0.7) {

    "GRID"
	#strong row +column structure = regular grid layout

  } else if (row_score > 0.6 & flow_score < 0.3) {

    "STAGGER"
	#row structure exists but flow is inconsistent = staggered layout

  } else if (blockage_score > 0.6) {

    "BLOCKAGE"
	#high spatial variance, inset or segmented layout

  } else {

    "IRREGULAR"
	#no dominant structural pattern detected
  }

  # -----------------------------
  # STORE
  # -----------------------------
  panel_layout_list[[length(panel_layout_list) + 1]] <- data.frame(
    Page_Number = page,
    layout_type = layout_type,
    grid_score = (row_score + col_score) / 2,
    stagger_score = 1 - flow_score,
    blockage_score = blockage_score,
    flow_score = flow_score
  )
}

#combine all page-level results into final dataset
panel_layout_df <- do.call(rbind, panel_layout_list)


#######################################################################
#################################################################
#######################################################################

	### Layout Complexity Score ###---------------------------
	#the scores of panels per page, panel shapes, borders, panel layout/org, directionality will be averaged to create an overall “layout complexity” score.
	######## NOTE: panels per page are averaged but not normalized, so one title could have 4 per page and another could have 8 and this may skew results in favor of panels per page being easier (since other metrics show 1 as easiest and 0 has hardest)
	
	#convert characters to numeric values
	# copy to new array
	variablesbytitletemp <- as.data.frame(variablesbytitle, stringsAsFactors = FALSE)

	# convert columns 4–8 to numeric
	variablesbytitletemp[t, 4:8, drop = FALSE]
	variablesbytitletemp[, 4:8] <- lapply(
		variablesbytitletemp[, 4:8],
		function(x) as.numeric(as.character(x))
	)

	# compute the mean on the numeric copy
	variablesbytitletemp[t, 9] <-
    rowMeans(variablesbytitletemp[t, 4:8, drop = FALSE], na.rm = TRUE)

	#put value into original array
	variablesbytitle[t, 9] <- variablesbytitletemp[t, 9]


	### Complexity of Framing Structure ### ---------------------
	#create data frame for framing complexity such that descriptors 
	# and the automated scores are present
	# Macro = 1, mono = 0.75, micro = 0.5, Amorphic = 0.25
	framingcomplexity <- data.frame (
		Framing = titledata$Framing,
		FramingComplexity = titledata$FramingComplexity
	)
	
	variablesbytitle[t,10]=mean(framingcomplexity$FramingComplexity, na.rm = TRUE)


	### Sequencing of Images ###------------------
	# Shifts in time maintaining full views of scenes are simpler than those that shift between views of characters, between viewpoints (i.e., zooms), between different perspectives (e.g., third to first person point-of-view), between different domains (e.g., from “reality” to a dream sequence or flashback), or that use idiosyncratic sequencing patterns (e.g., “cross-cutting” shifts back and forth between characters).
	# Things layered ontop of each other, e.g., shift between macros that also has a character change
	# New method for this - combining framing types and situational changes
	# Narrative complexity

	imagesequencing <- data.frame (
		narrativecomplexity = titledata$NarrativeComplexity,
		characterchangesnum = titledata$CharacterChangeNum,
		timechangesnum = titledata$TimeChangeNum,
		spacechangesnum = titledata$SpaceChangeNum,
		characterchanges = titledata$CharacterChangeNum.1,
		timechanges = titledata$TimeChangeNum.1,
		spacechanges = titledata$SpaceChangeNum.1,
		framing = titledata$Framing,
		framingcomplexity = titledata$FramingComplexity
	)
	variablesbytitle[t,11]=mean(imagesequencing$narrativecomplexity, na.rm = TRUE)


	### Backgrounds ###-------------------------------------
	# in the background explicitness scores depicted = 1 amorphic = 0.75 affix = 0.5

	#create a data frame to hold background information
	backgroundcomplexity <- data.frame(
		Backgrounds = titledata$Backgrounds,
		BackgroundExplicitness = titledata$BackgroundExplicitness
		)
		variablesbytitle[t,12]= mean(backgroundcomplexity$BackgroundExplicitness, na.rm = TRUE)

	### Situational Coherence ### ---------------------------
	# Time, character, and location shifts/changes
	# These should be output as three separate columns in TINTIN
	# For any given panel, can average across these three values. Or can add them together.
	# Full changes = 1; partial change = 0.5; no change = 0
	# If adding, will want to invert the numbers for time since normative time is moving. So time moving = 0, partial change = 0.5, no change = 1
	# Or may want to average over every panel for each one of these, then create a composite average

	situationalcoherence <- data.frame (
		characterchangesnum = titledata$CharacterChangeNum,
		timechangesnum = titledata$TimeChangeNum,
		spacechangesnum = titledata$SpaceChangeNum,
		characterchanges = titledata$CharacterChangeNum.1,
		timechanges = titledata$TimeChangeNum.1,
		spacechanges = titledata$SpaceChangeNum.1
	)

	situationalcoherence$situationperpanel <- rowMeans(
  		situationalcoherence[, c(
    	"characterchangesnum",
    	"timechangesnum",
    	"spacechangesnum"
  		)],
  		na.rm = TRUE
	)

	variablesbytitle[t, 13] <- mean(situationalcoherence$situationperpanel, na.rm = TRUE)

################################
###############################
################################
	### Compositional Structure ###----------------------------
	# Will need to think about this one - lots of variables. Each variable probably has single things that we could compute, and then we'd need to think about how to combine them.
	# Not in TINTIN yet

# ICS
# shot scale (higher the number the wider the viewpoint (more simple)), angle of view (closer to 0 are more simple), flow (complicated and doesn't really have a straight forward harder or easier) - flow alignment (1 is easier and 0 is less easy), framing of angle (0 is normative and 1 is not)
# not in every book
# normative and non-normative
# angle of view 0 is 0, 45 is 0.5, high or low angle is equal, top or bottom up are 1
# flow alignment - action in panels match actual direction (yes is easier)

	compositionalstructure <- data.frame(
		shotscale = titledata$ShotScale,
		shotscalenum = titledata$ShotScaleNum,
		angleofview = titledata$AngleofView,
		angleofviewnum = titledata$AngleofViewNum,
		angleofviewcomplexity = NA,
		flow = titledata$FlowAlignmentType,
		flownum = titledata$Flow.AlignmentNum,
		flowcomplexity = NA,
		framingangle = titledata$FramingAngle,
		framinganglenum = titledata$FramingAngleNum
	)

	compositionalstructure$angleofviewcomplexity = ifelse(compositionalstructure$angleofviewnum == 0, 0,
													ifelse(compositionalstructure$angleofviewnum %in% c(45, -45), 0.5,
													ifelse(compositionalstructure$angleofviewnum %in% c(90, -90), 1, NA)))

	compositionalstructure$flowcomplexity = ifelse(compositionalstructure$flownum == 1, 0,
	ifelse(compositionalstructure$flownum ==0, 1, NA))

	compositionalstructuremeans <- data.frame(
		shotscalemean = mean(compositionalstructure$shotscalenum),
		angleofviewmean = mean(compositionalstructure$angleofviewcomplexity),
		flowmean = mean(compositionalstructure$flowcomplexity),
		framinganglemean = mean(compositionalstructure$framinganglenum)
	)

	variablesbytitle[t,14] = mean(as.numeric(compositionalstructuremeans[1, ]), na.rm = TRUE)

	### Perspective Taking ###--------------------------------------
	# First-person perspective, over the shoulder, hands in frame, character looking at the viewer, etc.
	# Full first-person perspective-taking = 1; indirect perspective (over the shoulder) = 0.5; not annotated/objective perspective = 0
	# Not in TINTIN yet
	
	perspectivetaking <- data.frame(
		perspectiveclass = titledata$PerspectiveClas,
		perspectivescore = titledata$PerspectiveScore
	)

	variablesbytitle[t,15] = mean(perspectivetaking$perspectivescore, na.rm =TRUE)

################################
###############################
################################
	### Conventionalization of Panels ###------------------------------
	# Lots of different templates
	# Could analyze as:
		# Is this a conventionalized panel or not?
		# If it is, is it productive or not? (Some conventionalized panels are fixed, others are more flexible in how they can be depicted. More productive means more flexible.)
		# For all panels, panels NOT templatic = 1; productive = 0.5; fixed = 0 (because fixed are presumed to be easier or more familiar for those with higher fluency; although this is an assumption, no empirical data!)

# lexical productivity
# descriptive: subcategorized panels as productive or fixed, if none then it is not a template, template with free form slots
# numerical: fixed = 0  productive = 0.5, non-templatic = 1

	conventinalizationpanels <- data.frame(
		lexicalproductivty = titledata$Lexical_Productivity,
		lexicalproductivitynum = titledata$Lexical_ProductivityNum)

	variablesbytitle[t, 16] = mean(conventinalizationpanels$lexicalproductivitynum, na.rm = TRUE)

	### Avg Number of Characters per Panel ###--------------------------------------
	#takes the mean of number of characters per panel for the entire title
	
	#create a data frame to hold only characters per panel from title data
	charnumpanel <- data.frame()
	charnumpanel = (titledata$CharactersPerPanel)
	
	#calculate the mean number of characters in the whole title
	variablesbytitle[t,17] = mean(charnumpanel, na.rm = TRUE)


	### Total number of Characters per Story ###---------------
	# "Relations" in continuity schemes - but only for main characters. Only done for ~300 books
	# May want to drop this one, or look at it only in a subset of stories
	# not in TINTIN corpus


	### Text Complexity ### -------------------------------
	# Not sure if we want to include this one, if we want to restrict this (for now) to visual narrative complexity
	# We'd need to be able to extract the actual text from the comics, which I'm not sure we can do in MAST
	# Comics are also in a bunch of different languages so this would be difficult


	### Arousal and valence? We didn't propose this in the grant
	# Arousal = intensity, scale from 1-5
	arousal <- data.frame(
		arousalscore = titledata$Arousal
	)
	variablesbytitle[t,18] = mean(arousal$arousalscore, na.rm = TRUE)

	# Valence = positive/neutral/negative, 5-point scale (negative, slightly negative, neutral, slightly positive, positive)
		valence <- data.frame(
		valence = titledata$Valence,
		valencescore = titledata$Valence.1
	)
	variablesbytitle[t,19] = mean(valence$valencescore, na.rm = TRUE)

	# Demographics #-------------------
	#audience, style/origin, format, publication date, genre

	#audience
	# everyone = 0 , teen-adult = 0.5, adult =1
	audience <- data.frame(
		audience = titledata$Audience
	)
	#create loop for audience scoring
	audience$audiencescore = ifelse(audience$audience == "Adult", 1,
                           ifelse(audience$audience == "Teen-Adult", 0.5,
                           ifelse(audience$audience == "Everyone", 0 )))

	variablesbytitle[t,20]= mean(audience$audiencescore, na.rm = TRUE)
		


#}	# title loop

variablesbytitle = as.data.frame(variablesbytitle)



### Next try getting a numerical rating for each title, averaged over all variables


### Will also want to add in the demographic information for each story (e.g., target population)


### Will also need to extract all these variables for the VEA comprehension test strips



#######################################
### Methods we propose in the grant ###
#######################################

# For the purposes of this pilot work we will consider the following structural variables that can contribute to visual narrative complexity.  
# 1)	Layout complexity: This metric will be comprised of several variables, the scores of which will be averaged to create an overall “layout complexity” score. 
# 	a.	Panels per page: Comics with fewer panels per page will be relatively simpler to navigate than panels with multiple panels per page. 
# 	b.	Panel shapes: Square or rectangle panels are most common in comics, and will thus be simpler to understand, while other non-traditional shapes will be more complex. 
# 	c.	Borders: Panels with defined borders will be simpler to understand, whereas panels without clearly defined edges will require additional processing by the reader to understand where the edges of each panel lie. 
# 	d.	Panel layout/organization: Layouts using pure grids or whole rows tend to be simplest, whereas staggers add another level of complexity, and embedded columns (“blockages”) tend to be more complex.
# 	e.	Directionality: Left-to-right “Z-paths”, which mimic alphabetic writing systems, are simpler for readers familiar with alphabetic writing systems to understand than up-and-down columns or more complex paths in which panels are read.  
# 2)	Complexity of framing structure: “Macros” (panels depicting an entire scene) are more explicit in terms of semantic content, and should thus be easier to understand, compared to “monos” (panels depicting only one character or object) or “micros” (which show a “zoomed in” part of a character, object, or scene).
# 3)	Sequencing of images: Shifts in time maintaining full views of scenes are simpler than those that shift between views of characters, between viewpoints (i.e., zooms), between different perspectives (e.g., third to first person point-of-view), between different domains (e.g., from “reality” to a dream sequence or flashback), or that use idiosyncratic sequencing patterns (e.g., “cross-cutting” shifts back and forth between characters). 
# 4)	Backgrounds: Depicted backgrounds clearly show the spatial location and are easiest to comprehend relative to those with symbolic content or absent or impossible backgrounds.
# 5)	Situational coherence: Greater shifts between panels in various meaningful dimensions (e.g., time, spatial location, characters) will be harder to comprehend than fewer shifts.
# 6)	Compositional structure: Comic panels vary in how they depict information, such as the angle of viewpoint (lateral, high/low angles), shot scale (long shot to close up), or framing angle (straight or tilted content). More normative compositions (lateral angles, full shots, straight content) are considered easier to comprehend than more deviant compositions. 
# 7)	Perspective taking: Many comics show or imply a character’s perspective; panels without first person perspectives are simpler than those that show an implicit perspective, which are easier than those with an explicit first-person perspective.
# 8)	Conventionalization of panels: Just like language, comic panels vary from using highly regularized patterns to being novel and productive representations. While regularized templates are presumably simpler than novel images as they are entrenched in readers’ memories, they also reflect knowledge in the visual language people are exposed to. Here, higher percentages of templatic panels will reflect more complexity.
# 9)	Number of characters: We will consider both the number of characters per panel and the number of characters in the overall story, with more characters being more complex due to working memory demands. 
# 10)	Length: Longer comics will be more complex than shorter comics. 
# 11)	Text complexity: Since many comics incorporate both images and written text, the difficulty level of the text will be taken into account. Here we will consider both the number of words in a comic and the approximate grade level of the vocabulary used.

# To develop our ranking system, we will score the complexity of every comic in the TINTIN Corpus along each of these variables. Ordinal categories will be defined based on both theoretical reasoning and examination of frequency within the TINTIN Corpus and will be assigned a numerical code varying between 0 and 1, with non-integer values representing intermediate levels (e.g., 0=less complex; 0.5=moderately complex; 1=very complex). While we have described much of our theory above, the specific definitions of categories will be done as part of this project. Numerical raw scores (e.g., number of panels) will be normalized to a 0-1 scale using the minimum and maximum values observed in the TINTIN Corpus. Each variable listed above will thus have a range between 0 and 1, which will allow for averaging across variables to obtain a total complexity score. Individual subscale scores will also be retained to help with interpretation (e.g., a comic may have a complicated layout but a relatively straightforward compositional structure). 

# sanity check: panel alignment
if (!all(quad_diagnostics$Panel %in% titledata$PanelNum)) {
  warning("Mismatch between quad_diagnostics panels and original PanelNum")
}

#plotting panel shapes and pages
output_plots <- "./plots"
dir.create(output_plots, showWarnings = FALSE, recursive = TRUE)

safe_title <- title %>%
  iconv(from = "", to = "UTF-8", sub = "byte") %>%   # normalize encoding
  gsub("[^A-Za-z0-9_]", "_", .) %>%
  gsub("_+", "_", .) %>%
  gsub("^_|_$", "", .)

pdf(file.path(output_plots, paste0(safe_title, "_report.pdf")),
    width = 8, height = 8)

tryCatch({

    if (!exists("quad_diagnostics") || nrow(quad_diagnostics) == 0) {
	stop("quad_diagnostics is empty — no shapes were recorded")
	}

	pages <- unique(quad_diagnostics$Page_number)
	pages <- pages[!is.na(pages)]

	if (length(pages) == 0) {
	stop("No valid pages found in quad_diagnostics")
	}

	pages <- sort(pages)
	if (nrow(quad_diagnostics) == 0) {
		stop("quad_diagnostics is empty — no shapes were recorded")
		}

  for (pg in pages) {

    quad_df <- quad_diagnostics %>% 
      filter(Page_number == pg)
	quad_df <- quad_df %>%
  	  arrange(Page_number, Panel)

	#layout_label <- panel_layout_df %>%
    #filter(Page_Number == pg) %>%
    #pull(layout_type)

    #if (length(layout_label) == 0) layout_label <- "UNKNOWN"

    if (nrow(quad_df) == 0) next

    plot_df <- data.frame()

    for (i in seq_len(nrow(quad_df))) {

      row <- quad_df[i, ]

      if (is.na(row$coords) || row$coords == "") next

      coords_pairs <- str_split(row$coords, " \\| ")[[1]]

      coords_matrix <- do.call(rbind, lapply(coords_pairs, function(pair) {
		vals <- as.numeric(str_split(pair, ",")[[1]])
		if (length(vals) != 2 || any(is.na(vals))) return(NULL)
		vals
		}))

	  if (is.null(coords_matrix) || nrow(coords_matrix) < 2) next

      if (nrow(coords_matrix) < 2) next

      coords_matrix <- rbind(coords_matrix, coords_matrix[1, ])

      plot_df <- rbind(plot_df, data.frame(
		Panel = row$Panel,
		ComicPanel = row$ComicPanel,   # ← ADD
		x = coords_matrix[,1],
		y = coords_matrix[,2]
		))
    }

    if (nrow(plot_df) == 0) next

    centroids <- plot_df %>%
  group_by(Panel, ComicPanel) %>%
  summarise(x = mean(x), y = mean(y), .groups = "drop")

   p <- ggplot(plot_df, aes(x, y, group = Panel)) +
		geom_polygon(fill = NA, color = "black", size = 1) +

		geom_text(
			data = centroids,
			aes(x = x, y = y, label = ComicPanel),
			color = "black",
			size = 4
		) +

		coord_fixed() +
		scale_y_reverse() +   # <- add this
		theme_minimal() +
		labs(title = paste("Page", pg, "-"))#, layout_label))

    print(p)
  }

}, error = function(e) {
  message("Error occurred: ", e$message)
})

dev.off()