import pandas as pd
#create a df based on the flags
def configureDataFrame(options):
    columnslist=[]
    optionsbydefault=['isHavingNullData','%NullData','isHavingNanValues','%NanValues','isHavingBlankValues','%BlankValues','DataType']
    for i in range(len(options)):
        if(options[i]==1):
            columnslist.append(optionsbydefault[i])
    return pd.DataFrame(columns=columnslist) 

def isHavingNullData(df,columnname):
    if perNullData(df,columnname)>0:
        return True
    else:
        return False
def perNullData(df,columnname):
    return df[df[columnname].isNull()].count()/df.count()

def isHavingNanValues(df,columnname):
    if perNanValues(df,columnname)>0:
        return True
    else:
        return False
def perNanValues(df,columnname): 
    return df[df[columnname].cast("bigint").isNull()].count()/df.count()
def isHavingBlankValues(df,columnname):
    if perBlankValues(df,columnname)>0:
        return True
    else:
        return False
def perBlankValues(df,columnname): 
    return df[df[columnname]==''].count()/df.count()
def dataType(df,columnname):
    return df.schema[columnname].dataType
functionList=[isHavingNullData,perNullData,isHavingNanValues,perNanValues,isHavingBlankValues,perBlankValues,dataType]

def analyze(df,options):
    analysisdf=configureDataFrame(options)
    print(analysisdf)
    for i in df.columns:
        analysisdf=analysisdf.append(ColumnAnalyser(df,i,options),ignore_index=True)
        
    return analysisdf    
    #print(i)
    
    #cm=columnNullPercentage(df,i)
    #print(cm)
    #ab=ab.append({"ColumnName":i,"%NullData":str(cm)},ignore_index=True)
    
            
def ColumnAnalyser(df,columnname,options):
    #analysisdf=configureDataFrame(options)
    samplefunctionname=['isHavingNullData','%NullData','isHavingNanValues','%NanValues','isHavingBlankValues','%BlankValues','DataType']
    #functionList=[isHavingNullData,perNullData,isHavingNanValues,perNanValues,isHavingBlankValues,perBlankValues,dataType]
    Dict={}
    Dict["columnName"]=columnname
    for i in range(len(options)):
        if(options[i]==1):
            Dict[samplefunctionname[i]]=functionList[i](df,columnname)
    return Dict        
            
        