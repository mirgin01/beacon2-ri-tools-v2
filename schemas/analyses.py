import json
import xlwings as xw
import re

file_to_open='analyses.json'
# Opening JSON file 
f = open(file_to_open,) 
   
# returns JSON object as  
# a dictionary 
data = json.load(f) 
   
commonDefinitions = open('commondefinitions.json')
commonDefinitions = json.load(commonDefinitions)
commonComponents = open('beaconcommoncomponents.json')
commonComponents = json.load(commonComponents)



def data_types(data):
    commonDefinitions = open('commondefinitions.json')
    commonDefinitions = json.load(commonDefinitions)
    commonComponents = open('beaconcommoncomponents.json')
    commonComponents = json.load(commonComponents)
    dict_types={}
    list_of_definition_keys=[]
    for kprinc, vprinc in data.items():
        if kprinc == 'properties':
            for key, value in vprinc.items():
                dict_types[key]={}
                for k, v in value.items():
                    if k == "type":
                        dict_types[key]['type']=v
                    elif k == '$ref':
                        dict_types[key]['type']={}
                        if 'commonDefinitions' in v:
                            v_splitted = v.split('/')
                            for kcd, vcd in commonDefinitions.items():
                                if kcd == v_splitted[-1]:
                                    for kcd1, vcd1 in vcd.items():
                                        if 'ontologyTerm' in vcd1:
                                            dict_types[key]['type']='ontologyTerm.json'
                                        elif kcd1 == 'type':
                                            dict_types[key]['type']=vcd1
                        elif 'beaconCommonComponents' in v:
                            v_splitted = v.split('/')
                            for kcd, vcd in commonComponents.items():
                                if kcd == v_splitted[-1]:
                                    for kcd1, vcd1 in vcd.items():
                                        if 'ontologyTerm' in vcd1:
                                            dict_types[key]['type']='ontologyTerm.json'
                                        elif kcd1 == 'type':
                                            dict_types[key]['type']=vcd1
                        elif '.json' in v:
                            splitted_v=v.split('/')
                            dict_types[key]['type']=splitted_v[-1]
                        elif 'definitions' in v:
                            list_of_definition_keys.append(key)
                            splitted_v=v.split('/')
                            a = open(file_to_open)
                            data_a=json.load(a)
                            for keyx, valuex in data_a.items():
                                if keyx == 'definitions':
                                    for kx,vx in valuex.items():
                                        if kx == splitted_v[-1]:
                                            for kx1, vx1 in vx.items():
                                                if kx1 == 'items':
                                                    for kx2, vx2 in vx1.items():
                                                        if '.json' in vx2:
                                                            vx2_splitted = vx2.split('/')
                                                            dict_types[key]['items']=vx2_splitted[-1]
                                                elif kx1 == 'type':
                                                    dict_types[key]['type']=vx1
                                                elif kx1 == 'properties':
                                                    for kx2, vx2 in vx1.items():
                                                        for kx3, vx3 in vx2.items():
                                                            if kx3 == '$ref':
                                                                vx3_splitted = vx3.split('/')
                                                                dict_types[key][kx2]=vx3_splitted[-1]
                                                            elif kx3 == 'items':
                                                                for kx4, vx4 in vx3.items():
                                                                    if '.json' in vx4:
                                                                        vx4_splitted = vx4.split('/')
                                                                        dict_items={}
                                                                        dict_items['items']=vx4_splitted[-1]
                                                                        dict_types[key][kx2]=dict_items
                                                            elif kx3 == 'type':
                                                                try:
                                                                    dict_items['type']=vx3
                                                                    dict_types[key][kx2]=dict_items
                                                                except UnboundLocalError:
                                                                    dict_types[key][kx2]=vx3
                                                if isinstance(vx1, dict):
                                                    for kx2, vx2 in vx1.items():
                                                        if isinstance(vx2,dict):
                                                            
                                                            for kx3, vx3 in vx2.items():
                                                                if 'items' in kx3:
                                                                    v_to_split = vx2['items']
                                                                    for kts, vts in v_to_split.items():
                                                                        if kts == '$ref':
                                                                            if isinstance(vts, str):
                                                                                vts_splitted = vts.split('/')
                                                                                if '.json' in vts_splitted[-1]:
                                                                                    dict_types[key]['items']=vts_splitted[-1]
                                                                                else:
                                                                                    dict_types[key]['arraytype']=vts_splitted[-1]
                                                                        else:
                                                                            dict_types[key]['items']=v_to_split
                    elif k == 'items':
                        for kcd, vcd in v.items():
                            if kcd == '$ref':
                                if 'definitions' in vcd:
                                    vcd_splitted = vcd.split('/')
                                    a = open(file_to_open)
                                    data_a=json.load(a)
                                    for keyx, valuex in data_a.items():
                                        if keyx == 'definitions':
                                            for kx,vx in valuex.items():
                                                if kx == vcd_splitted[-1]:
                                                    data_vcd = vx
                                else:
                                    vcd_splitted = vcd.split('/')
                                    dict_types[key]['items']=vcd_splitted[-1]
                                    vcd_file = open(vcd_splitted[-1])
                                    data_vcd = json.load(vcd_file) 
                                for keyv, itemv in data_vcd.items():
                                    if keyv == 'properties':
                                        vcd_dict = itemv
                                    elif keyv == 'required':
                                        dict_types[key]['required']=itemv
                                for key2, item2 in vcd_dict.items():
                                    for keyd, itemd in item2.items():
                                        if keyd == "type":
                                            if itemd=='array':
                                                pass
                                            else:
                                                dict_types[key][key2]=itemd
                                        elif keyd == "items":
                                            if isinstance(itemd, dict):
                                                for ki, vi in itemd.items():
                                                    if ki =='$ref':
                                                        dict_types[key][key2]={}
                                                        vi_splitted = vi.split('/')
                                                        dict_types[key][key2]['arraytype']=vi_splitted[-1]
                                        elif keyd == '$ref':
                                            if '.json' in itemd:
                                                item_splitted = itemd.split('/')
                                                dict_types[key][key2]=item_splitted[-1]
                                            elif 'commonDefinitions' in itemd:
                                                v_splitted = itemd.split('/')
                                                for kcd, vcd in commonDefinitions.items():
                                                    if kcd == v_splitted[-1]:
                                                        for kcd1, vcd1 in vcd.items():
                                                            if 'ontologyTerm' in vcd1:
                                                                dict_types[key][key2]='ontologyTerm.json'
                                                            elif kcd1 == 'type':
                                                                dict_types[key][key2]=vcd1
                                        elif 'oneOf' in keyd:
                                            dict_types[key][key2]=itemd
        elif kprinc == 'required':
            dict_types[kprinc]=vprinc
        dictio_return={}
        dictio_return['dict_types']=dict_types
        dictio_return['list']=list_of_definition_keys
    return dictio_return

