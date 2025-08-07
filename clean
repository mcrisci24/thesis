library(mosaic)
library(tidyverse)
library(readxl)

# Income distribution file to be merged into PSID data
percentiles <- read_xlsx("C:/Users/markc/Downloads/IncomeDistribution.xlsx")
head(percentiles)


psid <- read_xlsx("C:/Users/markc/Downloads/J348297 PSID data.xlsx")
summary(ER30012$J348)

dim(J348)
# Last column would not appear so had to do this to the variable name
as.data.frame(percentiles)
print(percentiles, n = 6, width = Inf)
percentiles$`Lower limit\nof top 5\npercent\n(dollars)`
names(percentiles)[7] <- "Top5_LowerLimit"
head(percentiles)
# Force-print with all 7 columns
print(percentiles, width = Inf)
names(percentiles)


# Number summaries
summary(percentiles$Year)

summary(percentiles$`Numbers (In Thousands)`)

summary(percentiles$Lowest)

summary(percentiles$Second)

summary(percentiles$Third)

summary(percentiles$Fourth)

summary(percentiles$Top5_LowerLimit)

# Load percentiles file (optional – used for comparisons)
percentiles <- read_xlsx("C:/Users/markc/Downloads/IncomeDistribution.xlsx")
names(percentiles)[7] <- "Top5_LowerLimit"





# ------- Clean & Subset Data --------

library(tidyverse)
library(readxl)
library(mosaic)
library(ggplot2)
library(readr)



# data
psid <- read_xlsx("C:/Users/markc/Downloads/J348297 PSID data.xlsx")
colnames(psid)
unique(psid$ER30022)
summary(psid$ER30069)

# Check first 10 rows and all relationship columns for 1968-1971
psid %>%
  select(ER30001, ER30002, ER30003, ER30022, ER30045, ER30069) %>%
  head(10)


# define ID and Income columns
id_cols <- c("ER30001", "ER30002")  # Household and Person IDs


# MONEY INCOMES NOT USED IN FINAL ANALYSIS----
# list of all income variables by year
#income_cols <- c(
#  "V74", # Heads labor income 1967
#  "V514",# '68
#  "V1196", #'69
#  "ER30033", # Money Income '68
#  "ER30057", "ER30081", "ER30106", "ER30130", "ER30152",
#  "ER30173", "ER30202", "ER30231", "ER30268", "ER30298", "ER30328", "ER30358",
#  "ER30386", "ER30415", "ER30445", "ER30480", "ER30515", "ER30551", "ER30586",
#  "ER30622", "ER30659", "ER30705", "ER30750", "ER30821", "ER4140",#<-- up to 1993
#  "ER27397",  # 1996
#  "ER28738",  # 1999
#  "ER29485",  # 2001
#  "ER30196",  # 2003
#  "ER41005",  # 2005
# "ER46913",  # 2007
#  "ER52334",  # 2009
#  "ER58251",  # 2011
#  "ER65487",  # 2013
#  "ER71566",  # 2015
#  "ER71293",  #2016 
# "ER77587",  # 2017
# "ER77315",  # 2018 GOOD
# "ER83534",   #2019 FIX THIS & ABOVE ^
#  "ER81642", # 2020 GOOD
#  "ER85496", # 2022 GOOD
#)

#subset and rename
psid_income <- psid %>%
  select(all_of(c(id_cols, income_cols)))

colnames(psid_income) <- c(
  "HH_ID", "PERSON_ID",
  paste0("Income_", c(
    1971:1995,
    1996, 1997, 1999, 2001, 2003, 2005,
    2007, 2009, 2011, 2013, 2015, 2017, 2019
  ))
)

# Plots
# Convert to long format
psid_long <- psid_income %>%
  pivot_longer(
    cols = starts_with("Income_"),
    names_to = "year",
    names_prefix = "Income_",
    values_to = "income"
  ) %>%
  mutate(year = as.numeric(year))
view(psid_income)
# Plot income over time by individual
ggplot(psid_long, aes(x = year, y = income, group = PERSON_ID)) +
  geom_line(alpha = 0.2) +
  labs(title = "Income over Time by Individual",
       x = "Year", y = "Total Family Income (Head Labor)") +
  theme_minimal()

# save to CSV
write.csv(psid_income, "psid_income_71_19.csv", row.names = FALSE)

income_long





# Plan to complete the following tasks:
# 1. Plot the "Total labor income of head" variable dynamics for each given row
# 2. Try plotting "TOTAL LABOR/MONEY/TAXABLE INCOME" variables up until 1993
# 3. Compare the  "Total labor income of head" &  "TOTAL LABOR/MONEY/TAXABLE INCOME" variable dynamics from 1968 to 1993 (trying overlapping their plots for the same row, see how they differ)

# ---------------ONLY ENDED UP USING HEAD LABOR INCOME VARIABLES AND YEAR alongside identifier variables---------------------
library(tidyverse)
library(readxl)
library(ggplot2)
library(dplyr)

# PSID data
psid <- read_xlsx("C:/Users/markc/Downloads/J348297 PSID data.xlsx")

# Household and Person IDs
id_cols <- c("ER30001", "ER30002") 

psid.Mfile <- read_xlsx("C:/Users/markc/Downloads/M348297 PSID data.xlsx")
colnames(psid.Mfile)
psid.Jfile <- read_csv("C:/Users/markc/Downloads/PSID_J.csv")
colnames(psid.Jfile)


table(psid.Jfile$ER30003)


#head(head_labor_income)
#view(head_labor_income)

# Head Labor income variables
head_labor_vars <- c(
  "V514", "V1196", "V1897", "V2498", "V3051", "V3463", "V3863", "V5031", "V5627", "V6174",
  "V6767", "V7413", "V8066", "V8690", "V9376", "V11023", "V12372", "V13624", "V14671", "V16145",
  "V17534", "V18878", "V20178", "V21484", "ER30750", "ER4140", "ER6980", "ER9231", "ER16463",
  "ER20443", "ER24116", "ER27931", "ER40921", "ER46829", "ER52237", "ER58038", "ER65216",
  "ER71293", "ER77315", "ER81642", "ER85496"
)
head_labor_years <- c(
  1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983,
  1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1998, 2000, 2002, 2004,
  2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022
)

# # TOTAL MONEY/TAXABLE INCOME variables & years (NOT USED ANYMORE)
# total_money_vars <- c(...)
# total_money_years <- 1968:1993
summary(dream92$head_labor_vars)


# Relationship to head variable and years (unchanged)
rel_vars <- c(
  "ER30003", "ER30022", "ER30045", "ER30069", "ER30093", "ER30119", "ER30140", "ER30162", "ER30190", "ER30219",
  "ER30248", "ER30285", "ER30315", "ER30345", "ER30375", "ER30401", # 1968–1982
  "ER30431", "ER30465", "ER30500", "ER30537", "ER30572", "ER30608", "ER30644", "ER30691", "ER30735",
  "ER30808", "ER33103", "ER33203", "ER33303", "ER33403", "ER33503", "ER33603", "ER33703", "ER33803", "ER33903",
  "ER34003", "ER34103", "ER34203", "ER34303", "ER34503", "ER34703", "ER34903", "ER35103"
)

rel_years <- c(
  1968:1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1999,
  2001, 2003, 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021, 2023
)



# VARIABLES BELOW ARE FOR FUTURE WORK
sex_hd <- c(
  "V119", "V1010", "V1240", "V1943", ""
)


age_hd <- c(
  "V1008", "V1239","V1942", "V2542", "V3095", "V3508", "V3921", "V4436", "V5350", "V5850", "V6462", "V7067", 
  "V7658", "V8352", "V8961", "V10419", "V11606", "V13011", "V14114", "V15130", "V16631", "V18049", "V19349",
  "V20651", "V22406", "ER2007", "ER5006", "ER7006", "ER10009", "ER13010", "ER17013", "ER33604", "ER21017",
  "ER25017", "ER36017", "ER42017", "ER47317", "ER53017", "ER60017", "ER66017", "ER72017", "ER78017", "ER82018"
)

age_ind <- c(
  "ER30004","ER30023", "ER30046", "ER30070", "ER30094", "ER30120", "ER30141", "ER30163", "ER30191", "ER30220",
  "ER30249", "ER30286", "ER30316", "ER30346", "ER30376", "ER30402", "ER30432", "ER30466", "ER30501", "ER30538", 
  "ER30573", "ER30609", "ER30645", "ER30692", "ER30736", "ER30809", "ER33104", "ER33204", "ER33304", "ER33404",
  "ER33504", "ER33704", "ER33804", "ER33904", "ER34004", "ER34104", "ER34204", "ER34305", "ER34504", "ER34704",
  "ER34904", "ER35104"
)



