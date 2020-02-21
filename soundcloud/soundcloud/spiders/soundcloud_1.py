# -*- coding: utf-8 -*-
import json
import re
import pandas as pd
import scrapy
from scrapy.http import Request

class Soundcloud1Spider(scrapy.Spider):
    name = 'soundcloud_1'

    def __init__(self):

        self.file_name = 'results/soundcloud.csv'


    def start_requests(self):
        try:
            with open('profiles_to_parse.txt', 'r', encoding='utf-8') as f:
                profiles = f.readlines()
                for profile in profiles:
                    yield Request(url=profile, callback=self.parse)
        except FileNotFoundError:
            print('Please provide profiles_to_parse.txt in the project folder')

    def parse(self, response):
        script = response.xpath('/html/body/script[9]/text()').get()
        half = re.search(r'(?<=\{\}\}\)\}\,\[)(.*)(\]\}\]\)\;)', script).group(1)
        almost = re.search(r'(\{\"avatar)(.*)(?=)', half).group(0)
        clean_dict = json.loads(almost)
        try:
            half_desc = clean_dict['description'].strip().replace('\n','')
            email_list = re.findall(r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", half_desc)  
        except AttributeError:
            pass
        result_dict = {
            'url':response.url,
            'artist name':None,
        }
        result_dict['artist name'] = clean_dict['username']
        c = 1
        try:
            for n in range(len(email_list)):
                result_dict[f'email_{c}'] = email_list[n]
                c+=1
        except UnboundLocalError:
            pass
        df = pd.DataFrame([result_dict])
        try:
            file_df = pd.read_csv(self.file_name)
            if len(df.columns) > len(file_df.columns):
                new_df = pd.concat([file_df, df], axis=0, ignore_index=True, sort=False)
            else:
                new_df = pd.concat([file_df, df], axis=0, ignore_index=True, sort=False)
            new_df.drop_duplicates(inplace=True)
            new_df.to_csv(self.file_name, mode='w',header=True, index=None)               
        except FileNotFoundError:
            df.to_csv(self.file_name,mode='w', header=True, index=None)