returned = data_types(data)
dict_types=returned['dict_types']

list_of_definition_keys=returned['list']






def subtypes(file):
    age = open(file) 
    subdict = {}
    data = json.load(age)
    for key, value in data.items():
        if key == 'properties':
            for k,v in value.items():
                if k == 'required':
                    subdict[k]=v
                else:
                    subdict[k]=""
                if isinstance(v, dict):
                    for k1, v1 in v.items():
                        if k1 == 'type':
                            if v1 == 'array':
                                subdict[k]['type']='array'
                            else:
                                subdict[k]=v1
                        elif k1 == '$ref':
                            if 'ontologyTerm' in v1:
                                subdict[k]= 'ontologyTerm.json'
                            elif 'commonDefinitions' in v1:
                                v1_splitted = v1.split('/')
                                for kcd, vcd in commonDefinitions.items():
                                    if kcd == v1_splitted[-1]:
                                        for kcd1, vcd1 in vcd.items():
                                            if 'ontologyTerm' in vcd1:
                                                subdict[k]='ontologyTerm.json'
                                            elif kcd1 == 'type':
                                                subdict[k]={}
                                                subdict[k]=vcd1

                            else:
                                v1_splitted = v1.split('/')
                                subdict[k]=v1_splitted[-1]
                        elif k1 == 'oneOf':
                            subdict[k]={}
                            subdict[k]['oneOf']=[]
                            for valor in v1:
                                for kval, vval in valor.items():
                                    if kval == '$ref':
                                        vval_splitted = vval.split('/')
                                        subdict[k]['oneOf'].append(vval_splitted[-1])
                        elif k1 == 'items':
                            for k2, v2 in v1.items():
                                if k2 == '$ref':
                                    if '.json' in v2:
                                        v2_splitted = v2.split('/')
                                        subdict[k]={}
                                        subdict[k]['items']=v2_splitted[-1]
                                    else:
                                        v2_splitted = v2.split('/')
                                        subdict[k]={}
                                        for keyx, valuex in data.items():
                                            if keyx == 'definitions':
                                                for kx, vx in valuex.items():
                                                    if kx == v2_splitted[-1]:
                                                        for k1x, v1x in vx.items():
                                                            if k1x == 'properties':
                                                                for k2x, v2x in v1x.items():
                                                                    for k3x, v3x in v2x.items():
                                                                        if k3x == '$ref':
                                                                            if 'ontologyTerm' in v3x:
                                                                                subdict[k][k2x]='ontologyTerm.json'
                                                                            else:
                                                                                splitted_v = v3x.split('/')
                                                                                double_split = splitted_v[-1].split('/')
                                                                                subdict[k][k2x]=double_split[-1]
                                                                        elif k3x == 'type':
                                                                            subdict[k][k2x]=v3x
                                                            elif k1x == 'required':
                                                                subdict[k][k1x]=v1x
        elif key == 'type':
            subdict['type']=value
        elif key == 'oneOf':
            subdict['oneOf']=[]
            for valor in value:
                for kval, vval in valor.items():
                    if kval == '$ref':
                        vval_splitted = vval.split('/')
                        subdict['oneOf'].append(vval_splitted[-1])
    return subdict