race <- c(
  "V181", "V801", "V1490", "V2202", "V2828", "V3300", "V3720", "V4204", "V5096", "V5662", "V6209",
  "V6802", "V7447", "V8099", "V8723", "V9408", "V11055", "V11938", "V13565", "V14612", "V16086",
  "V17483", "V18814", "V20114", "V21420", "V23276", "ER3944", "ER6814", "ER9060", "ER11848", "ER15928",
  "ER19989", "ER23426", "ER27393", "ER40565", "ER46543", "ER51904", "ER57659", "ER64810", "ER70882",
  "ER76897","ER81144", "ER85121"
)

# A20 HOUSE VALUE variables 68-23
house_value <- c(
  "V5", "V449", "V1122", "V1823", "V2423", "V3021", "V3417", 
  "V3817", "V4318", "V5217", "V5717", "V6319", "V6917", "V7517",
  "V8217", "V8817", "V10018", "V11125", "V12524", "V13724", "V14824",
  "V16324", "V17724", "V19024", "V20324", "V21610", "ER2033", "ER5032",
  "ER7032", "ER10036", "ER13041", "ER17044", "ER21043", "ER25029",
  "ER36029", "ER42030", "ER47330", "ER53030", "ER60031", "ER66031",
  "ER72031", "ER78032", "ER82033"
)

state_grew_hd <- c(
  "V311", "V787", "V1477", ""
)

parents_poor_hd <- c(
  "V317",   # 1968
  "V792",   # 1969
  "V1483",  # 1970
  "V2195",  # 1971
  "V2821",  # 1972
  "V3239",  # 1973
  "V3661",  # 1974
  "V4680",  # 1975
  "V5600",  # 1976
  "V6149",  # 1977
  "V6746",  # 1978
  "V7379",  # 1979
  "V8031",  # 1980
  "V8655",  # 1981
  "V9320",  # 1982
  "V9969",  # 1983
  "V10645", # 1984
  "V11276", # 1985
  "V11925", # 1986
  "V12568", # 1987
  "V13236", # 1988
  "V13917", # 1989
  "V14583", # 1990
  "V15229", # 1991
  "V15919", # 1992
  "V16596", # 1993
  "V17265", # 1994
  "V17928", # 1995
  "V18619", # 1996
  "V19293", # 1997
  "V19966", # 1999
  "V20626", # 2001
  "V21287", # 2003
  "V21946", # 2005
  "V22606", # 2007
  "V23266", # 2009
  "V23926", # 2011
  "V24586", # 2013
  "V25246", # 2015
  "V25906", # 2017
  "V26566", # 2019
  "V27226", # 2021
  "V27886"  # 2023
)

# Father_edu hd
father_edu_hd <- c(
  "V318",   # 1968
  "V793",   # 1969
  "V1484",  # 1970
  "V2196",  # 1971
  "V2822",  # 1972
  "V3240",  # 1973
  "V3662",  # 1974
  "V4681",  # 1975
  "V5601",  # 1976
  "V6150",  # 1977
  "V6747",  # 1978
  "V7380",  # 1979
  "V8032",  # 1980
  "V8656",  # 1981
  "V9321",  # 1982
  "V9970",  # 1983
  "V10646", # 1984
  "V11277", # 1985
  "V11926", # 1986
  "V12569", # 1987
  "V13237", # 1988
  "V13918", # 1989
  "V14584", # 1990
  "V15230", # 1991
  "V15920", # 1992
  "V16597", # 1993
  "V17266", # 1994
  "V17929", # 1995
  "V18620", # 1996
  "V19294", # 1997
  "V19967", # 1999
  "V20627", # 2001
  "V21288", # 2003
  "V21947", # 2005
  "V22607", # 2007
  "V23267", # 2009
  "V23927", # 2011
  "V24587", # 2013
  "V25247", # 2015
  "V25907", # 2017
  "V26567", # 2019
  "V27227", # 2021
  "V27887"  # 2023
)


other_training <- c(
  "V314",   # 1968
  "V795",   # 1969
  "V1486",  # 1970
  "V2198",  # 1971
  "V2824",  # 1972
  "V3242",  # 1973
  "V3664",  # 1974
  "V4685",  # 1975
  "V5609",  # 1976
  "V6158",  # 1977
  "V6755",  # 1978
  "V7388",  # 1979
  "V8040",  # 1980
  "V8664",  # 1981
  "V9322",  # 1982
  "V9972",  # 1983
  "V10648", # 1984
  "V11279", # 1985
  "V11928", # 1986
  "V12571", # 1987
  "V13239", # 1988
  "V13920", # 1989
  "V14586", # 1990
  "V15232", # 1991
  "V15922", # 1992
  "V16599", # 1993
  "V17268", # 1994
  "V17931", # 1995
  "V18622", # 1996
  "V19296", # 1997
  "V19969", # 1999
  "V20629", # 2001
  "V21290", # 2003
  "V21949", # 2005
  "V22609", # 2007
  "V23269", # 2009
  "V23929", # 2011
  "V24589", # 2013
  "V25249", # 2015
  "V25909", # 2017
  "V26569", # 2019
  "V27229", # 2021
  "V27889"  # 2023
)



region_now <- c(
  "V361",   # 1968
  "V876",   # 1969
  "V1572",  # 1970
  "V2284",  # 1971
  "V2911",  # 1972
  "V3279",  # 1973
  "V3699",  # 1974
  "V5054",  # 1975
  "V5633",  # 1976
  "V6180",  # 1977
  "V6773",  # 1978
  "V7419",  # 1979
  "V8071",  # 1980
  "V8695",  # 1981
  "V9365",  # 1982
  "V10013", # 1983
  "V10691", # 1984
  "V11331", # 1985
  "V11993", # 1986
  "V12652", # 1987
  "V13331", # 1988
  "V14017", # 1989
  "V14695", # 1990
  "V15349", # 1991
  "V16039", # 1992
  "V16721", # 1993
  "V17399", # 1994
  "V18067", # 1995
  "V18755", # 1996
  "V19425", # 1997
  "V20099", # 1999
  "V20759", # 2001
  "V21419", # 2003
  "V22079", # 2005
  "V22739", # 2007
  "V23399", # 2009
  "V24059", # 2011
  "V24719", # 2013
  "V25379", # 2015
  "V26039", # 2017
  "V26699", # 2019
  "V27359", # 2021
  "V28019"  # 2023
)



region_hd_grew <- c(
  "V362",   # 1968
  "V877",   # 1969
  "V1573",  # 1970
  "V2285",  # 1971
  "V2912",  # 1972
  "V3280",  # 1973
  "V3700",  # 1974
  "V5055",  # 1975
  "V5634",  # 1976
  "V6181",  # 1977
  "V6774",  # 1978
  "V7420",  # 1979
  "V8072",  # 1980
  "V8696",  # 1981
  "V9366",  # 1982
  "V10014", # 1983
  "V10692", # 1984
  "V11332", # 1985
  "V11994", # 1986
  "V12653", # 1987
  "V13332", # 1988
  "V14018", # 1989
  "V14696", # 1990
  "V15350", # 1991
  "V16040", # 1992
  "V16722", # 1993
  "V17400", # 1994
  "V18068", # 1995
  "V18756", # 1996
  "V19426", # 1997
  "V20100", # 1999
  "V20760", # 2001
  "V21420", # 2003
  "V22080", # 2005
  "V22740", # 2007
  "V23400", # 2009
  "V24060", # 2011
  "V24720", # 2013
  "V25380", # 2015
  "V26040", # 2017
  "V26700", # 2019
  "V27360", # 2021
  "V28020"  # 2023
)


geo_mobility <- c(
  "V363",   # 1968
  "V878",   # 1969
  "V1576",  # 1970
  "V2288",  # 1971
  "V2915",  # 1972
  "V3283",  # 1973
  "V3703",  # 1974
  "V5058",  # 1975
  "V5637",  # 1976
  "V6184",  # 1977
  "V6777",  # 1978
  "V7423",  # 1979
  "V8075",  # 1980
  "V8699",  # 1981
  "V9369",  # 1982
  "V10017", # 1983
  "V10695", # 1984
  "V11335", # 1985
  "V11997", # 1986
  "V12656", # 1987
  "V13335", # 1988
  "V14021", # 1989
  "V14699", # 1990
  "V15353", # 1991
  "V16043", # 1992
  "V16725", # 1993
  "V17403", # 1994
  "V18071", # 1995
  "V18759", # 1996
  "V19429", # 1997
  "V20103", # 1999
  "V20763", # 2001
  "V21423", # 2003
  "V22083", # 2005
  "V22743", # 2007
  "V23403", # 2009
  "V24063", # 2011
  "V24723", # 2013
  "V25383", # 2015
  "V26043", # 2017
  "V26703", # 2019
  "V27363", # 2021
  "V28023"  # 2023
)



