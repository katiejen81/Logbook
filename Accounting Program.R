
# Program Information -----------------------------------------------------

# Bookkeeping the Online Logbook Data
# Written by KTanner on May 29, 2017
# Files are located in /home/katie/Downloads/Mike Schedule


# Bring in libraries ------------------------------------------------------

library(dplyr)
library(readODS)
library(sqldf)
library(stringi)
library(data.table)


# Bring in data -----------------------------------------------------------

schedule <- read_ods('/home/katie/Downloads/Mike Schedule/Mike Export.ods')

logbook <- read_ods('/home/katie/Downloads/Mike Schedule/Crew Log (Responses).ods')


# Data Filtering and Clean ------------------------------------------------

## Normalize the column headers
list <- names(logbook)
list <- sub("\\s+", "_", list)
colnames(logbook) <- list

list <- names(schedule)
list <- sub("\\s+", "_", list)
list <- sub('/', '_', list)
colnames(schedule) <- list

## Only look at the actual flight time while at XJT (As opposed to old silver time or sim time)

logbook <- subset(logbook, logbook$AIRCRAFT_MAKE_AND_MODEL == 'EMB-145' & !grepl("Sim", logbook$AIRCRAFT_IDENT))

## Only look at flights that have already happened and clean up dates

schedule$Date_new <- as.Date(schedule$Date, "%m/%d/%Y")
logbook$DATE_new <- as.Date(logbook$DATE, "%m/%d/%Y")

schedule <- subset(schedule, schedule$Date_new < as.Date('2017-05-31', format='%Y-%m-%d'))

## Getting weird errors in SQLDF - let's rename some columns
logbook$Origin <- stri_sub(logbook$FROM, -3, -1)
logbook$Dest <- stri_sub(logbook$TO, -3, -1)

## And we are getting duplicates in our SQL Query - We need to match on another key
## Let's use the last three digits of the tail number

logbook$Tail3 <- stri_sub(logbook$AIRCRAFT_IDENT, -3, -1)
schedule$Tail3 <- stri_sub(schedule$Tail, -3, -1)


## Now let's see what is missing from the logbook

missing_logbook <- sqldf('select a.Date, a.Tail, a.Origin, a.Dest, a.Block, a.Credit
                         from schedule as a
                         left join logbook b 
                         ON (a.Date_new = b.DATE_new
                         AND upper(a.Origin) = upper(b.Origin)
                         AND upper(a.Dest) = upper(b.Dest))
                         where b.DATE is NULL')

## There is still something missing. Let's look

logbook$Month <- format(logbook$DATE_new, '%Y-%m')
schedule$Month <- format(schedule$Date_new, '%Y-%m')

logbook_count <- count(logbook, as.character(logbook$Month))
schedule_count <- count(schedule, as.character(schedule$Month))
colnames(logbook_count) <- c("Month", "Count")
colnames(schedule_count) <- c("Month", "Count")

total_count <- merge(logbook_count, schedule_count, by="Month")

difference <- subset(total_count, Count.x != Count.y)

### There was a duplicate in the export. Removing and moving on

# Compare the total time to block time ------------------------------------

schedule$Depart <- as.character(schedule$Depart)
schedule$Arrive <- as.character(schedule$Arrive)

comparison <- sqldf('SELECT DISTINCT a.*, b.*
                    FROM logbook a
                    LEFT JOIN schedule b
                    ON (a.DATE_new = b.Date_new
                    AND upper(a.Origin) = upper(b.Origin)
                    AND upper(a.Dest) = upper(b.Dest)
                    AND a.Tail3 = b.Tail3)')

missing <- subset(comparison, is.na(comparison$Block) == TRUE)

## Let's remove the duplicates

comparison$Distance <- abs(comparison$TOTAL_DURATION_OF_FLIGHT - comparison$Block)

comparison <- comparison[order(comparison$Timestamp, comparison$DATE, comparison$AIRCRAFT_IDENT, comparison$FROM, comparison$TO, comparison$TOTAL_DURATION_OF_FLIGHT, comparison$APPROACH, comparison$Distance),]

test<- comparison[!duplicated(comparison[,c("Timestamp", "DATE", "AIRCRAFT_IDENT", "FROM", "TO", "TOTAL_DURATION_OF_FLIGHT", "APPROACH")]),]

## Compare the number of hours

logbook_total <- sum(test$TOTAL_DURATION_OF_FLIGHT)
schedule_total <- sum(test$Block)

sum_of_errors <- sum(test$Distance)

df <- test[order(-test$Distance), ]

df$true_distance <- df$TOTAL_DURATION_OF_FLIGHT - df$Block

sum_of_errors_true <- sum(df$true_distance)


## Write out to a new file

test$TOTAL_DURATION_OF_FLIGHT <- test$Block
test$`AIRPLANE_MULTI-ENGINE_LAND` <- test$Block
test$SECOND_IN_COMMAND <- test$Block
test$DATE <- test$DATE_new

write <- test[order(test$DATE), ]
write <- test[, c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18)]
write <- write[order(write$DATE), ]

list <- names(write)
list <- sub("_", " ", list)
colnames(write) <- list

write.csv(write, '/home/katie/Downloads/Mike Schedule/XJT_Logbook_CLEAN.csv', na=" ")