def oneof_function(oneof_array):
    list_oneof=[]
    for value in oneof_array:
        value1=subtypes(value)
        list_oneof.append(value1)
    for val in list_oneof:
        for k, v in val.items():
            if k == 'oneOf':
                list_oneof2=[]
                for lor in v:
                    lor1=subtypes(lor)
                    list_oneof2.append(lor1)

                nova_llista=[]
                for item in list_oneof2:
                    for clau, valor in item.items():
                        if 'ontologyTerm' in valor:
                            nou_dict={}
                            nou_dict[clau]={}
                            nou_dict[clau]['id']=""
                            nou_dict[clau]['label']=""
                            if nou_dict not in nova_llista:
                                nova_llista.append(nou_dict)
                        elif '.json' in valor:
                            nou_dict={}
                            nou_dict[clau]=subtypes(valor)
                            if nou_dict not in nova_llista:
                                nova_llista.append(nou_dict)
                        elif 'number' in valor:
                            nou_dict[clau]=0
                            if nou_dict not in nova_llista:
                                nova_llista.append(nou_dict)
                        elif 'string' in valor:
                            nou_dict[clau]=""
                            if nou_dict not in nova_llista:
                                nova_llista.append(nou_dict)
            else:
                if isinstance(v, dict):
                    new_dict={}
                    new_dict[k]={}
                    for ki, vi in v.items():
                        new_dict[k][ki]={}
                        if 'ontologyTerm' in vi:
                            new_dict[k][ki]["id"]=""
                            new_dict[k][ki]["label"]=""
                            if new_dict not in nova_llista:
                                nova_llista.append(new_dict)
                        elif '.json' in vi:
                            elementvi=subtypes(vi)
                            new_dict[k][ki]=elementvi
                            if new_dict not in nova_llista:
                                nova_llista.append(new_dict)
    listing=[]
    for item in nova_llista:
        new_dict={}
        for k, v in item.items():
            new_dict[k]={}
            if isinstance(v,dict):
                for key, value in v.items():
                    if 'ontologyTerm' in value:
                        new_dict[k][key]={}
                        new_dict[k][key]["id"]=""
                        new_dict[k][key]["label"]=""
                    elif '.json' in value:
                        valornou=subtypes(value)
                        new_dict[k][key]=valornou
                    elif 'number' in value:
                        new_dict[k][key]=0
                    elif 'string' in value:
                        new_dict[k][key]=""
                    elif key == 'type':
                        pass
                    else:
                        new_dict[k][key]=value
            elif k == 'value':
                new_dict[k]=0

        listing.append(new_dict)
    new_listing=[]
    for item in listing:
        typed_dict={}
        for k, v in item.items():
            if k == 'typedQuantities':
                typed_dict[k]={}
                for key, value in v.items():
                    if key == 'quantity':
                        typed_dict[k][key]={}
                        for clau, valor in value.items():
                            if 'ontologyTerm' in valor:
                                typed_dict[k][key][clau]={}
                                typed_dict[k][key][clau]["id"]=""
                                typed_dict[k][key][clau]["label"]=""
                            elif '.json' in valor:
                                valor_nou=subtypes(valor)
                                typed_dict[k][key][clau]=valor_nou
                            elif 'number' in valor:
                                typed_dict[k][key][clau]=0
                            elif 'string' in valor:
                                typed_dict[k][key][clau]=""
                            elif clau == 'type':
                                pass
                            else:
                                typed_dict[k][key][clau]=valor
        
            else:
                new_listing.append(item)
        new_listing.append(typed_dict)
    nuevalista=[]
    for item in new_listing:
        if item != {}:
            nuevalista.append(item)
    llisteta=[]
    for item in nuevalista:
        typed_dict2={}
        for k, v in item.items():
            if k == 'typedQuantities':
                typed_dict2[k]={}
                for key, value in v.items():
                    if key == 'quantity':
                        typed_dict2[k][key]={}
                        if isinstance(value, dict):
                            for clau, valor in value.items():
                                typed_dict2[k][key][clau]={}
                                if isinstance(valor, dict):
                                    for ki, vi in valor.items():
                                        if 'ontologyTerm' in vi:
                                            typed_dict2[k][key][clau][ki]={}
                                            typed_dict2[k][key][clau][ki]["id"]=""
                                            typed_dict2[k][key][clau][ki]["label"]=""
                                        elif '.json' in vi:
                                            valor_nou=subtypes(vi)
                                            typed_dict2[k][key][clau][ki]=valor_nou
                                        elif 'number' in vi:
                                            typed_dict2[k][key][clau][ki]=0
                                        elif 'string' in vi:
                                            typed_dict2[k][key][clau][ki]=""
                                        elif ki == 'type':
                                            pass
                                        else:
                                            typed_dict2[k][key][clau][ki]=vi
                                elif clau == 'value':
                                        typed_dict2[k][key][clau]=0
            else:
                if item not in llisteta:
                    llisteta.append(item)
        llisteta.append(typed_dict2)
    llista_final=[]
    for item in llisteta:
        if item != {}:
            llista_final.append(item)
    return llista_final


def oneofunc(array):
    new_array=[]
    for item in array:
        if 'ontologyTerm' in item:
            new_item={}
            new_item['id']=""
            new_item['label']=""
        elif 'Timestamp' in item:
            new_item=""
        else:
            new_item = subtypes(item)
        new_array.append(new_item)
    new_array2=[]
    for item in new_array:
        dict_2={}
        if isinstance(item, dict):
            for k,v in item.items():
                if 'string' in v:
                    dict_2[k]=""
                elif 'ontologyTerm' in v:
                    dict_2[k]={}
                    dict_2[k]["id"]=""
                    dict_2[k]["label"]=""
                elif '.json' in v:
                    element=subtypes(v)
                    dict_2[k]=element
                elif 'integer' in v:
                    dict_2[k]=0
                elif 'type' in k:
                    pass
                else:
                    dict_2[k]=v
        new_array2.append(dict_2)
    new_array3=[]
    for item in new_array2:
        dict_3={}
        if isinstance(item, dict):
            for k,v in item.items():
                dict_3[k]={}
                if isinstance(v, dict):
                    for key, value in v.items():
                        if 'string' in value:
                            dict_3[k][key]=""
                else:
                    dict_3[k]=v
        new_array3.append(dict_3)
    new_array4=[]
    for item in new_array3:
        if item == {}:
            new_array4.append("")
        else:
            new_array4.append(item)   

    return new_array4    