state_now <- c(
  "V537",   # 1968
  "V1103",  # 1969
  "V1803",  # 1970
  "V2403",  # 1971
  "V3003",  # 1972
  "V3403",  # 1973
  "V3803",  # 1974
  "V4303",  # 1975
  "V5203",  # 1976
  "V5703",  # 1977
  "V6303",  # 1978
  "V6903",  # 1979
  "V7503",  # 1980
  "V8203",  # 1981
  "V8803",  # 1982
  "V9403",  # 1983
  "V10003", # 1984
  "V10603", # 1985
  "V11203", # 1986
  "V11803", # 1987
  "V12403", # 1988
  "V13003", # 1989
  "V13603", # 1990
  "V14203", # 1991
  "V14803", # 1992
  "V15403", # 1993
  "V16003", # 1994
  "V16603", # 1995
  "V17203", # 1996
  "V17803", # 1997
  "V18403", # 1999
  "V19003", # 2001
  "V19603", # 2003
  "V20203", # 2005
  "V20803", # 2007
  "V21403", # 2009
  "V22003", # 2011
  "V22603", # 2013
  "V23203", # 2015
  "V23803", # 2017
  "V24403", # 2019
  "V25003", # 2021
  "V25603"  # 2023
)


state_hd_grew <- c(
  "V787",   # 1969
  "V1477",  # 1970
  "V2189",  # 1971
  "V2815",  # 1972
  "V3233",  # 1973
  "V3655",  # 1974
  "V4674",  # 1975
  "V5594",  # 1976
  "V6143",  # 1977
  "V6740",  # 1978
  "V7373",  # 1979
  "V8025",  # 1980
  "V8649",  # 1981
  "V9313",  # 1982
  "V9964",  # 1983
  "V10639", # 1984
  "V11270", # 1985
  "V11919", # 1986
  "V12562", # 1987
  "V13230", # 1988
  "V13911", # 1989
  "V14577", # 1990
  "V15223", # 1991
  "V15913", # 1992
  "V16590", # 1993
  "V17259", # 1994
  "V17922", # 1995
  "V18613", # 1996
  "V19287", # 1997
  "V19960", # 1999
  "V20620", # 2001
  "V21281", # 2003
  "V21940", # 2005
  "V22600", # 2007
  "V23260", # 2009
  "V23920", # 2011
  "V24580", # 2013
  "V25240", # 2015
  "V25900", # 2017
  "V26560", # 2019
  "V27220", # 2021
  "V27880"  # 2023
)

state_grew_hd <- c(
  # 1968–1977
  "V311",   # 1968
  "V787",   # 1969
  "V1477",  # 1970
  "V2189",  # 1971
  "V2815",  # 1972
  "V3233",  # 1973
  "V3655",  # 1974
  "V4674",  # 1975
  "V5594",  # 1976
  "V6143",  # 1977
  # 1978–1987
  "V6740",  # 1978
  "V7373",  # 1979
  "V8025",  # 1980
  "V8649",  # 1981
  "V9313",  # 1982
  "V9964",  # 1983
  "V10639", # 1984
  "V11270", # 1985
  "V11919", # 1986
  "V12562", # 1987
  # 1988–1997
  "V13230", # 1988
  "V13911", # 1989
  "V14577", # 1990
  "V15223", # 1991
  "V15913", # 1992
  "V16590", # 1993
  "V17259", # 1994
  "V17922", # 1995
  "V18613", # 1996
  "V19287", # 1997
  # 1999–2023: You need to check your exact PSID release! (Often these jump by 600–700 for each biennial year)
  "V19960", # 1999
  "V20620", # 2001
  "V21281", # 2003
  "V21940", # 2005
  "V22600", # 2007
  "V23260", # 2009
  "V23920", # 2011
  "V24580", # 2013
  "V25240", # 2015
  "V25900", # 2017
  "V26560", # 2019
  "V27220", # 2021
  "V27880"  # 2023
)



state_now <- c(
  "V537", "V1103", "V1803", ""
)


state_hd_grew <- c(
  "V787", "V1477", "V2189", ""
)






rel_lookup <- tibble(rel_var = rel_vars, year = rel_years)
rel_lookup

head_labor_income <- psid %>%
  select(all_of(c(id_cols, head_labor_vars)))

# Correctly rename ONLY the income columns
names(head_labor_income)[-(1:2)] <- paste0("HeadLabor_", head_labor_years)

# THEN add family_person as new column at the end
head_labor_income <- head_labor_income %>%
  mutate(family_person = paste(ER30001, ER30002, sep = "_"))

# Convert from wide format to long because in wide each year is a seperate column. 
# Long is necessary for time-series analysis
head_labor_long <- head_labor_income %>%
  pivot_longer(
    cols = starts_with("HeadLabor_"),
    names_to = "year",
    names_prefix = "HeadLabor_",
    values_to = "head_labor_income"
  ) %>% 
  mutate(year = as.numeric(year))

# Instead, just use head_labor_long as main "income_long":
income_long <- head_labor_long

# total_money_income <- psid %>%
#   select(all_of(c(id_cols, total_money_vars))) %>%
#   mutate(family_person = paste(ER30001, ER30002, sep = "_"))
# names(total_money_income)[-(1:2)] <- paste0("MoneyIncome_", total_money_years)
# total_money_long <- total_money_income %>%
#   pivot_longer(
#     cols = starts_with("MoneyIncome_"),
#     names_to = "year",
#     names_prefix = "MoneyIncome_",
#     values_to = "money_income"
#   ) %>% mutate(year = as.numeric(year))

# # Also comment out this join (NO LONGER NEEDED)
# income_long <- left_join(head_labor_long, total_money_long,
#                          by = c("ER30001", "ER30002", "year", "family_person"))


view(income_long)


# --- Relationship to Head
rel_long <- psid %>%
  select(all_of(c(id_cols, rel_vars))) %>%
  pivot_longer(
    cols = -all_of(id_cols),
    names_to = "rel_var",
    values_to = "relation_code"
  ) %>%
  left_join(rel_lookup, by = "rel_var") %>%
  mutate(relation_code = as.numeric(relation_code))



relation_labels_68_82 <- c(
  "1" = "Head",
  "2" = "Wife",
  "3" = "Son/Daughter",
  "4" = "Brother/Sister",
  "5" = "Parent",
  "6" = "Grandchild/Niece/Nephew/<18",
  "7" = "Other/In-law/Other Adult",
  "8" = "Spouse moved/died prior year",
  "9" = "NA", 
  "0" = "Inap./New Sample"
)

