from cyvcf2 import VCF
import json
from tqdm import tqdm
import glob
import re
import conf.conf as conf
import uuid
import json
import gc
from pymongo.mongo_client import MongoClient

client = MongoClient(
        #"mongodb://127.0.0.1:27017/"
        "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
            conf.database_user,
            conf.database_password,
            conf.database_host,
            conf.database_port,
            conf.database_name,
            conf.database_auth_source,
        )
    )

with open('files/deref_schemas/genomicVariations.json') as json_file:
    dict_properties = json.load(json_file)

def generate(dict_properties):
    total_dict =[]
    i=1
    l=0
    

    for vcf_filename in glob.glob("files/vcf/files_to_read/*.vcf.gz"):
        print(vcf_filename)
        vcf = VCF(vcf_filename, strict_gt=True)
        my_target_list = vcf.samples
        count=0
        
        
        
        num_rows=conf.num_variants
        pbar = tqdm(total = num_rows)
        for v in vcf:
            dict_to_xls={}
            vstringed = str(v)
            v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_NFE_AF=')
            if len(v_splitted) < 2:
                v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_FIN_AF=')
                population = 'FIN'
            if len(v_splitted) < 2:
                v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_SAS_AF=')
                population = 'SAS'
            if len(v_splitted) < 2:
                v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_AMI_AF=')
                population = 'AMI'
            if len(v_splitted) < 2:
                v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_ASJ_AF=')
                population = 'ASJ'
            if len(v_splitted) < 2:
                v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_POPMAX_AF=')
                population = 'POPMAX'
            if len(v_splitted) < 2:
                v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_AMR_AF=')
                population = 'AMR'
            if len(v_splitted) < 2:
                v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_AF=')
                population = 'gnomAD_genomes'
            if len(v_splitted) < 2:
                v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_EAS_AF=')
                population = 'EAS'
            if len(v_splitted) < 2:
                v_splitted = vstringed.split('dbNSFP_gnomAD_genomes_AFR_AF=')
                population = 'AFR'
            
            clinvar_splitted=vstringed.split('CLINVAR_CLNSIG=')
                
            clinvar2_splitted=vstringed.split('CLINVAR_CLNDN=')
            if len(clinvar_splitted) > 1 and len(clinvar2_splitted) >1:
                clinvar_resplitted = clinvar_splitted[1].split(';')
                clinvar2_resplitted = clinvar2_splitted[1].split(';')
                clinicalRelevance = clinvar_resplitted[0]
                conditionId=clinvar2_resplitted[0]
                if clinicalRelevance == 'Conflicting_interpretations_of_pathogenicity':
                    clinicalRelevance='uncertain_significance'
                elif clinicalRelevance == 'Benign/Likely_benign':
                    clinicalRelevance='likely_benign'
                clinicalRelevance = clinicalRelevance.lower()
                dict_to_xls['caseLevelData|clinicalInterpretations|clinicalRelevance']=clinicalRelevance
                dict_to_xls['caseLevelData|clinicalInterpretations|conditionId']=conditionId
                dict_to_xls['caseLevelData|clinicalInterpretations|effect|id']="MedGen:CN517202"
                
                
            try:
                v_resplitted = v_splitted[1].split(';')
                allele_frequency = v_resplitted[0]
                try:
                    allele_frequency = int(allele_frequency)
                except Exception:
                    allele_frequency = allele_frequency.split(',')
                    allele_frequency=int(allele_frequency[0])
                dict_to_xls['frequencyInPopulations|sourceReference']='gnomad.broadinstitute.org/'
                dict_to_xls['frequencyInPopulations|source']='The Genome Aggregation Database (gnomAD)'
                dict_to_xls['frequencyInPopulations|frequencies|population']=population
                dict_to_xls['frequencyInPopulations|frequencies|alleleFrequency']=allele_frequency
            except Exception:
                pass
            try:
                if v.INFO.get('VT') == 'SV': continue
            except Exception:
                pass
            '''
            try:
                allele_frequency = v.INFO.get('AF')
                if isinstance(allele_frequency, float):
                    if allele_frequency > conf.allele_frequency: continue
            except Exception:
                pass
            '''
            
            #print(v)
            
            ref=v.REF
            chrom=v.CHROM
            start=v.start
            end=v.end
            alt=v.ALT
            dict_to_xls['variation|alternateBases'] = alt[0]

            dict_to_xls['variation|referenceBases'] = ref
            try:
                dict_to_xls['variation|variantType'] = v.INFO.get('VT')
                if v.INFO.get('VT') is None:
                    if len(alt[0]) == len(ref):
                        dict_to_xls['variation|variantType']='SNP'
                    else:
                        dict_to_xls['variation|variantType']='INDEL'
            except Exception:
                dict_to_xls['variation|variantType']='UNKNOWN'
            #print(v.INFO.get('ANN'))
            if v.INFO.get('ANN') is not None:
                annot = v.INFO.get('ANN')
                transcripts = annot.split(',')
                dict_to_xls['molecularAttributes|molecularEffects|id'] = ""
                for transcript in transcripts:
                    annotations = transcript.split("|")
                    if '&' in annotations[1]:
                        annot_splitted = annotations[1].split('&')
                        annot_splitted = list(dict.fromkeys(annot_splitted))
                        for annotation in annot_splitted:
                            if dict_to_xls['molecularAttributes|molecularEffects|id'] == "":
                                dict_to_xls['molecularAttributes|molecularEffects|label'] = annotation
                                if annotation == 'missense_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "ENSGLOSSARY:0000150"
                                elif annotation == 'intron_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "ENSGLOSSARY:0000161"
                                elif annotation == 'upstream_gene_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001631"
                                elif annotation == '5_prime_UTR_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001623"
                                elif annotation == 'synonymous_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001819"
                                elif annotation == 'downstream_gene_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001632"
                                elif annotation == 'non_coding_transcript_exon_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001792"
                                elif annotation == '5_prime_UTR_premature_start_codon_gain_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001988"
                                elif annotation == 'splice_region_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001630"
                                elif annotation == 'intergenic_region':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0000605"
                                elif annotation == 'splice_donor_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001575"
                                elif annotation == '3_prime_UTR_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001624"
                                elif annotation == 'splice_acceptor_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001574"
                                elif annotation == 'stop_retained_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001567"
                                               
                            else:
                                dict_to_xls['molecularAttributes|molecularEffects|label'] += "|"+annotation
                                if annotation == 'missense_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"ENSGLOSSARY:0000150"
                                elif annotation == 'intron_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"ENSGLOSSARY:0000161"
                                elif annotation == 'upstream_gene_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001631"
                                elif annotation == '5_prime_UTR_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001623"
                                elif annotation == 'synonymous_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001819"
                                elif annotation == 'downstream_gene_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001632"
                                elif annotation == 'non_coding_transcript_exon_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001792"
                                elif annotation == '5_prime_UTR_premature_start_codon_gain_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001988"
                                elif annotation == 'splice_region_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001630"
                                elif annotation == 'intergenic_region':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0000605"
                                elif annotation == 'splice_donor_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001575"
                                elif annotation == '3_prime_UTR_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001624"
                                elif annotation == 'splice_acceptor_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+ "SO:0001574"
                                elif annotation == 'stop_retained_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+ "SO:0001567"
                                
                    else:
                        annotated_items=[]
                        if annotations[1] not in annotated_items:
                            annotated_items.append(annotations[1])
                            if dict_to_xls['molecularAttributes|molecularEffects|id'] == "":
                                dict_to_xls['molecularAttributes|molecularEffects|label'] = annotations[1]
                                if annotations[1] == 'missense_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "ENSGLOSSARY:0000150"
                                elif annotations[1] == 'intron_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "ENSGLOSSARY:0000161"
                                elif annotations[1] == 'upstream_gene_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001631"
                                elif annotations[1] == '5_prime_UTR_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001623"
                                elif annotations[1] == 'synonymous_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001819"
                                elif annotations[1] == 'downstream_gene_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001632"
                                elif annotations[1] == 'non_coding_transcript_exon_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001792"
                                elif annotations[1] == '5_prime_UTR_premature_start_codon_gain_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001988"
                                elif annotations[1] == 'intergenic_region':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0000605"
                                elif annotations[1] == '3_prime_UTR_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001624"
                                elif annotations[1] == 'stop_retained_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] = "SO:0001567"
                            else:
                                dict_to_xls['molecularAttributes|molecularEffects|label'] += "|"+annotations[1]
                                if annotations[1] == 'missense_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"ENSGLOSSARY:0000150"
                                elif annotations[1] == 'intron_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"ENSGLOSSARY:0000161"
                                elif annotations[1] == 'upstream_gene_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001631"
                                elif annotations[1] == '5_prime_UTR_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001623"
                                elif annotations[1] == 'synonymous_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001819"
                                elif annotations[1] == 'downstream_gene_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001632"
                                elif annotations[1] == 'non_coding_transcript_exon_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001792"
                                elif annotations[1] == '5_prime_UTR_premature_start_codon_gain_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001988"
                                elif annotations[1] == 'intergenic_region':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0000605"
                                elif annotations[1] == '3_prime_UTR_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+"SO:0001624"
                                elif annotations[1] == 'stop_retained_variant':
                                    dict_to_xls['molecularAttributes|molecularEffects|id'] += "|"+ "SO:0001567"
                    #print(dict_to_xls['molecularAttributes|molecularEffects|id'])
                    #print(annotations)
                    if annotations[10] == '':
                        dict_to_xls['molecularAttributes|aminoacidChanges']='.'
                    else:
                        dict_to_xls['molecularAttributes|aminoacidChanges'] = annotations[10]
                    dict_to_xls['molecularAttributes|geneIds'] = annotations[4]

            
            
            zigosity={}
            zigosity['0/1']='GENO:GENO_0000458'
            zigosity['1/0']='GENO:GENO_0000458'
            zigosity['1/1']='GENO:GENO_0000136'
            j=0
            dict_to_xls['caseLevelData|zygosity|id'] =''
            dict_to_xls['caseLevelData|zygosity|label']=''

            for zygo in v.genotypes:
                if dict_to_xls['caseLevelData|zygosity|id'] == '':
                    if zygo[0] == 1 and zygo[1]== 1:
                        dict_to_xls['caseLevelData|zygosity|label'] = '1/1'
                        dict_to_xls['caseLevelData|zygosity|id'] = zigosity['1/1']
                        dict_to_xls['caseLevelData|biosampleId'] = my_target_list[j]
                    elif zygo[0] == 1 and zygo[1]== 0:
                        dict_to_xls['caseLevelData|zygosity|label'] = '1/0'
                        dict_to_xls['caseLevelData|zygosity|id'] = zigosity['1/0']
                        dict_to_xls['caseLevelData|biosampleId'] = my_target_list[j]
                    elif zygo[0] == 0 and zygo[1]== 1:
                        dict_to_xls['caseLevelData|zygosity|label'] = '0/1'
                        dict_to_xls['caseLevelData|zygosity|id'] = zigosity['0/1']
                        dict_to_xls['caseLevelData|biosampleId'] = my_target_list[j]
                        
                else:
                    if zygo[0] == 1 and zygo[1]== 1:
                        dict_to_xls['caseLevelData|zygosity|label'] = dict_to_xls['caseLevelData|zygosity|label'] + '|' + '1/1'
                        dict_to_xls['caseLevelData|zygosity|id'] = dict_to_xls['caseLevelData|zygosity|id'] + '|' + zigosity['1/1']
                        dict_to_xls['caseLevelData|biosampleId'] = dict_to_xls['caseLevelData|biosampleId'] + '|' + my_target_list[j]
                    elif zygo[0] == 1 and zygo[1]== 0:
                        dict_to_xls['caseLevelData|zygosity|label'] = dict_to_xls['caseLevelData|zygosity|label'] + '|' + '1/0'
                        dict_to_xls['caseLevelData|zygosity|id'] = dict_to_xls['caseLevelData|zygosity|id'] + '|' + zigosity['1/0']
                        dict_to_xls['caseLevelData|biosampleId'] = dict_to_xls['caseLevelData|biosampleId'] + '|' + my_target_list[j]
                    elif zygo[0] == 0 and zygo[1]== 1:
                        dict_to_xls['caseLevelData|zygosity|label'] = dict_to_xls['caseLevelData|zygosity|label'] + '|' + '0/1'
                        dict_to_xls['caseLevelData|zygosity|id'] = dict_to_xls['caseLevelData|zygosity|id'] + '|' + zigosity['0/1']
                        dict_to_xls['caseLevelData|biosampleId'] = dict_to_xls['caseLevelData|biosampleId'] + '|' + my_target_list[j]
                    

                j+=1

            chromos=re.sub(r"</?\[>", "", chrom)
            if conf.reference_genome == 'GRCh37':
                dict_to_xls['identifiers|genomicHGVSId'] = 'NC_0000'+str(chromos) + '.10' + ':' + 'g.' + str(start) + ref + '>' + alt[0]
            elif conf.reference_genome == 'GRCh38':
                dict_to_xls['identifiers|genomicHGVSId'] = 'NC_0000'+str(chromos) + '.11' + ':' + 'g.' + str(start) + ref + '>' + alt[0]
            elif conf.reference_genome == 'NCBI36':
                dict_to_xls['identifiers|genomicHGVSId'] = 'NC_0000'+str(chromos) + '.9' + ':' + 'g.' + str(start) + ref + '>' + alt[0]

            dict_to_xls['variation|location|interval|start|value'] = int(start)
            dict_to_xls['variation|location|interval|start|type']="Number"
            dict_to_xls['variation|location|interval|end|value'] = int(end)
            dict_to_xls['variation|location|interval|end|type']="Number"

            dict_to_xls['variation|location|interval|start|value'] = int(start)
            dict_to_xls['variation|location|interval|start|type']="Number"
            dict_to_xls['variation|location|interval|end|value'] = int(end)
            dict_to_xls['variation|location|interval|end|type']="Number"
            dict_to_xls['variation|location|interval|type']="SequenceInterval"
            dict_to_xls['variation|location|type']="SequenceLocation"
            dict_to_xls['variation|location|sequence_id']="HGVSid:" + str(chrom) + ":g." + str(start) + ref + ">" + alt[0]
            dict_to_xls['variantInternalId'] = str(uuid.uuid1())+':' + str(ref) + ':' + str(alt[0])
            

            k=0


            dict_of_properties={}
            for kline, vline in dict_to_xls.items():
                property_value = kline

                
                valor = vline

                if valor:
                    dict_of_properties[property_value]=valor
                    

                elif valor == 0:
                    dict_of_properties[property_value]=valor

            
            #print(dict_properties)
            #print(dict_of_properties)
            definitivedict={}
            for key, value in dict_properties.items():
                if isinstance(value, list):
                    value_list=[]
                    item_dict={}
                    for item in value:
                        outcome = 0
                        if isinstance(item, dict):
                            
                            for ki, vi in item.items():
                                if isinstance(vi, list):
                                    vi_list=[]
                                    subitem_dict={}
                                    for subitem in vi:
                                        if isinstance(subitem, dict):
                                            for k, v in subitem.items():
                                                if isinstance(v, list):
                                                    listitemv=[]
                                                    vivdict={}
                                                    for itemv in v:
                                                    
                                                        if isinstance(itemv, dict):
                                                            #print('ki is {}'.format(ki))
                                                            #print('k is {}'.format(k))
                                                            #print(itemv)
                                                            
                                                            for kiv, viv in itemv.items():
                                                                

                                                                if isinstance(viv, list):

                                                                    for itemviv in viv:
                                                                        if isinstance(itemviv, dict):
                                                                            
                                                                            for kivi, vivi in itemviv.items():
                                                                                new_item = ""
                                                                                new_item = key + "|" + ki + "|" + k + "|" + kiv + "|" + kivi
                                                                                for propk, propv in dict_of_properties.items():
                                                                                    if propk == new_item:
                                                                                        
                                                                                        try:
                                                                                            if 'value' in propk:
                                                                                                vivdict[kiv][kivi]=int(propv)
                                                                                            else:
                                                                                                vivdict[kiv][kivi]=propv
                                                                                        except Exception:
                                                                                            vivdict[kiv]={}
                                                                                            vivdict[kiv][kivi]=propv
                                                                                    elif propk == key + "|" + ki + "|" + k + "|" + kiv:
                                                                                        vivdict[kiv]=propv
                                                                                



                                                                                    
                                                            


                                                                else:
                                                                    new_item = ""
                                                                    new_item = key + "|" + ki + "|" + k + "|" + kiv
                                                                    for propk, propv in dict_of_properties.items():
                                                                        if propk == new_item:
                                                                            #print(propk)
                                                                            vivdict[kiv]=propv





                                                            

                                                        if vivdict != {}:
                                                            #print(vivdict)
                                                            subitem_dict[k]=vivdict
                                                if isinstance(v, dict):
                                                    for k1, v1 in v.items():
                                                        new_item = ""
                                                        new_item = key + "|" + ki + "|" + k + "|" + k1
                                                        for propk, propv in dict_of_properties.items():
                                                            if propk == new_item:
                                                                try:
                                                                    subitem_dict[k][k1]=propv
                                                                except Exception:
                                                                    subitem_dict[k]={}
                                                                    subitem_dict[k][k1]=propv
                                                else:
                                                    new_item = ""
                                                    new_item = key + "|" + ki + "|" + k
                                                    for propk, propv in dict_of_properties.items():
                                                        if propk == new_item:


                                                            try:
                                                                propv = re.sub(r'\s', '', propv)
                                                                respropv = json.loads(propv) 
                                                                subitem_dict[k]=respropv
                                                            except Exception:
                                                                subitem_dict[k]=propv


                                        if subitem_dict != {}:
                                            if subitem_dict not in vi_list and subitem_dict != {}:
                                                

                                                vi_list.append(subitem_dict)

                                            if ki == 'clinicalInterpretations' or ki == 'frequencies':
                                                item_dict[ki]=vi_list
                                            else:
                                                item_dict[ki]=vi_list[0]
                                elif isinstance(vi, dict):
                                    vi_dict={}
                                    for ki1, vi1 in vi.items():
                                        new_item = ""
                                        new_item = key + "|" + ki + "|" + ki1
                                        for propk, propv in dict_of_properties.items():
                                            if propk == new_item:
                                                vi_dict[ki1]=propv 
                                                item_dict[ki]=vi_dict
                                    if vi_dict=={}:
                                        del vi_dict
                                else:
                                    
                                    new_item = ""
                                    new_item = key + "|" + ki
                                    for propk, propv in dict_of_properties.items():
                                        if propk == new_item:
                                            if '|' in propv:
                                                outcome +=1
                                                v1_keys=[]
                                            item_dict[ki]=propv
        
                            if item_dict != {} and item_dict != [{}]:
                                

                                if outcome > 0:
                                    if item_dict not in value_list:
                                        value_list.append(item_dict)
                                    if value_list != []:
                                        itemdict={}
                                        definitivedict[key]=[]
                                        v_array=[]
                                        for itemvl in value_list:

                                            for kvl, vvl in itemvl.items():
                                                if isinstance(vvl, str):
                                                    if '|' in vvl:
                                                        itemv={}
                                                        v_array = vvl.split('|')
                                                        itemv[kvl]=v_array
                                                        v_key = kvl
                                                elif isinstance(vvl, dict):
                                                    
                                                    v1_array=[]
                                                    itemdict[kvl]={}
                                                    v1_keys = []
                                                    for kvl1, vvl1 in vvl.items():
                                                        itemdict[kvl][kvl1]={}
                                                        if isinstance(vvl1, str) and '|' in vvl1:
                                                            vvl1_array = vvl1.split('|')
                                                            for vvlitem in vvl1_array:
                                                                v1_array.append(vvlitem)
                                                            v1_bigkeys = kvl
                                                            if kvl1 not in v1_keys:
                                                                v1_keys.append(kvl1)

                                        if v1_keys != []:
                                            n=0
                                            list_to_def=[]
                                            half_array_number = len(v1_array)/2
                                            itemdict[v1_bigkeys]={}

                                            while n < int(half_array_number):
                                                newdict={}
                                                newdict[v1_bigkeys]={}
                                                num=int(half_array_number+n)
                                                #print(v_array)
                                                #print(v1_array)
                                                newdict[v_key]=v_array[n]
                                                
                                                newdict[v1_bigkeys][v1_keys[0]]=v1_array[n]
                                                newdict[v1_bigkeys][v1_keys[1]]=v1_array[num]
                                                list_to_def.append(newdict)
                                                n +=1
                                            for itemldf in list_to_def:
                                                definitivedict[key].append(itemldf)
                                        elif len(v_array) > 1:
                                            list_to_def=[]
                                            
                                            for itva in v_array:
                                                newdict={}
                                                newdict[v_key]=itva
                                                list_to_def.append(newdict)
                                            for itemldf in list_to_def:
                                                definitivedict[key].append(itemldf)
                                        else:
                                            for itemvl in value_list:
                                                definitivedict[key].append(itemvl) 
                                else:
                                    if key == 'caseLevelData' or key=='frequencyInPopulations':
                                        definitivedict[key]=[]
                                        definitivedict[key].append(item_dict)
                                    else:
                                        definitivedict[key]=item_dict
                                    
                elif isinstance(value, dict):
                    value_dict={}
                    for kd, vd in value.items():
                        if isinstance(vd, list):
                            vd_list=[]
                            value_dict[kd]={}
                            for itemvd in vd:
                                if isinstance(itemvd, dict):
                                    dict_mol={}
                                    list_mol=[]
                                    for kd1, vd1 in itemvd.items():
                                        
                                        new_item = ""
                                        new_item = key + "|" + kd + "|" + kd1
                                        for propk, propv in dict_of_properties.items():
                                            if propk == new_item:
                                                if '|' in propv:
                                                    propv_splitted = propv.split('|')
                                                    propv_splitted=list(dict.fromkeys(propv_splitted))
                                                    t=0
                                                    

                                                    while t < len(propv_splitted):
                                                        dict_mol={}
                                                        try:
                                                            dict_mol[kd1]=propv_splitted[t]
                                                            
                                                        except Exception:
                                                            
                                                            dict_mol[kd1]=propv_splitted[t]
                                                            
                                                        t+=1
                                                        list_mol.append(dict_mol)
                                                    
                                                    t=0
                                                    u=0
                                                    if kd1 == 'label':
                                                        try:
                                                            if len(list_mol) == 2:
                                                                dict_mol_2={}
                                                                dict_mol_2['id']=list_mol[t]['id']
                                                                dict_mol_2['label']=list_mol[t+1]['label']
                                                                try:
                                                                    value_dict[kd].append(dict_mol_2)
                                                                except Exception:
                                                                    value_dict[kd]=[]
                                                                    value_dict[kd].append(dict_mol_2)
                                                        except Exception:
                                                            pass
                                                        else:
                                                            try:
                                                                while u < len(list_mol):
                                                                    dict_mol_2={}
                                                                    dict_mol_2['id']=list_mol[t]['id']
                                                                    indice = int(len(list_mol)/2)
                                                                    dict_mol_2['label']=list_mol[t+indice]['label']
                                                                    try:
                                                                        value_dict[kd].append(dict_mol_2)
                                                                    except Exception:
                                                                        value_dict[kd]=[]
                                                                        value_dict[kd].append(dict_mol_2)
                                                                    t+=1
                                                                    u+=2
                                                            except Exception:
                                                                pass
                                                    
                                                    if value_dict not in vd_list:
                                                        vd_list.append(value_dict)
                                                else:
                                                    if value_dict == {}:
                                                        value_dict[kd]={}
                                                    if 'molecularEffects' in kd:
                                                        try:
                                                            dict_mol[kd1]=propv
                                                            value_dict[kd].append(dict_mol)
                                                        except Exception:
                                                            dict_mol[kd1]=propv
                                                            value_dict[kd]=[]
                                                    else:                                                          
                                                        value_dict[kd][kd1]=propv

                                    #print(list_mol)



                                else:
                                    new_item = ""
                                    new_item = key + "|" + kd
                                    for propk, propv in dict_of_properties.items():
                                        if propk == new_item:
                                            value_dict[kd]=[]
                                            value_dict[kd].append(propv)


                                value_dict = {ka:va for ka,va in value_dict.items() if va != {}}
                                if value_dict != {}:
                                    definitivedict[key]=value_dict
                        else:
                            new_item = ""
                            new_item = key + "|" + kd
                            for propk, propv in dict_of_properties.items():
                                if propk == new_item:
                                    value_dict[kd]=propv
                                    definitivedict[key]=value_dict
                else:
                    new_item = ""
                    new_item = key
                    for propk, propv in dict_of_properties.items():
                        if propk == new_item:
                            definitivedict[key]=propv

            total_dict.append(definitivedict)
            
            if i == num_rows:

                client.beacon.genomicVariations.insert_many(total_dict)
                pbar.update(1)
                break
            elif (i/10000).is_integer():
                client.beacon.genomicVariations.insert_many(total_dict)
                del definitivedict
                del total_dict
                gc.collect()
                total_dict=[]
                pbar.update(1)

            
            pbar.update(1)
            i+=1

    if i != num_rows:
        client.beacon.genomicVariations.insert_many(total_dict)
        
        

    pbar.close()
    return i, l

total_i, l=generate(dict_properties)


if total_i-l > 0:
    print('Successfully inserted {} records into beacon'.format(total_i-l))
else:
    print('No registries found.')