def overtypes(element):
    overtypes={}
    if isinstance(element, dict):
        for key, value in element.items():
            if isinstance(value, bool):
                overtypes[key]=value
            elif '.json' in value:
                new_value=subtypes(value)
                overtypes[key]=new_value
            elif 'string' in value:
                new_value=""
                overtypes[key]=new_value
            elif 'CURIE' in value:
                new_value=""
                overtypes[key]=new_value
            elif 'boolean' in value:
                new_value=True
                overtypes[key]=new_value
            elif isinstance(value, dict):
                new_value=""
                for k, v in value.items():
                    if k == 'oneOf':
                        if 'complexValue.json' in v:
                            new_value=oneof_function(v)
                        else:
                            new_value=oneofunc(v)
                if new_value != "":
                    overtypes[key]=new_value
                else:
                    overtypes[key]=value
            elif isinstance(value, list):
                overtypes[key]=value   
            elif value=='':
                overtypes[key]=value                
    return overtypes





def dict_overtypes(element):
    superovertypes={}
    for key, value in element.items():
        if isinstance(value, dict):
            superovertypes[key]={}
            for k, v in value.items():
                if 'CURIE' in v:
                    superovertypes[key][k]=''
                elif 'string' in v:
                    superovertypes[key][k]=''
                elif '.json' in v:
                    superovertypes[key][k]=subtypes(v)
                elif 'boolean' in v:
                    superovertypes[key][k]=True
                elif 'oneOf' in k:
                    superovertypes[key][k]=overtypes(v)
                elif k == 'items':
                    list_items=[]
                    list_items.append(v)
                    superovertypes[key]=list_items
        else:
            superovertypes[key]=value
    return superovertypes




def super_overtypes(element):
    superovertypes={}
    for key, value in element.items():
        if isinstance(value, dict):
            superovertypes[key]={}
            for k, v in value.items():
                if isinstance(v, dict):
                    superovertypes[key][k]={}
                    for k1, v1 in v.items():
                        if 'CURIE' in v1:
                            superovertypes[key][k][k1]=""
                        elif 'string' in v1:
                            superovertypes[key][k][k1]=""
                        elif '.json' in v1:
                            superovertypes[key][k]=subtypes(v1)
                        elif 'oneOf' in k1:
                            superovertypes[key][k]=oneofunc(v1)
                        elif 'number' in v1:
                            superovertypes[key][k][k1]=0
                else:
                    superovertypes[key][k]=v
        else:
            superovertypes[key]=value
    return superovertypes




def megaovertypes(element):
    superovertypes={}
    for key, value in element.items():
        if isinstance(value, dict):
            superovertypes[key]={}
            for k, v in value.items():
                if k == 'items':
                    list_items=[]
                    list_items.append(v)
                    superovertypes[key]=list_items
                else:
                    superovertypes[key][k]=v
        else:
            superovertypes[key]=value
    return superovertypes


          



def disease():          
    element=subtypes('disease.json')
    element=overtypes(element)
    element=overtypes(element)
    element=dict_overtypes(element)
    return element

def measure():          
    element=subtypes('measurement.json')
    element=overtypes(element)
    element=overtypes(element)
    element=dict_overtypes(element)
    element=super_overtypes(element)
    return element

def ontologyTerm():
    element=subtypes('ontologyTerm.json')
    element=overtypes(element)
    return element

def exposure():
    element=subtypes('exposure.json')
    element=overtypes(element)
    element=dict_overtypes(element)
    return element

def procedure():
    element=subtypes('procedure.json')
    element=overtypes(element)
    element=overtypes(element)
    element=dict_overtypes(element)
    return element

def pedigree():
    element=subtypes('pedigree.json')
    element=overtypes(element)
    element=dict_overtypes(element)
    element=super_overtypes(element)
    return element 

def phenotypicFeature():
    element=subtypes('phenotypicFeature.json')
    element=overtypes(element)
    element=overtypes(element)
    element=dict_overtypes(element)
    element=super_overtypes(element)
    element=megaovertypes(element)
    return element    

def evidence():
    element=subtypes('evidence.json')
    element=overtypes(element)
    element=dict_overtypes(element)
    return element

def treatment():
    element=subtypes('treatment.json')
    element=overtypes(element)
    element=dict_overtypes(element)
    element=super_overtypes(element)
    element=super_overtypes(element)
    element=megaovertypes(element)
    return element

list_of_definitions_required=[]
list_of_properties_required=[]
list_of_headers_definitions_required=[]


for key, value in dict_types.items():
    if isinstance(value, dict):
        for k, v in value.items():
            if k == 'required':
                for item in v:
                    all_name = key + '_' + item
                    list_of_headers_definitions_required.append(key)
                    list_of_definitions_required.append(all_name)

for key, value in dict_types.items():
    if key == 'required':
        for item in value:
            list_of_properties_required.append(item)

finaldict={}