rel_long <- rel_long %>%
  mutate(
    relation_label = case_when(
      year <= 1982 ~ dplyr::recode(as.character(relation_code), !!!relation_labels_68_82),
      year > 1982 & year < 2017 ~ case_when(
        relation_code == 10 ~ "Head",
        relation_code == 20 ~ "Legal Spouse",
        relation_code == 22 ~ "Non-Legal Spouse",
        relation_code == 30 ~ "Son or daughter",
        relation_code == 33 ~ "Stepchild of Head",
        relation_code == 35 ~ "Stepchild of Spouse",
        relation_code == 37 ~ "Son or Daughter-in-law of Head",
        relation_code == 38 ~ "Foster child",
        relation_code == 40 ~ "Brother or sister of Head",
        relation_code == 47 ~ "Sibling-in-law of Head",
        relation_code == 48 ~ "Sibling of Head's cohabitor",
        relation_code == 50 ~ "Parent of Head",
        relation_code == 57 ~ "Parent-in-law of Head",
        relation_code == 58 ~ "Parent of Head's cohabitor",
        relation_code == 60 ~ "Grandchild of Head",
        relation_code == 65 ~ "Great Grandchild of Head",
        relation_code == 66 ~ "Grandparent of Head",
        relation_code == 67 ~ "Grandparent of Legal Spouse",
        relation_code == 68 ~ "Great Grandparent of Head",
        relation_code == 69 ~ "Great Grandparent of Legal Spouse",
        relation_code == 70 ~ "Nephew or Niece of Head",
        relation_code == 71 ~ "Nephew or Niece of Legal Spouse",
        relation_code == 72 ~ "Uncle or Aunt of Head",
        relation_code == 73 ~ "Uncle or Aunt of Legal Spouse",
        relation_code == 74 ~ "Cousin of Head",
        relation_code == 75 ~ "Cousin of Legal Spouse",
        relation_code == 83 ~ "Child of first year cohabitor not head",
        relation_code == 88 ~ "First-year cohabitor of Head",
        relation_code == 90 ~ "Legal Husband of Head",
        relation_code == 92 ~ "Uncooperative Legal Spouse of Head",
        relation_code == 95 ~ "Other relative of Head",
        relation_code == 96 ~ "Other relative of Legal Spouse",
        relation_code == 97 ~ "Other relative of cohabitor",
        relation_code == 98 ~ "Other nonrelatives",
        relation_code == 0 ~ "Inap.: from Immigrant sample",
        TRUE ~ "Other"
      ),
      year >= 2017 ~ case_when(
        relation_code == 10 ~ "Reference Person",
        relation_code == 20 ~ "Legal Spouse/Partner",
        relation_code == 22 ~ "Non-legal Spouse/Partner",
        relation_code == 30 ~ "Child",
        relation_code == 33 ~ "Stepchild of Reference Person",
        relation_code == 35 ~ "Stepchild of Spouse",
        relation_code == 37 ~ "Son or Daughter-in-law of Reference Person",
        relation_code == 38 ~ "Foster child",
        relation_code == 40 ~ "Brother or sister of Reference Person",
        relation_code == 47 ~ "Sibling-in-law of Reference Person",
        relation_code == 48 ~ "Sibling of Reference Person's cohabitor",
        relation_code == 50 ~ "Parent of Reference Person",
        relation_code == 57 ~ "Parent-in-law of Reference Person",
        relation_code == 58 ~ "Parent of Reference Person's cohabitor",
        relation_code == 60 ~ "Grandchild of Reference Person",
        relation_code == 65 ~ "Great Grandchild of Reference Person",
        relation_code == 66 ~ "Grandparent of Reference Person",
        relation_code == 67 ~ "Grandparent of Legal Spouse",
        relation_code == 68 ~ "Great Grandparent of Reference Person",
        relation_code == 69 ~ "Great Grandparent of Legal Spouse",
        relation_code == 70 ~ "Nephew or Niece of Reference Person",
        relation_code == 71 ~ "Nephew or Niece of Legal Spouse",
        relation_code == 72 ~ "Uncle or Aunt of Reference Person",
        relation_code == 73 ~ "Uncle or Aunt of Legal Spouse",
        relation_code == 74 ~ "Cousin of Reference Person",
        relation_code == 75 ~ "Cousin of Legal Spouse",
        relation_code == 83 ~ "Child of first year cohabitor not Reference Person",
        relation_code == 88 ~ "First-year cohabitor of Reference Person",
        relation_code == 90 ~ "Legal Husband of Reference Person",
        relation_code == 92 ~ "Uncooperative Legal Spouse of Reference Person",
        relation_code == 95 ~ "Other relative of Reference Person",
        relation_code == 96 ~ "Other relative of Legal Spouse",
        relation_code == 97 ~ "Other relative of cohabitor",
        relation_code == 98 ~ "Other nonrelatives",
        relation_code == 0 ~ "Inap.: from Immigrant sample",
        TRUE ~ "Other"
      )
    )
  )



income_long <- income_long %>%
  left_join(
    rel_long %>% select(ER30001, ER30002, year, relation_code, relation_label),
    by = c("ER30001", "ER30002", "year")
  )



#rel_long_valid <- rel_long %>% 
#  filter(relation_code != 0)

table(income_long$relation_label)

# Checking that all relation codes are present because 0-9 for the years 1968-1982 are not showing
table(psid)
View(rel_long)
table(income_long$relation_code)
income_
table(income_relation_long$relation_code)
table(rel_long$relation_code)
table(psid$ER30045)
table(psid_$ER30069)
table(income_relation_long$relation_code)
table(psid$ER30431)
table(psid$ER30500)

View(psid[, c("ER30001", "ER30002", "ER30003", "ER30022", "ER30045")])
summary(psid$ER300069)
head(dream)

# Pick a person and see how it looks 
# I tried different types of plots to try to visualize something
person_id <- income_relation_long$family_person[500]
income_one <- filter(income_relation_long, family_person == person_id)

ggplot(income_one, aes(x = year)) +
  geom_line(aes(y = head_labor_income), color = "blue", size = 1.5) +
  labs(title = paste("Income Trajectory: Person", person_id),
       x = "Year", y = "Income") +
  theme_minimal()

head(income_one)
dim(income_one)
view(income_one)

# Scatter plot for incomes
ggplot(income_one, aes(x = year)) +
  geom_point(aes(y = head_labor_income), color = "blue", size = 2, alpha = 0.7) +
  labs(
    title = paste("Scatter Plot: Income by Year for Person", person_id),
    x = "Year", y = "Income"
  ) +
  theme_minimal()



# NEW data frame for plots is called rel_long

# Merge the long income and relation data
income_relation_long <- head_labor_long %>%
  left_join(
    rel_long %>% select(ER30001, ER30002, year, relation_code, relation_label),
    by = c("ER30001", "ER30002", "year")
  )

dim(income_relation_long)
dim(head_labor_long)
view(head(income_relation_long))
view(head_labor_long)
head

family_id <- 4
family_data <- income_relation_long %>% filter(ER30001 == family_id)
view(family_data)
table(income_relation_long$relation_code)
# Plot to explore of all members of a given family colored by relation
ggplot(family_data, aes(x = year, y = head_labor_income, color = relation_label, group = ER30002)) +
  geom_line(size = 1.1, alpha = 0.8) +
  facet_wrap(~ relation_label, ncol = 1, scales = "free_y") +
  labs(
    title = paste("Income Trajectories by Relation: Family", family_id),
    x = "Year", y = "Head Labor Income", color = "Relation to Head"
  ) +
  theme_minimal()


# This plot shows all families colored by relation
ggplot(income_relation_long, aes(x = year, y = head_labor_income, color = relation_label, group = family_person)) +
  geom_line(alpha = 0.15) +
  stat_summary(aes(group = relation_label), fun = mean, geom = "line", size = 1.5) +
  labs(
    title = "Average Income Trajectories by Relation to Head",
    x = "Year", y = "Head Labor Income"
  ) +
  theme_minimal()


# Boxplot of income by relationship to head type
# For a specific year
latest_year <- max(income_relation_long$year, na.rm = TRUE)
income_relation_long %>%
  filter(year == latest_year) %>%
  ggplot(aes(x = relation_label, y = head_labor_income)) +
  geom_boxplot(outlier.alpha = 0.3, fill = "lightblue") +
  labs(title = paste("Income by Relation Type in", latest_year), x = "Relation", y = "Head Labor Income") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))


# Violin plot across 68-23 ehhhh...not great
ggplot(income_relation_long, aes(x = relation_label, y = head_labor_income)) +
  geom_violin(fill = "lightgray") +
  labs(title = "Distribution of Income by Relation (All Years)", x = "Relation", y = "Head Labor Income") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))


# Hiistogram income by relation
ggplot(income_relation_long, aes(x = head_labor_income)) +
  geom_histogram(bins = 50, fill = "blue", alpha = 0.5) +
  labs(title = "Distribution of Head Labor Income", x = "Income", y = "Count") +
  theme_minimal()




# ------------- Income Distribution Quintiles ---------------

library(dplyr)
library(ggplot2)
library(purrr)
library(readr)

quintiles <- read_xlsx("C:/Users/markc/Downloads/IncomeDistribution.xlsx")

head(quintiles)

# Check how year variable is 
head(income_long)
# YEAR variables are weird and I have to fix them to merge datasets rabble rabble rabble arbdbajsbdgads

# Year variables are set as characters in both dataframes
#quintiles <- quintiles %>%
#  mutate(year = as.character(year))

#income_long %>%
#  mutate(year = as.character(year))


# Join to get income thresholds for each year
income_long <- income_long %>%
  left_join(quintiles, by = "year")

