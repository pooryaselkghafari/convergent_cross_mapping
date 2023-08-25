# convergent_cross_mapping
This code is a simple tool to download a set of datasets from Google Trends (based on the user's input) over a time period and detect their interaction with a target time series dataset using convergent cross-mapping

Store the keywords you want to download their frequency from Google Trends in a csv file.
Store the time series data set (for example sales of a product) in another csv file.

N_round sets the number of layers the code will work. In step one  the code will explore Google Trends, download the keywords, check whether the keywords have a significant relationship with your target data, and in the next steps  digs deeper and downloads the related keywords from Google Trend, download their frequency and checks for significant interactions with your target dataset. The results are stored in separate folders.

# Example

```
first_test =  keyword_mind_map(path_kw= "path to your keywords",path_target="path to the target time series",
                               date_start='2004-01-01',date_end="2019-11-29",region="US",causal_threshold=1,sales_start_date = "2007-05")  

map_2_layer = keyword_map(n_round = 3)
```