for key, value in dict_types.items():
    if key not in list_of_definition_keys:
        items_dict={}
        list_of_items=[]
        if isinstance(value, dict):
            for k,v in sorted(value.items()):              
                if k == 'items':
                    if 'disease' in v:
                        items_dict = disease()
                    elif 'measure' in v:
                        items_dict = measure()
                    elif 'ontologyTerm' in v:
                        items_dict = ontologyTerm()
                    elif 'exposure' in v:
                        items_dict = exposure()
                    elif 'procedure' in v:
                        items_dict = procedure()
                    elif 'pedigree' in v:
                        items_dict = pedigree()
                    elif 'phenotypicFeature' in v:
                        items_dict = phenotypicFeature()
                    elif 'evidence' in v:
                        items_dict = evidence()
                    elif 'treatment' in v:
                        items_dict = treatment()
                elif k == 'type':
                    if v == 'array':
                        list_of_items.append(items_dict)
                        finaldict[key]=list_of_items
                    elif 'ontologyTerm' in v:
                        items_dict=ontologyTerm()
                        finaldict[key]=items_dict
                    elif 'object' in v:
                        items_dict={}
                        finaldict[key]=items_dict
                    elif 'string' in v:
                        finaldict[key]=''
    elif key in list_of_definition_keys:
        finaldict[key]={}
        items_dict={}
        if isinstance(value, dict):
            for k,v in sorted(value.items()):
                if k == 'items':
                    if 'ontologyTerm' in v:
                        finaldict[key]=ontologyTerm()
                elif 'integer' in v:
                        finaldict[key][k]=0
                elif 'string' in v:
                        finaldict[key][k]=''
                elif 'object' in v:
                        finaldict[key][k]={}
                        finaldict[key][k]['availability']=True
                        finaldict[key][k]['availabilityCount']=0
                        finaldict[key][k]['distribution']={}
                elif isinstance(v, dict):
                    finaldict[key][k]={}
                    for k1, v1 in v.items():
                        if k1 == 'items':
                            if 'ontologyTerm' in v1:
                                items_dict = ontologyTerm()
                            elif '.json' in v1:
                                if 'disease' in v1:
                                    items_dict = disease()
                                elif 'measure' in v1:
                                    items_dict = measure()
                                elif 'ontologyTerm' in v1:
                                    items_dict = ontologyTerm()
                                elif 'exposure' in v1:
                                    items_dict = exposure()
                                elif 'procedure' in v1:
                                    items_dict = procedure()
                                elif 'pedigree' in v1:
                                    items_dict = pedigree()
                                elif 'phenotypicFeature' in v1:
                                    items_dict = phenotypicFeature()
                                elif 'evidence' in v1:
                                    items_dict = evidence()
                                elif 'treatment' in v1:
                                    items_dict = treatment()
                            elif 'integer' in v1:
                                items_dict = 0
                            elif 'string' in v1:
                                items_dict = ""
                            elif 'Ethnicity' in v1:
                                items_dict = {}
                                items_dict['id']=""
                                items_dict['label']=""
                            elif 'Sex' in v1:
                                items_dict = {}
                                items_dict['id']=""
                                items_dict['label']=""
                            elif 'GeographicLocation' in v1:
                                items_dict = {}
                                items_dict['id']=""
                                items_dict['label']=""
                        elif k1 == 'type':
                            if v1 == 'array':
                                list_of_items=[]
                                list_of_items.append(items_dict)
                                finaldict[key][k]=list_of_items
                            elif 'ontologyTerm' in v:
                                items_dict=ontologyTerm()
                                finaldict[key][k]=items_dict
                            elif 'object' in v:
                                items_dict={}
                                finaldict[key][k]=items_dict
                            elif 'string' in v:
                                finaldict[key][k]=''
                        elif k1 == 'arraytype':
                            b = open(file_to_open)
                            data_b=json.load(b)
                            for kb, vb in data_b.items():
                                if kb == 'definitions':
                                    definitions_dict=vb   
                            for kd, vd in definitions_dict.items():
                                if kd == v1:
                                    arraydict = vd
                            for ka, va in arraydict.items():
                                if ka == 'properties':
                                    propertiesdict=va
                            for kp, vp in propertiesdict.items():
                                finaldict[key][k][kp]={}
                                for kp1, vp1 in vp.items():
                                    if kp1 == 'type':
                                        if vp1 == 'string':
                                            finaldict[key][k][kp]=''
                                        elif vp1 == 'number':
                                            finaldict[key][k][kp]=0
                                    elif kp1 == '$ref':
                                        if 'ontologyTerm' in vp1:
                                            finaldict[key][k][kp]=ontologyTerm()
                                        elif 'definitions' in vp1:
                                            vp1_splitted = vp1.split('/')
                                            c = open(file_to_open)
                                            data_c=json.load(c)
                                            for kbc, vbc in data_c.items():
                                                if kbc == 'definitions':
                                                    definitions_dictc=vbc   
                                            for kdc, vdc in definitions_dictc.items():
                                                if kdc == vp1_splitted[-1]:
                                                    arraydictc = vdc
                                            for kac, vac in arraydictc.items():
                                                if kac == 'properties':
                                                    propertiesdictc=vac
                                            for kpc, vpc in propertiesdictc.items():
                                                for kpc1, vpc1 in vpc.items():
                                                    if kpc1 == 'type':
                                                        if vpc1 == 'string':
                                                            finaldict[key][k][kp][kpc]=''
                                                        elif vpc1 == 'object':
                                                            finaldict[key][k][kp][kpc]={}



 