income_long <- income_long %>%
  mutate(
    quintile = case_when(
      head_labor_income <= Lowest ~ 1, # Bottom 20th lowest
      head_labor_income <= Second ~ 2, 
      head_labor_income <= Third ~ 3, 
      head_labor_income <= Fourth ~ 4, # Top 20th highest 80th and above
      head_labor_income > Fourth ~ 5,
      TRUE ~ NA_real_
    ),
    quintile_label = case_when(
      head_labor_income <= Lowest ~ "lowest",
      head_labor_income <= Second ~ "second",
      head_labor_income <= Third ~ "third",
      head_labor_income <= Fourth ~ "fourth",
      head_labor_income > Fourth ~ "top",
      TRUE ~ NA_character_
    )
  )
summary(income_long)

# I joined too many times and added extra columns. The following code deletes excess columns
# Remove all duplicate columns with .y suffix
#income_long <- income_long %>%
#  select(-contains(".y"))

# Remove .x from the column names to simplify
#colnames(income_long) <- gsub("\\.x$", "", colnames(income_long))
colnames(income_long)
view(income_long)

# I duplicated the quintiles because I joined too many times. This removes it:
#income_long <- income_long[, !duplicated(colnames(income_long))]

summary(income_long)
plot(head_labor_income ~ year, data= income_long)
dim(income_long)

write_csv(income_long, "C:/Users/markc/Downloads/dream")
# ------------------------------------------------------------

# Load necessary libraries
library(foreign)
library(dplyr)
library(readr)
library(tidyr)
library(readxl)

# Load existing CSV in long format
dream <- read.csv("C:/Users/Mark Crisci/Downloads/dream.csv")
success <- read.csv("C:/Users/Mark Crisci/Downloads/DreamSuccess.csv")


# Load and convert .dbf file
j602 <- read.dbf("C:/Users/Mark Crisci/Downloads/J348602.dbf")

# Select required variables from J602.dbf (excluding ages.dbf)
j602 <- j602 %>%
  select(ER30001, ER30002, ER32000,
         V5, V449, V1122, V1823, V2423, V3021, V3417, V3817, V4318, V5217, V5717,
         V6319, V6917, V7517, V8217, V8817, V10018, V11125, V12524, V13724, V14824,
         V16324, V17724, V19024, V20324, V21610, ER2033, ER5032, ER7032, ER10036,
         ER13041, ER17044, ER21043, ER25029, ER36029, ER42030, ER47330, ER53030,
         ER60031, ER66031, ER72031, ER78032, ER82033,
         V3939, V4450, V5364, V5864, V6479, V7084, V7675, V8364, V8974, V10437,
         V11618, V13023, V14126, V15140, V16641, V18072, V19372, V20672, V22427,
         ER2032, ER5031, ER7031, ER10035, ER13040, ER17043, ER21042, ER25028,
         ER36028, ER42029, ER47329, ER53029, ER60030, ER66030, ER72030, ER78031,
         ER82032,
         TA050609, TA070584, TA090637, TA110725, TA130745, TA150758, TA170805,
         TA190954, TA210992, TA050884, TA070865, TA090925, TA111057, TA131092,
         TA151132, TA171955, TA192131, TA212252, TA050947, TA090992, TA111134,
         TA131226, TA151286, TA171981, TA192192, TA212387, TA050949, TA090994,
         TA111136, TA131228, TA151288, TA171983, TA192194, TA212389, TA192191,
         TA212386)



# Own rent or neither, data from 1975-2023 
own_rent <- c(
  "V3939", "V4450", V5364 V5864 V6479 V7084 V7675 V8364 V8974 V10437 V11618 V13023 V14126 V15140 V16641 V18072 V19372 V20672 V22427 ER2032 ER5031 ER7031 ER10035
  ER13040 ER17043 ER21042 ER25028 ER36028 ER42029 ER47329 ER53029 ER60030 ER66030
  ER72030 ER78031 ER82032
  
)


# Reshape j602_selected into long format
j602 <- j602 %>%
  pivot_longer(cols = -c(ER30001, ER30002),
               names_to = "variable",
               values_to = "value")
# Merge with the dream dataset
dream <- dream %>%
  left_join(j602, by = c("ER30001", "ER30002"))
head(dream)
# Save the complete dataset as a new CSV
write_csv(final_df, "C:/Users/Mark Crisci/Downloads/dreamOR.csv")





# Remove 1992 from the dataset
dream <- dream %>%
  filter(year != 1992)
  #select(head_labor_income)

write.csv(dream, "C:/Users/Mark Crisci/Downloads/dream_92.csv", row.names = FALSE)

dream_92 <- read.csv("C:/Users/Mark Crisci/Downloads/dream_92.csv")
summary(dream_92$head_labor_income)
head(dream_92)
summary(dream_92)

sum(dream_92$head_labor_income, na.rm = TRUE)


install.packages("rlang")
library(rlang)
# --- Load Required Libraries ---
library(readxl)
library(ggplot2)
library(scales)
library(readr)
library(mosaic)

# --- Load Data from Excel Files ---
df1 <- read_excel("C:/Users/Mark Crisci/Documents/lowestAtleast_fourth68_22.xlsx")
df2 <- read_excel("C:/Users/Mark Crisci/Documents/lowestTop68_22.xlsx")
df3 <- read_excel("C:/Users/Mark Crisci/Documents/downwardToptoLow68_22.xlsx")


# --- Clean Data: Remove Rows with NA Values ---
df1_clean <- na.omit(df1)
df2_clean <- na.omit(df2)
df3_clean <- na.omit(df3)

# probability column as numeric
df1_clean$probability <- as.numeric(df1_clean$probability)
df2_clean$probability <- as.numeric(df2_clean$probability)
df3_clean$probability <- as.numeric(df3_clean$probability)

plot(probability~year, data = df1)

lm.obj <- lm(probability ~ year, data = df1_clean)
summary(lm.obj)
confint(lm.obj, level = 0.95)


lm.obj.2 <- lm(probability ~ year, data = df2_clean)
summary(lm.obj.2)

lm.obj.down <- lm(probability ~ year, data = df3_clean)
summary(lm.obj.down)

# # log transform probability----does not improve.
# 
# log.obj <- lm(log(probability) ~ year, data = df1_clean)
# summary(log.obj)
# 
# log.obj.2 <- lm(log(probability) ~ year, data = df2_clean)
# summary(log.obj.2)
# 
# 
# log.obj.down <- lm(log(probability) ~ year, data = df3_clean)
# summary(log.obj.down)


plot(log.obj)

plot(lm.obj)


# Trend line plots

ggplot(df1_clean, aes(x = year, y = probability))+
  geom_point(color = "black")+
  geom_smooth(method = "lm", se = FALSE, color = "red")+
  labs(title = "Linear Regression of Probability Trend Over Time", x ="year",
       y="probability")+
    
  theme_minimal()
  
ggplot(df2_clean, aes(x = year, y = probability)) +
  geom_point(color = "green") +
  geom_smooth(method = "lm", se = FALSE, color = "darkgreen") +
  labs(title = "DF2: Probability Trend", x = "Year", y = "Probability") +
  theme_light()

ggplot(df3_clean, aes(x = year, y = probability)) +
  geom_point(color = "purple") +
  geom_smooth(method = "lm", se = FALSE, color = "black") +
  labs(title = "DF3: Downward Probability Trend", x = "Year", y = "Probability") +
  theme_classic()

# -------- The only significant model
  
# --- Plot 1: Probability Trajectory (Lowest to At Least Fourth Quintile) ---
p1 <- ggplot(df1_clean, aes(x = year, y = probability)) +
  geom_line(color = "#1f77b4", size = 1.3) +
  geom_point(color = "#1f77b4", size = 2.5) +
  theme_minimal(base_size = 15) +
  labs(
    title = "Trajectory: Probability (Lowest to At Least Fourth Quintile)",
    x = "Year",
    y = "Probability"
  ) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1)) +
  theme(
    plot.title = element_text(face = "bold", size = 17),
    axis.title = element_text(face = "bold"),
    axis.text = element_text(size = 13)
  )

# --- Plot 2: Probability Trajectory (Lowest to Top Quintile) ---
p2 <- ggplot(df2_clean, aes(x = year, y = probability)) +
  geom_line(color = "#d62728", size = 1.3) +
  geom_point(color = "#d62728", size = 2.5) +
  theme_minimal(base_size = 15) +
  labs(
    title = "Trajectory: Probability (Lowest to Top Quintile)",
    x = "Year",
    y = "Probability"
  ) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1)) +
  theme(
    plot.title = element_text(face = "bold", size = 17),
    axis.title = element_text(face = "bold"),
    axis.text = element_text(size = 13)
  )

# --- Print Plots ---
print(p1)
print(p2)


head(df1)

# ------------ ANALYSIS of Dream.csv ------------------

library(mosaic)
library(magrittr) 
library(dplyr)

