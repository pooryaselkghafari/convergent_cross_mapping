import pandas as pd
import math
import matplotlib.pyplot as plt
from causal_ccm.causal_ccm import ccm
import numpy as np
from sklearn.preprocessing import StandardScaler
import statistics
import time
import pandas as pd
import os
import natsort
import shutil
from selenium import webdriver
from pathlib import Path


class keyword_mind_map():

    def __init__(self, path_kw,path_target,date_start,date_end,region = "all",simplicity_factor=0.9,causal_sensitivity = 0.1 ,causal_threshold = 0.1, link ="https://trends.google.com/trends/explore?date=", sales_start_date = "2004-01"):

        self.path_kw = path_kw
        self.path_target = path_target #the economic outcome
        self.date_start = date_start
        self.date_end = date_end
        self.region = region
        self.simplicity_factor = simplicity_factor
        self.causal_sensitivity = causal_sensitivity
        self.causal_threshold = causal_threshold
        self.link = link
        self.sales_start_date = sales_start_date


    def causalaty_check (self,keywords_interest):
        data = keywords_interest #read the initial set of keywords
        target_data = data.columns[0]
        Y = pd.to_numeric(data[target_data]) #create dependent variables matrix
        Y = Y.diff() #take first diff
        Y = Y.fillna(0) #fill nans with zeros
        causal_threshold = self.causal_threshold #the level of convergence
        keyword_list = pd.DataFrame()
        keyword_pass = 0
        for keyword in range(len(data.columns)):
            keyword_name = data.columns[keyword]
            if keyword_name == target_data:
                continue
            X = pd.to_numeric(data[keyword_name])
            X = X.diff()
            X = X.fillna(0)
            E , tau = self.best_E_tau(Y,X)
            L = len(X)
            causality         = ccm(X,Y,tau,E,L).causality()
            causality_reverse = ccm(Y,X,tau,E,L).causality()
            if keyword_name != target_data:
                
                if causality[1] < 0.05 :
                    keyword_list.loc[keyword_pass,"query"] = keyword_name
                    keyword_list.loc[keyword_pass,"direct effect"] = causality[0]
                    
                if causality_reverse[1] < 0.05 :
                    keyword_list.loc[keyword_pass,"query"] = keyword_name
                    keyword_list.loc[keyword_pass,"reverse effect"] = causality_reverse[0]
 
                keyword_pass += 1
                print('done')
        return keyword_list
    
    
    def best_E_tau (self,target,compare):#which keyword to compare to get best tau and L
        #simplicity factor is to avoid choosing very large E and tau for very few increases in prediction skills
        #read the initial set of keywords
        target = pd.to_numeric(target)
        compare = pd.to_numeric(compare)
        print(target)
        print(compare)
        L = len(target.index)
        Max_E = int(L/18)
        E_range = np.arange(3,Max_E,1)
        tau_range = np.arange(1,10,1)
        predict_skill_max = 0
        E_max = 3
        tau_max = 1
        for tau in tau_range:
            for E in E_range:
                ccm_model = ccm(compare,target,tau,E,L)
                predict_skill_temp = ccm_model.causality()[0]
                if predict_skill_temp *self.simplicity_factor > predict_skill_max:
                    E_max = E
                    tau_max = tau
                    predict_skill_max = predict_skill_temp
        return (E_max,tau_max)
    
    
    def interest_over_time (self,keyword,target_data):
        # Create the webdriver object. Here the 
        # chromedriver is present in the driver 
        # folder of the root directory.
        kw_list = keyword
        dir_path = os.path.dirname(os.path.realpath(__file__)) #get the current directory
        os.chdir(dir_path)
        download_directory = dir_path + "/all_keywords"
        Path(download_directory).mkdir(parents=True, exist_ok=True)
        os.chdir(download_directory)
        link = self.link + self.date_start +"%20"+self.date_end +"&geo=" + self.region + "&q="
        kw_list = list(kw_list.iloc[:,0])
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : download_directory} #change download directory
        chromeOptions.add_experimental_option("prefs",prefs)
        
        for kw in range(len(kw_list)):
            keyword = kw_list[kw]
            keyword = keyword.replace(" ","%20")
            driver = webdriver.Chrome(r"./driver/chromedriver",options=chromeOptions)
            link_temp = link + keyword
            driver.get(link_temp)
            time.sleep(3)
            driver.refresh() #refresh the page to avoid error 429
            # Maximize the window and let code stall 
            # for 10s to properly maximise the window.
            time.sleep(2)
            driver.maximize_window()
            # Obtain download button by class name and click.
            button = driver.find_element("class name", "widget-actions-item")
            button.click()
            time.sleep(3)
            driver.close()
        keywords_interest = pd.DataFrame()
        
        for file in natsort.natsorted(os.listdir()):
          if (file!= ".DS_Store"):
            file_path = f"{download_directory}/{file}"
            keyword = pd.read_csv(file_path) 
            keyword_columns = keyword.loc['Month','Category: All categories']
            keyword_columns = keyword_columns.replace(': (United States)',"")
            keyword = keyword.rename(columns={'Category: All categories': keyword_columns})
            keyword = keyword.drop('Month')
            keywords_interest = pd.concat([keywords_interest,keyword],axis =1)     
        keywords_interest = keywords_interest.reset_index()
        shutil.rmtree(download_directory,ignore_errors=True) # Delete unwanted files and directory
        keywords_interest = keywords_interest.drop(columns='index',axis =1)
        keywords_interest = keywords_interest.replace(['<1'],1)
        change = 0
        if self.sales_start_date != "2004-01":
            year  = int(self.sales_start_date[:4]) - 2004
            print(year)
            month = int(self.sales_start_date[5:]) - 1
            print(month)
            change = year*12 + month 
            print("the change is" + str(change))
        keywords_interest = keywords_interest.iloc[change:,:]
        keywords_interest.index = target_data.index
        keywords_interest = pd.concat([target_data,keywords_interest],axis =1)
        keywords_interest.to_csv('/Users/pooryaselkghafari/Desktop/test.csv')
        return keywords_interest
    
    
    def related_queries (self,keyword):
        # Create the webdriver object. Here the 
        # chromedriver is present in the driver 
        # folder of the root directory.
        link = self.link + self.date_start +"%20"+self.date_end +"&geo=" + self.region + "&q="
        chromeOptions = webdriver.ChromeOptions()
        dir_path = os.path.dirname(os.path.realpath(__file__)) #get the current directory
        os.chdir(dir_path)
        download_directory = dir_path + "/all_keywords"
        Path(download_directory).mkdir(parents=True, exist_ok=True)
        os.chdir(download_directory)
        prefs = {"download.default_directory" : download_directory} #change download directory
        chromeOptions.add_experimental_option("prefs",prefs)
        keyword = keyword.replace(" ","%20")
        driver = webdriver.Chrome(r"./driver/chromedriver",options=chromeOptions)
        link_temp = link + keyword
        driver.get(link_temp)
        time.sleep(5)
        driver.refresh() #refresh the page to avoid error 429
        # Maximize the window and let code stall 
        # for 10s to properly maximise the window.
        driver.maximize_window()
        time.sleep(5)
        # Obtain download button by class name and click.
        button = driver.find_elements("class name", "widget-actions-item.export")#find the download button
        driver.execute_script("arguments[0].click();", button[3])#some fucking damn button is covering the export button. It took me 2 days to realize!! so this code is to uncover it.    
        time.sleep(3)
        driver.close()
        download_directory = download_directory + "/relatedQueries.csv"
        final_keyword_list = pd.read_csv(download_directory,header=None,sep='delimiter',skiprows=4) #clean the file and only keep keywords
        final_keyword_list = final_keyword_list[0].str.split(",",expand=True)
        final_keyword_list = final_keyword_list[[0]]
        final_keyword_list = final_keyword_list[final_keyword_list[0] != 'RISING']
        final_keyword_list = final_keyword_list.drop_duplicates() #remove duplicates
        download_directory = dir_path + "/all_keywords"
        shutil.rmtree(download_directory,ignore_errors=True) # Delete unwanted files and directory
        
        return final_keyword_list


    def one_step(self,data):
        target_data = pd.read_csv(self.path_target)
        print("getting google trends data, do not panic....")
        keyword_interest = self.interest_over_time(data,target_data)
        print("doing the magic....")
        final_keywords = self.causalaty_check(keyword_interest)
        return final_keywords
    
    def keyword_map (self,n_round=1):
        print("mapping initiated, round 1")
        data = pd.read_csv(self.path_kw)
        keyword_list = self.one_step(data)
        print("wraping up first round")
        dir_path = os.path.dirname(os.path.realpath(__file__)) #get the current directory
        os.chdir(dir_path)
        result_path_temp = dir_path + "/results" 
        Path(result_path_temp).mkdir(parents=True, exist_ok=True)
        os.chdir(result_path_temp)
        Path('round1').mkdir(parents=True, exist_ok=True)#make a tem directory to store round1 results
        result_path = result_path_temp + "/round1" + "/results.csv"
        keyword_list.to_csv(result_path)
        if n_round > 1:
            n_round -= 1
            for step in range(n_round):
                keyword_list = list(keyword_list["query"])
                round_number = step + 2
                print("starting round" + str(round_number))
                folder_name = "round" + str(round_number)
                Path(folder_name).mkdir(parents=True, exist_ok=True)#make a tem directory to store round1 results
                for kw in range(len(keyword_list)):
                    print("doing magic for keyword" + keyword_list[kw])
                    file_name = keyword_list[kw] + ".CSV"
                    result_path = result_path_temp + "/round" + str(round_number) + "/" + file_name
                    data = self.related_queries(keyword_list[kw])
                    results = self.one_step(data)
                    results.to_csv(result_path)
                        
                    
      