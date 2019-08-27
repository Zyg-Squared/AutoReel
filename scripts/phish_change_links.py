#!/usr/bin/python3
###########
### File Name : phish_change_links.py
### Usage : python3 ./scripts/phish_change_links.py 
### Prerequiste Info : None
### Description : Handy script for Converts href links in emails to {{.URL}}, currently set to avoid .css files
### 
############

import re
import argparse



############################ Changes links in HTML emails or landing pages to use the phishing URL set in your campaign ############################   
if __name__== "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--input_file", "-i", help="convert the hrefs in this file to {{.URL}}")
        #parser.add_argument("--output_file","-o", help="output file")
        args = parser.parse_args()
        print("Input filename: "+str(args.input_file))
        #print("Output filename: "+str(args.output_file))
        
        
        reg_block = re.compile("<a href=\".*?\"")
        with open(str(args.input_file), 'r') as input_file_handler:
            input_file_data = input_file_handler.read().replace('\n', '') 

            
        matches = re.findall(reg_block, str(input_file_data))  
        output = input_file_data
        if matches:
            for match in matches:
                if not str(match).endswith(".css\"") and not str(match).endswith("#\""):
                    print("Match:"+str(match))
                    output = output.replace(match, '<a href=\"{{.URL}}\"') 

        f = open(str(args.input_file),"w") #opens file with name of "test.txt"
        f.write(output)
        f.close()

    except Exception as ex:
        print("Exception:"+str(ex))

print("Program Complete")
############################ - End Function 