head(dream)
summary(dream)




# Ensure quintile_label is a character (just in case)
dream$quintile_label <- as.character(dream$quintile_label)

# Function to flag ascension from "lowest"
get_ascend_from_lowest <- function(df) {
  # Get first quintile_label per person
  df_first <- df %>%
    group_by(family_person) %>%
    arrange(year) %>%
    slice(1) %>%
    ungroup() %>%
    select(family_person, first_quintile = quintile_label)
  
  # Join first_quintile to main dataframe
  df <- df %>% left_join(df_first, by = "family_person")
  
  # Check who ever started in "lowest"
  started_lowest <- unique(df$family_person[df$first_quintile == "lowest"])
  
  # For each person, flag if at any point they reached "fourth" or "top" after being "lowest"
  ascended <- df %>%
    filter(family_person %in% started_lowest) %>%
    group_by(family_person) %>%
    summarize(ascend = as.integer(any(quintile_label %in% c("fourth", "top")))) %>%
    ungroup()
  
  # Set column: 1 if ascended, 0 if not, NA if not in started_lowest
  df <- df %>%
    left_join(ascended, by = "family_person") %>%
    mutate(ascend_from_lowest = case_when(
      first_quintile == "lowest" ~ ascend,
      TRUE ~ NA_integer_
    )) %>%
    select(-first_quintile, -ascend)
  
  return(df)
}
# Run functions to add column
dream <- get_ascend_from_lowest(dream)


# Function to flag ascension from "lowest" or "second"
get_ascend_from_second_or_lowest <- function(df) {
  # Get first quintile_label per person
  df_first <- df %>%
    group_by(family_person) %>%
    arrange(year) %>%
    slice(1) %>%
    ungroup() %>%
    select(family_person, first_quintile = quintile_label)
  
  # Join first_quintile to main dataframe
  df <- df %>% left_join(df_first, by = "family_person")
  
  # Check who ever started in "lowest" or "second"
  started_second_or_lowest <- unique(df$family_person[df$first_quintile %in% c("lowest", "second")])
  
  # For each person, flag if at any point they reached "fourth" or "top" after being "lowest" or "second"
  ascended <- df %>%
    filter(family_person %in% started_second_or_lowest) %>%
    group_by(family_person) %>%
    summarize(ascend = as.integer(any(quintile_label %in% c("fourth", "top")))) %>%
    ungroup()
  
  # Set column: 1 if ascended, 0 if not, NA if not in started_second_or_lowest
  df <- df %>%
    left_join(ascended, by = "family_person") %>%
    mutate(ascend_from_second_or_lowest = case_when(
      first_quintile %in% c("lowest", "second") ~ ascend,
      TRUE ~ NA_integer_
    )) %>%
    select(-first_quintile, -ascend)
  
  return(df)
}

# Run both functions to add columns
dream <- get_ascend_from_lowest(dream)
dream <- get_ascend_from_second_or_lowest(dream)

# Optional: Check result
table(dream$ascend_from_lowest, useNA = "always")
table(dream$ascend_from_second_or_lowest, useNA = "always")

# Save the new dataset if needed
write.csv(dream, "C:/Users/Mark Crisci/Downloads/DreamSuccess.csv", row.names = FALSE)




#----GLM MODELING-----


dream <- read.csv("C:/Users/Mark Crisci/Downloads/dream_92.csv")
success <- read.csv("C:/Users/Mark Crisci/Downloads/DreamSuccess.csv")
head(success)
summary(dream)

# Assuming your dataframe is called dream and quintile_label is your quintile column
table(success$quintile_label)


# Simple totals table of mobility from lowest or second quintiles
table(success$ascend_from_second_or_lowest, useNA = "ifany")
# allow user to pick if this its going to be exactly this q

library(carData)

summary(lm.obj)
glm.obj <- glm(`ascend_from_lowest` ~ `head_labor_income` + year, data = success, family = "binomial")

summary(glm.obj)


vif(glm.obj)
confint(glm.obj)


model_predict <- predict(glm.obj, newdata = data.frame(`head_labor_income`= 50000, year = 1990), type='response')

confusionMatrix(model_predict)
library(ggplot2)
# Make a new data frame with year across the observed range, holding income at its median
newdat <- data.frame(
  year = seq(min(success$year, na.rm=TRUE), max(success$year, na.rm=TRUE), by=1),
  head_labor_income = median(success$head_labor_income, na.rm=TRUE)
)
# Predict probability (on response scale)
newdat$pred_prob <- predict(glm.obj, newdata = newdat, type = "response")

ggplot(newdat, aes(x = year, y = pred_prob)) +
  geom_line(size = 1.2, color = "#2ca02c") +
  labs(
    x = "Year",
    y = "Predicted Probability of Upward Mobility",
    title = "Predicted Probability of Upward Mobility Over Time (Median Income)"
  ) +
  theme_minimal(base_size = 16)

# Vary income instead, hold year at its median
newdat2 <- data.frame(
  year = median(success$year, na.rm=TRUE),
  head_labor_income = seq(min(success$head_labor_income, na.rm=TRUE),
                          max(success$head_labor_income, na.rm=TRUE), length.out=100)
)
newdat2$pred_prob <- predict(glm.obj, newdata = newdat2, type = "response")

ggplot(newdat2, aes(x = head_labor_income, y = pred_prob)) +
  geom_line(size = 1.2, color = "#1f77b4") +
  labs(
    x = "Head Labor Income",
    y = "Predicted Probability of Upward Mobility",
    title = "Predicted Probability by Income (Median Year)"
  ) +
  theme_minimal(base_size = 16)



success$pred_prob <- predict(glm.obj, type = "response")

ggplot(success, aes(x = pred_prob, fill = factor(ascend_from_lowest))) +
  geom_histogram(position = "identity", alpha = 0.6, bins = 30) +
  labs(
    x = "Predicted Probability",
    fill = "Actual Upward Mobility",
    title = "Distribution of Predicted Probabilities by Actual Outcome"
  ) +
  theme_minimal(base_size = 16)

glm.obj.2 <- glm(`ascend_from_lowest` ~ `head_labor_income` + year + (head_labor_income:year), data = success, family = binomial)
summary(glm.obj.2)
vif(glm.obj.2)



# Load libraries
library(caret)
library(ggplot2)
library(dplyr)

# Assume your data is named 'success' with variables:
# ascend_from_lowest (0/1), head_labor_income, year

# Split data (80% train, 20% test)
set.seed(123)
success <- success %>%
  filter(!is.na(ascend_from_lowest),
         !is.na(head_labor_income),
         !is.na(year)) # add other predictors if necessary


train_idx <- createDataPartition(success$`ascend_from_lowest`, p = 0.8, list = FALSE)
train <- success[train_idx, ]
test <- success[-train_idx, ]

# Fit logistic regression model
glm.obj <- glm(ascend_from_lowest ~ head_labor_income + year, data = train, family = binomial)

# Predict probabilities on test set
test$pred_prob <- predict(glm.obj, newdata = test, type = "response")

# Optional: classify as 0/1 using a cutoff (e.g., 0.5)
test$pred_class <- ifelse(test$pred_prob > 0.5, 1, 0)

# ROC/AUC (optional, to evaluate model)
library(pROC)
roc_obj <- roc(test$ascend_from_lowest, test$pred_prob)
auc(roc_obj) # Print AUC value

# Visualization: Plot predicted probabilities by actual outcome
ggplot(test, aes(x = pred_prob, fill = as.factor(ascend_from_lowest))) +
  geom_histogram(position = "identity", alpha = 0.5, bins = 30) +
  labs(x = "Predicted Probability of Upward Mobility",
       fill = "Actual Upward Mobility (0=No, 1=Yes)",
       title = "Distribution of Predicted Probabilities") +
  theme_minimal()


# Alternatively, plot effect of income and year:
library(effects)
plot(allEffects(glm.obj), main="Effect of Head Labor Income and Year on Upward Mobility")

# For a nice trendline: plot predicted probability vs. year for a fixed income
newdata <- data.frame(
  head_labor_income = median(train$head_labor_income, na.rm = TRUE),
  year = seq(min(train$year, na.rm=TRUE), max(train$year, na.rm=TRUE))
)
newdata$pred_prob <- predict(glm.obj, newdata = newdata, type = "response")

ggplot(newdata, aes(x = year, y = pred_prob)) +
  geom_line(size = 1.2, color = "#0072B2") +
  labs(y = "Predicted Probability (Median Income)",
       x = "Year",
       title = "Predicted Upward Mobility Probability by Year (Median Income)") +
  theme_minimal()