def generate(dict_properties):
    list_of_excel_items=[]

    for key, value in dict_properties.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for ki, vi in item.items():
                        if isinstance(vi, list):
                            for subitem in vi:
                                if isinstance(subitem, dict):
                                    for k, v in subitem.items():
                                        if isinstance(v, dict):
                                            for k1, v1 in v.items():
                                                if isinstance(v1, dict):
                                                    for k2, v2 in v1.items():
                                                        if isinstance(v2, dict):
                                                            for k3, v3 in v2.items():
                                                                new_item = ""
                                                                new_item = key + "_" + ki + "_" + k + "_" + k1 + "_" + k2 + "_" + k3
                                                                list_of_excel_items.append(new_item)            
                                                        else:
                                                            new_item = ""
                                                            new_item = key + "_" + ki + "_" + k + "_" + k1 + "_" + k2
                                                            list_of_excel_items.append(new_item)                                        
                                                else:
                                                    new_item = ""
                                                    new_item = key + "_" + ki + "_" + k + "_" + k1
                                                    list_of_excel_items.append(new_item)
                                        else:
                                            new_item = ""
                                            new_item = key + "_" + ki + "_" + k
                                            list_of_excel_items.append(new_item)
                        elif isinstance(vi, dict):
                            for ki1, vi1 in vi.items():
                                if isinstance(vi1, dict):
                                    if vi1 == {}:
                                        new_item = ""
                                        new_item = key + "_" + ki + "_" + ki1
                                        list_of_excel_items.append(new_item)  
                                    else:
                                        for ki2, vi2 in vi1.items():
                                            new_item = ""
                                            new_item = key + "_" + ki + "_" + ki1 + "_" + ki2
                                            list_of_excel_items.append(new_item)     
                                else:
                                    new_item = ""
                                    new_item = key + "_" + ki + "_" + ki1
                                    list_of_excel_items.append(new_item)      
                        else:
                            new_item = ""
                            new_item = key + "_" + ki
                            list_of_excel_items.append(new_item) 
        elif isinstance(value, dict):
            for kd, vd in value.items():
                if isinstance(vd, list):
                    if isinstance(vd[0], dict):
                        for kd1, vd1 in vd[0].items():
                            if isinstance(vd1, dict):
                                for kd2, vd2 in vd1.items():
                                    new_item = ""
                                    new_item = key + "_" + kd + "_" + kd1 + "_" + kd2
                                    list_of_excel_items.append(new_item)
                            else:
                                new_item = ""
                                new_item = key + "_" + kd + "_" + kd1
                                list_of_excel_items.append(new_item)
                    else:
                        new_item = ""
                        new_item = key + "_" + kd
                        list_of_excel_items.append(new_item)
                elif isinstance(vd, dict):
                    for kd1, vd1 in vd.items():
                        if isinstance(vd1, dict):
                            for kd2, vd2 in vd1.items():
                                new_item = ""
                                new_item = key + "_" + kd + "_" + kd1 + "_" + kd2
                                list_of_excel_items.append(new_item)
                        else:
                            new_item = ""
                            new_item = key + "_" + kd + "_" + kd1
                            list_of_excel_items.append(new_item)
                else:
                    new_item = ""
                    new_item = key + "_" + kd
                    list_of_excel_items.append(new_item)
            if value == {}:
                new_item = key
                list_of_excel_items.append(new_item)
        else:
            new_item = ""
            new_item = key
            list_of_excel_items.append(new_item)

    wb = xw.Book('analyses.xlsx')

    sheet = wb.sheets['Sheet1']

    list_columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                    'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ',
                    'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ',
                    'CA', 'CC', 'CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CL', 'CM', 'CN', 'CO', 'CP', 'CQ', 'CR', 'CS', 'CT', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ',
                    'DA', 'DD', 'DD', 'DD', 'DE', 'DF', 'DG', 'DH', 'DI', 'DJ', 'DK', 'DL', 'DM', 'DN', 'DO', 'DP', 'DQ', 'DR', 'DS', 'DT', 'DU', 'DV', 'DW', 'DX', 'DY', 'DZ',
                    'EA', 'EE', 'EE', 'EE', 'EE', 'EF', 'EG', 'EH', 'EI', 'EJ', 'EK', 'EL', 'EM', 'EN', 'EO', 'EP', 'EQ', 'ER', 'ES', 'ET', 'EU', 'EV', 'EW', 'EX', 'EY', 'EZ',
    ]


    '''
    i=0
    for element in list_of_excel_items:
        number_sheet = list_columns[i]+str(1)
        sheet[number_sheet].value = element
        i+=1
        '''
    

    dict_of_properties={}
    list_of_filled_items=[]
    total_dict =[]
    num_registries = 3
    k=0
    j=2
    while j < num_registries:
        i=0
        while i <(len(list_of_excel_items)+2):
            
            property = list_columns[i]+str(1)
            property_value = sheet[property].value

            number_sheet = list_columns[i]+str(j)
            print(number_sheet)
            

            
            valor = sheet[number_sheet].value

            if i > 1:
                if valor is not None and valor != '':
                    list_of_filled_items.append(property_value)

            print(list_of_filled_items)

            if valor:
                dict_of_properties[property_value]=valor
            i +=1

        

        for lispro in list_of_properties_required:
            if lispro not in list_of_filled_items:
                raise Exception(('error: you are not filling all the required fields. missing field is: {}').format(lispro))

        definitivedict={}
        for key, value in dict_properties.items():
            if isinstance(value, list):
                value_list=[]
                for item in value:
                    if isinstance(item, dict):
                        item_dict={}
                        for ki, vi in item.items():
                            if isinstance(vi, list):
                                vi_list=[]
                                for subitem in vi:
                                    if isinstance(subitem, dict):
                                        subitem_dict={}
                                        for k, v in subitem.items():
                                            if isinstance(v, dict):
                                                for k1, v1 in v.items():
                                                    if isinstance(v1, dict):
                                                        for k2, v2 in v1.items():
                                                            if isinstance(v2, dict): 
                                                                for k3, v3 in v2.items():
                                                                    new_item = ""
                                                                    new_item = key + "_" + ki + "_" + k + "_" + k1 + "_" + k2 + "_" + k3
                                                                    for propk, propv in dict_of_properties.items():
                                                                        if propk == new_item:
                                                                            subitem_dict[k][k1]={}
                                                                            subitem_dict[k][k1][k2]={}
                                                                            subitem_dict[k][k1][k2][k3]=propv
                                                            else:
                                                                new_item = ""
                                                                new_item = key + "_" + ki + "_" + k + "_" + k1 + "_" + k2
                                                                for propk, propv in dict_of_properties.items():
                                                                    if propk == new_item:
                                                                        subitem_dict[k][k1]={}
                                                                        subitem_dict[k][k1][k2]=propv   
                                                    else:
                                                        new_item = ""
                                                        new_item = key + "_" + ki + "_" + k + "_" + k1
                                                        for propk, propv in dict_of_properties.items():
                                                            if propk == new_item:
                                                                if subitem_dict == {}:
                                                                    subitem_dict[k]={}
                                                                subitem_dict[k][k1]=propv  
                                            else:
                                                new_item = ""
                                                new_item = key + "_" + ki + "_" + k
                                                for propk, propv in dict_of_properties.items():
                                                    if propk == new_item:
                                                        subitem_dict[k]=propv
                                                        if subitem_dict != {} and subitem_dict[k] != {}:
                                                            if subitem_dict not in vi_list:
                                                                vi_list.append(subitem_dict)
                                                                item_dict[ki]=vi_list[0]
                                                                
                                                
                            elif isinstance(vi, dict):
                                vi_dict={}
                                for ki1, vi1 in vi.items():
                                    if isinstance(vi1, dict):
                                        vi_dict={}
                                        vi_dict[ki1]={}
                                        if vi1 == {}:
                                            new_item = ""
                                            new_item = key + "_" + ki + "_" + ki1
                                            for propk, propv in dict_of_properties.items():
                                                if propk == new_item:
                                                    propv = re.sub(r'\s', '', propv)
                                                    respropv = json.loads(propv)                                                    
                                                    item_dict[ki][ki1]=respropv 
                                        else:  
                                            for ki2, vi2 in vi1.items():
                                                new_item = ""
                                                new_item = key + "_" + ki + "_" + ki1 + "_" + ki2
                                                for propk, propv in dict_of_properties.items():
                                                    if propk == new_item:
                                                        vi_dict[ki1][ki2]=propv
                                                if vi_dict != {}:
                                                    vivilist=[]
                                                    print(vi_dict)
                                                    for kivi, vivi in vi_dict.items():
                                                        if vivi != {}:
                                                            vivilist.append(vivi)
                                                    for vivitem in vivilist:
                                                        if vivitem != {}:
                                                            item_dict[ki]=vi_dict    
                                    else:
                                        new_item = ""
                                        new_item = key + "_" + ki + "_" + ki1
                                        for propk, propv in dict_of_properties.items():
                                            if propk == new_item:
                                                vi_dict[ki1]=propv 
                                                item_dict[ki]=vi_dict
                            else:
                                new_item = ""
                                new_item = key + "_" + ki
                                for propk, propv in dict_of_properties.items():
                                    if propk == new_item:
                                        item_dict[ki]=propv
                            if item_dict != {} and item_dict != [{}]:
                                if item_dict not in value_list:
                                    value_list.append(item_dict)
                        if value_list != []:
                            print(value_list)
                            itemdict={}
                            definitivedict[key]=[]
                            v_array=[]
                            v1_array=[]
                            v2_array=[]
                            v1_keys = []
                            v2_keys=[]
                            kv2dict={}
                            kvl2dict={}
                            v1_bigkeys=[]
                            v2_bigkeys=[]
                            v3_bigkeys=[]
                            for itemvl in value_list:
                                for kvl, vvl in itemvl.items():
                                    if isinstance(vvl, str):
                                        if ',' in vvl:
                                            v_array = vvl.split(',')
                                            for vitem in v_array:
                                                v1_array.append(vitem)
                                            if kvl not in v1_bigkeys:
                                                v1_bigkeys.append(kvl)
                                    elif isinstance(vvl, dict):
                                        itemdict[kvl]={}
                                        for kvl1, vvl1 in vvl.items():
                                            itemdict[kvl][kvl1]={}
                                            if isinstance(vvl1, str) and ',' in vvl1:
                                                vvl1_array = vvl1.split(',')
                                                for vvlitem in vvl1_array:
                                                    v1_array.append(vvlitem)
                                                if kvl not in v1_bigkeys:
                                                    v1_bigkeys.append(kvl)
                                                if kvl1 not in v1_keys:
                                                    v1_keys.append(kvl1)
                                            elif isinstance(vvl1, dict):
                                                if kvl1 not in v2_bigkeys:
                                                    v2_bigkeys.append(kvl1)
                                                    
                                if v1_keys != []:
                                    n=0
                                    list_to_def=[]
                                    newdict={}
                                    for v1bigkey in v1_bigkeys:
                                        newdict[v1bigkey]={}
                                        if v1bigkey == 'measurementValue':
                                            newdict[v1bigkey][v2_bigkeys[0]]={}
                                            newdict[v1bigkey][v2_bigkeys[0]][v3_bigkeys[0]]=''
                                            newdict[v1bigkey][v2_bigkeys[0]][v3_bigkeys[1]]=''
                                        elif v1bigkey == 'assayCode':
                                            newdict[v1bigkey][v1_keys[0]]=""




                                    while n < len(v_array):
                                        num=int(n+len(v_array)-1)
                                        num2=int(n+len(v_array))
                                        num4=int(n+(len(v_array)*2))
                                        num6=int(n+(len(v_array)*3))
                                        for v1bigkey in v1_bigkeys:                                            
                                            if v1bigkey == 'measurementValue':
                                                newdict[v1bigkey][v2_bigkeys[0]][v3_bigkeys[0]]=v2_array[n]
                                                newdict[v1bigkey][v2_bigkeys[0]][v3_bigkeys[1]]=v2_array[num2]
                                                newdict[v1bigkey][v1_keys[3]]=v1_array[num6]
                                            elif v1bigkey == 'assayCode':
                                                newdict[v1bigkey][v1_keys[0]]=v1_array[n]
                                                newdict[v1bigkey][v1_keys[1]]=v1_array[num2]
                                            elif v1bigkey == 'date':
                                                newdict[v1bigkey]=v1_array[num4]
                                        list_to_def.append(newdict)
                                        
                                        n +=1
                                    for itemldf in list_to_def:
                                        definitivedict[key].append(itemldf)
                            else:
                                for itemvl in value_list:
                                    definitivedict[key].append(itemvl)       
            elif isinstance(value, dict):
                value_dict={}
                for kd, vd in value.items():
                    if isinstance(vd, list):
                        vd_list=[]
                        
                        
                        if isinstance(vd[0], dict):
                            dicty={}
                            propv_splitted_id=[]
                            propv_splitted_label=[]
                            arrayofkdvs=[]
                            
                            for kd1, vd1 in vd[0].items():
                                if isinstance(vd1, dict):
                                    for kd2, vd2 in vd1.items():
                                        new_item = ""
                                        new_item = key + "_" + kd + "_" + kd1 + "_" + kd2
                                        for propk, propv in dict_of_properties.items():
                                            if propk == new_item:
                                                value_dict[kd]={}
                                                value_dict[kd][kd1]={}
                                                value_dict[kd][kd1][kd2]=propv
                                else:
                                    new_item = ""
                                    new_item = key + "_" + kd + "_" + kd1
                                    for propk, propv in dict_of_properties.items():
                                        if propk == new_item:
                                            if ',' in propv:
                                                if propv_splitted_id != []:
                                                    propv_splitted_label = propv.split(',')
                                                else:
                                                    
                                                    propv_splitted_id = propv.split(',')
                                                if propv_splitted_label != []:
                                                    n=0
                                                    while n < len(propv_splitted_id):
                                                        dicty={}
                                                        dicty['id']=propv_splitted_id[n]
                                                        dicty['label']=propv_splitted_label[n]
                                                        for kdv, vdv in value_dict.items():
                                                            arrayofkdvs.append(kdv)
                                                        if kd not in arrayofkdvs:
                                                            value_dict[kd]=[]
                                                        value_dict[kd].append(dicty)
                                                        n+=1


                                            else:
                                                dicty[kd1]=propv
                                                arrayofkdvs=[]
                                                for kdv, vdv in value_dict.items():
                                                    arrayofkdvs.append(kdv)
                                                if kd not in arrayofkdvs:
                                                    value_dict[kd]=[]
                                                if dicty not in value_dict[kd]:
                                                    value_dict[kd].append(dicty)

                                
                                if value_dict != {}:
                                    if value_dict not in vd_list:
                                        vd_list.append(value_dict)
                            if vd_list != []:
                                definitivedict[key]=vd_list


                    elif isinstance(vd, dict):
                        for kd1, vd1 in vd.items():
                            if isinstance(vd1, dict):
                                for kd2, vd2 in vd1.items():
                                    new_item = ""
                                    new_item = key + "_" + kd + "_" + kd1 + "_" + kd2
                                    for propk, propv in dict_of_properties.items():
                                        if propk == new_item:
                                            if value_dict == {}:
                                                value_dict[kd]={}
                                            value_dict[kd][kd1]={}
                                            value_dict[kd][kd1][kd2]=propv
                                            definitivedict[key]=value_dict
                            else:
                                new_item = ""
                                new_item = key + "_" + kd + "_" + kd1
                                for propk, propv in dict_of_properties.items():
                                    if propk == new_item:
                                        value_dict[kd][kd1]=propv
                                        definitivedict[key]=value_dict
                        else:
                            new_item = ""
                            new_item = key + "_" + kd
                            for propk, propv in dict_of_properties.items():
                                if propk == new_item:
                                    value_dict[kd]=propv
                                    definitivedict[key]=value_dict
                    else:
                        new_item = ""
                        new_item = key + "_" + kd
                        for propk, propv in dict_of_properties.items():
                            if propk == new_item:
                                value_dict[kd]=propv
                                definitivedict[key]=value_dict
                if value == {}:
                    new_item = ""
                    new_item = key
                    for propk, propv in dict_of_properties.items():
                        if propk == new_item:
                            propv = re.sub(r'\s', '', propv)
                            respropv = json.loads(propv)  
                            definitivedict[key]=respropv
            else:
                new_item = ""
                new_item = key
                for propk, propv in dict_of_properties.items():
                    if propk == new_item:
                        definitivedict[key]=propv
        total_dict.append(definitivedict)
        j+=1
    return total_dict





dict_generado=generate(finaldict)


with open('definitive_bio.json', 'w') as f:
    json.dump(dict_generado, f)

        