# Split dataset into two time periods
dream68_95<- success %>% filter(year >= 1968 & year <= 1995)
dream96_22 <- success %>% filter(year >= 1996 & year <= 2022)
summary(dream68_95)
summary(dream96_22)
nrow(dream68_95)
nrow(dream96_22)

summary(dream68_95$head_labor_income)
summary(dream96_22$head_labor_income)


#Differnce of means t-test
t.test(head_labor_income ~ year >= 1996, data = success)

# Between two subsets periods
t.test(dream68_95$head_labor_income, dream96_22$head_labor_income)


glm.obj.68.95 <- glm(ascend_from_lowest ~ head_labor_income, data = dream68_95, family = binomial)
summary(glm.obj.68.95)

glm.obj.96.22 <- glm(ascend_from_lowest ~ head_labor_income, data = dream96_22, family = binomial)
summary(glm.obj.96.22)
ggplot(data = dream68_95, aes(x = head_labor_income, y = ascend_from_lowest)+
         geom_histogram())


# Create data frame of income values
income.vals <- seq(0, 100000, by = 1000)

# Predict probabilities
prob.68.95 <- predict(glm.obj.68.95, newdata = data.frame(head_labor_income = income.vals), type = "response")
prob.96.22 <- predict(glm.obj.96.22, newdata = data.frame(head_labor_income = income.vals), type = "response")


# Combine into df and plot
df_plot <- data.frame(
  head_labor_income = income.vals,
  prob.68.95 = prob.68.95,
  prob.96.22 = prob.96.22
)

ggplot(df_plot, aes(x = head_labor_income)) +
  geom_line(aes(y = prob.68.95, color = "1968–1995")) +
  geom_line(aes(y = prob.96.22, color = "1996–2022")) +
  labs(y = "Probability of Upward Mobility", x = "Labor Income", color = "Time Period") +
  theme_minimal()





# Split for testing data and train data
library(dplyr)
set.seed(123)

# Remove NA's
test.68.95 <- dream68_95 %>%
  filter(!is.na(ascend_from_lowest), !is.na(head_labor_income))


# Create index
train.index <- sample(1:nrow(test.68.95), 0.8 * nrow(test.68.95))

# Split data
train.data.68.95 <-test.68.95[train.index,]
final.test.68.95 <- test.68.95[-train.index,] 


glm.train.68.95 <- glm(ascend_from_lowest ~head_labor_income, data = train.data.68.95, family = binomial)
summary(glm.obj.68.95)

test.probs <- predict(glm.train.68.95, newdata = final.test.68.95,type = "response")
summary(test.probs)

test.class <- ifelse(test.probs > 0.5, 1, 0)
summary(test.class)

# Confusion matrix
table(Predicted = test.class, Actual = final.test.68.95$ascend_from_lowest)

# ACcuracy
mean(test.class == final.test.68.95$ascend_from_lowest)

#Library
library(pROC)
roc.obj <- roc(test_data$ascend_from_lowest, test.probs


# Create a data frame of example incomes (across a realistic range)
income.range <- data.frame(head_labor_income = seq(0, 200000, by = 1000))

# Predict probability of upward mobility for each example income
income.range$test.probs <- predict(glm.train.68.95, newdata = income.range, type = "response")

# Plot
ggplot(income.range, aes(x = head_labor_income, y = test.probs)) +
  geom_line(color = "steelblue", size = 1.2) +
  labs(
    title = "Predicted Probability of Escaping Bottom Quintile (1996–2022)",
    x = "Head Labor Income ($)",
    y = "Predicted Probability of Upward Mobility"
  ) +
  theme_minimal() +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
  geom_hline(yintercept = 0.5, linetype = "dashed", color = "gray") +
  annotate("text", x = 100000, y = 0.52, label = "50% Threshold", color = "gray")





# Required libraries
library(dplyr)
library(pROC)
library(ggplot2)

set.seed(123)  # for reproducibility

# STEP 1: Filter and clean the dataset
clean_96_22 <- dream96_22 %>%
  filter(!is.na(ascend_from_lowest), !is.na(head_labor_income))

# STEP 2: Train/test split (80/20)
train_index_96 <- sample(1:nrow(clean_96_22), 0.8 * nrow(clean_96_22))
train_96 <- clean_96_22[train_index_96, ]
test_96 <- clean_96_22[-train_index_96, ]

# STEP 3: Fit logistic model
glm_96 <- glm(ascend_from_lowest ~ head_labor_income, 
              data = train_96, 
              family = binomial)

# STEP 4: Predict probabilities on test set
test_probs_96 <- predict(glm_96, newdata = test_96, type = "response")
test_pred_class_96 <- ifelse(test_probs_96 >= 0.5, 1, 0)

# STEP 5: Confusion matrix
conf_matrix <- table(Predicted = test_pred_class_96, Actual = test_96$ascend_from_lowest)
print(conf_matrix)

# STEP 6: Accuracy
accuracy <- mean(test_pred_class_96 == test_96$ascend_from_lowest)
print(paste("Accuracy:", round(accuracy, 4)))

# STEP 7: ROC AUC
roc_96 <- roc(test_96$ascend_from_lowest, test_probs_96)
auc_96 <- auc(roc_96)
print(paste("AUC:", round(auc_96, 4)))


# Create a data frame of example incomes (across a realistic range)
income_range <- data.frame(head_labor_income = seq(0, 200000, by = 1000))

# Predict probability of upward mobility for each example income
income_range$predicted_prob <- predict(glm_96, newdata = income_range, type = "response")

# Plot
ggplot(income_range, aes(x = head_labor_income, y = predicted_prob)) +
  geom_line(color = "steelblue", size = 1.2) +
  labs(
    title = "Predicted Probability of Escaping Bottom Quintile (1996–2022)",
    x = "Head Labor Income ($)",
    y = "Predicted Probability of Upward Mobility"
  ) +
  theme_minimal() +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
  geom_hline(yintercept = 0.5, linetype = "dashed", color = "gray") +
  annotate("text", x = 100000, y = 0.52, label = "50% Threshold", color = "gray")









# 1. Install and load necessary packages
# If you don't have them installed, uncomment and run these lines:
install.packages("tidyverse")
# install.packages("reshape2") # For older R versions, or if you prefer melt()

library(tidyverse) # Includes dplyr, ggplot2, and tidyr

# 2. Load the data
# Make sure your CSV file is in your RStudio working directory,
# or provide the full path to the file.

# --- IMPORTANT CHANGE HERE ---
# Use the full, correct filename and tell R to treat empty strings as NA from the start
df <- read.csv(
  "C:/Users/Mark Crisci/Documents/Upward Mobility Matrix_exact.xlsx - Sheet1.csv",
  header = FALSE,
  skip = 3,
  stringsAsFactors = FALSE, # Prevents strings from being converted to factors automatically
  na.strings = c("", " ")   # Tells R to interpret empty strings or spaces as NA
)

# 3. Clean and reshape the data

# Identify the goal quintile names from the loaded data (row 1, columns 4-8 of the *read* df)
goal_quintiles <- as.character(df[1, 4:8])

# Identify the start quintile names from the loaded data (column 3, rows 2-6 of the *read* df)
start_quintile_names <- as.character(df[2:6, 3])

# Extract the mobility matrix part (the probabilities)
mobility_matrix <- df[2:6, 4:8]

# --- IMPORTANT CHANGE HERE ---
# Convert all columns in the mobility_matrix to numeric.
# We first convert to character to handle any potential factor issues, then to numeric.
mobility_matrix[] <- lapply(mobility_matrix, function(x) as.numeric(as.character(x)))

# Assign proper column names to the matrix
names(mobility_matrix) <- goal_quintiles

# Add the 'Start Quintile' as a column for pivoting
mobility_matrix$StartQuintile <- start_quintile_names

# Reshape data to a long format for ggplot2
df_long <- mobility_matrix %>%
  pivot_longer(
    cols = -StartQuintile, # Exclude StartQuintile from pivoting
    names_to = "GoalQuintile",
    values_to = "Probability"
  )

# --- IMPORTANT CHANGE HERE ---
# Filter out rows where Probability is NA.
# These NAs correspond to the empty cells in your original matrix
# where no transition probability is defined for upward mobility.
df_long <- df_long %>%
  filter(!is.na(Probability))

# Convert quintile columns to factors with specific order for plotting
# Ensure levels match the actual names extracted
df_long$StartQuintile <- factor(df_long$StartQuintile, levels = rev(start_quintile_names)) # Reverse for y-axis
df_long$GoalQuintile <- factor(df_long$GoalQuintile, levels = goal_quintiles)

# 4. Generate the heatmap
ggplot(df_long, aes(x = GoalQuintile, y = StartQuintile, fill = Probability)) +
  geom_tile(color = "white", linewidth = 0.5) + # Add white borders to tiles
  geom_text(aes(label = sprintf("%.2f", Probability)), color = "black", size = 3) + # Add text labels
  scale_fill_gradient(low = "lightblue", high = "darkblue", name = "Probability") + # Color gradient
  labs(
    title = "Upward Mobility Matrix (Exact Start, Exact Goal)",
    subtitle = "Time Horizon: 10 Years, Consecutive Stay: 3 Years",
    x = "Goal Quintile",
    y = "Start Quintile"
  ) +
  theme_minimal() + # Minimal theme for cleaner look
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1), # Rotate x-axis labels
    panel.grid.major = element_blank(), # Remove major grid lines
    panel.grid.minor = element_blank(), # Remove minor grid lines
    plot.title = element_text(hjust = 0.5), # Center title
    plot.subtitle = element_text(hjust = 0.5) # Center subtitle
  )









#------These plots below were used prior to moneyincome removal and are no longer used in analysis/cleaning/wrangling----

# PLOT for HEAD/labor income
ggplot() +
  geom_line(
    data = filter(income_long, show_sample),
    aes(x = year, y = head_labor_income, group = ER30002),
    color = "gray70", alpha = 0.7
  ) +
  stat_summary(
    data = income_long, aes(x = year, y = head_labor_income),
    fun = mean, geom = "line", color = "blue", size = 1.3
  ) +
  stat_summary(
    data = income_long, aes(x = year, y = head_labor_income),
    fun = median, geom = "line", color = "red", linetype = "dashed", size = 1
  ) +
  labs(
    title = "Head Labor Income Over Time: Sample Individuals, Mean (blue), Median (red dashed)",
    x = "Year", y = "Head Labor Income"
  ) +
  theme_minimal()


# PLOT money/ taxable income
#ggplot() +
#   data = filter(income_long, show_sample),
 #   aes(x = year, y = money_income, group = ER30002),
  #  color = "gray70", alpha = 0.7
#  ) +
 # stat_summary(
#    data = income_long, aes(x = year, y = money_income),
 #   fun = mean, geom = "line", color = "blue", size = 1.3
  #) +
  #stat_summary(
  #  data = income_long, aes(x = year, y = money_income),
   # fun = median, geom = "line", color = "red", linetype = "dashed", size = 1
  #) +
  #labs(
  #  title = "Money/Taxable Income Over Time: Sample Individuals, Mean (blue), Median (red dashed)",
  #  x = "Year", y = "Money/Taxable Income"
#  ) +
 # theme_minimal()


# BOTH ON THE SAME PLOT
#income_long2 <- income_long %>%
#  pivot_longer(
#    cols = c(head_labor_income, money_income),
#    names_to = "income_type",
#    values_to = "income"
#  )

#ggplot() +
 # geom_line(
  #  data = filter(income_long2, show_sample),
   # aes(x = year, y = income, group = interaction(ER30002, income_type), color = income_type),
  #alpha = 0.5
  #) +
#  stat_summary(
#   data = filter(income_long2, income_type == "head_labor_income"),
 #   aes(x = year, y = income),
#    fun = mean, geom = "line", color = "blue", size = 1.3
 # ) +
#  stat_summary(
 #   data = filter(income_long2, income_type == "money_income"),
  #  aes(x = year, y = income),
  #  fun = mean, geom = "line", color = "red", size = 1.3
#  ) +
 # labs(
#    title = "Income Over Time: Labor (blue), Money/Taxable (red)",
 #   x = "Year", y = "Income"
#  ) +
 # scale_color_manual(values = c("head_labor_income" = "blue", "money_income" = "red"),
#                     labels = c("Labor Income", "Money/Taxable Income")) +
 # theme_minimal()



#Transform the y-axis (log scale). This will make the distribution less “squished,”
# and differences among regular incomes more visible.
ggplot(income_long, aes(x = year, y = head_labor_income, group = ER30002)) +
  geom_line(alpha = 0.1, color = "steelblue") +
  scale_y_log10(labels = scales::dollar_format()) +
  stat_summary(aes(group = 1), fun = mean, geom = "line", color = "blue", size = 1.2) +
  stat_summary(aes(group = 1), fun = median, geom = "line", color = "red", linetype = "dashed", size = 1) +
  labs(
    title = "Head Labor Income Over Time (log scale)",
    y = "Labor Income (log scale)",
    x = "Year"
  ) +
  theme_minimal()
view(psid)

ggplot(income_long, aes(x = year, y = , group = ER30002)) +
  geom_line(alpha = 0.1, color = "steelblue") +
  scale_y_log10(labels = scales::dollar_format()) +
  stat_summary(aes(group = 1), fun = mean, geom = "line", color = "blue", size = 1.2) +
  stat_summary(aes(group = 1), fun = median, geom = "line", color = "red", linetype = "dashed", size = 1) +
  labs(
    title = "Head Labor Income Over Time (log scale)",
    y = "Labor Income (log scale)",
    x = "Year"
  ) +
  theme_minimal()


#Plot just the median and mean over time
income_summary <- income_long %>%
  group_by(year) %>%
  summarize(
    mean_income = mean(head_labor_income, na.rm = TRUE),
    median_income = median(head_labor_income, na.rm = TRUE),
    p25 = quantile(head_labor_income, 0.25, na.rm = TRUE),
    p75 = quantile(head_labor_income, 0.75, na.rm = TRUE)
  )

plot(income_long)
plot(income_summary)

# Plot income summary by year (over times) with lower and upper percentiles
ggplot(income_summary, aes(x = year)) +
  geom_ribbon(aes(ymin = p25, ymax = p75), fill = "gray80", alpha = 0.4) +
  geom_line(aes(y = mean_income), color = "blue", size = 1.2) +
  geom_line(aes(y = median_income), color = "red", linetype = "dashed", size = 1) +
  labs(
    title = "Summary of Head Labor Income Over Time",
    y = "Labor Income",
    x = "Year"
  ) +
  theme_minimal()


# Boxplots or violin plots by year. 
ggplot(income_long, aes(x = factor(year), y = head_labor_income)) +
  geom_boxplot(outlier.shape = NA, fill = "lightblue", alpha = 0.6) +
  scale_y_log10(labels = scales::dollar_format()) +
  labs(
    title = "Distribution of Head Labor Income by Year",
    x = "Year",
    y = "Labor Income (log scale)"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))







# CHECK IF MONEY INCOME tracks something different by checking correlation
# Calculate correlation per person (across all available years)
cor_results <- income_long %>%
  group_by(ER30001, ER30002) %>%
  summarize(
    cor = cor(head_labor_income, money_income, use = "complete.obs")
  ) %>%
  ungroup()

summary(cor_results$cor)
hist(cor_results$cor, breaks = 20, main = "Distribution of Correlation between Labor and Money Income", xlab = "Correlation")



# These plots were added on 6/20
# I made these after adding the "relation/ship to head/ref person variables to dataframe
ggplot(income_long)


# Plots
ggplot(income_long, aes(x = year, group = ER30002)) +
  # Head Labor Income: All traces
  geom_line(aes(y = head_labor_income), alpha = 0.1, color = "blue") +
  # Money/Taxable Income: All traces
  geom_line(aes(y = money_income), alpha = 0.1, color = "red") +
  
  # Head Labor Income: Mean trend
  stat_summary(aes(y = head_labor_income), fun = mean, geom = "line",
               color = "blue", size = 1.5, linetype = "solid") +
  # Money/Taxable Income: Mean trend
  stat_summary(aes(y = money_income), fun = mean, geom = "line",
               color = "red", size = 1.5, linetype = "dashed") +
  
  # Head Labor Income: Median trend
  stat_summary(aes(y = head_labor_income), fun = median, geom = "line",
               color = "blue", size = 1, linetype = "dotdash") +
  # Money/Taxable Income: Median trend
  stat_summary(aes(y = money_income), fun = median, geom = "line",
               color = "red", size = 1, linetype = "dotdash") +
  
  labs(title = "Head Labor Income vs. Money/Taxable Income: 1968–1993",
       subtitle = "Solid=Mean, Dotdash=Median, Blue=Labor, Red=Money/Taxable",
       x = "Year", y = "Income (Nominal $)",
       caption = "Each line = one individual") +
  theme_minimal()



