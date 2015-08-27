# -*- coding: utf-8 -*-
'''
Created on Aug 25, 2015

@author: pabreu
'''

import json

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

class ReadCompostoSimplesPlugin(plugins.SingletonPlugin, tk.DefaultDatasetForm):
    
    plugins.implements(plugins.IDatasetForm, inherit=True)
    
    def package_types(self):
        return [u'simples', u'composto']


    def show_package_schema(self):
        schema = super(ReadCompostoSimplesPlugin, self).show_package_schema()
        schema['tags']['__extras'].append(tk.get_converter('free_tags_only'))

        # Objectivo:
        schema.update({'objectivo': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })
        
        # vocabulario de peridiocidade de manutencao do recurso
        schema.update({'manutencao_recurso': [tk.get_converter('convert_from_tags')('manutencao_recurso'), tk.get_validator('ignore_missing')]})

        # Idioma
        schema.update({'idioma': [tk.get_converter('convert_from_tags')('vocab_iso_639_2'), tk.get_validator('ignore_missing')] })
        # Codificacao_caracteres
        schema.update({'codificacao_caracteres': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })

        # Notas
        schema.update({'anotacoes': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })

        # Responsavel Produtor
        schema.update({'responsavel_produtor_nome': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })
        schema.update({'responsavel_produtor_email': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })
        schema.update({'responsavel_produtor_telefone': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })
        schema.update({'responsavel_produtor_und_organica': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })
        
        # Consulta online
        schema.update({'consulta_online': [tk.get_converter('convert_from_extras'), self.convert_to_list_dict() ] })
        schema.update({'consulta_online_tuple_list': [self.convert_to_tuple_list('consulta_online') ] })

        # georreferenciado
        schema.update({'georreferenciado': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })

        # tipo_representacao_espacial
        schema.update({'tipo_representacao_espacial': [tk.get_converter('convert_from_tags')('vocab_representacao_espacial'), tk.get_validator('ignore_missing') ] })
        
        # Resolucao espacial: string json
        schema.update({'resolucao_espacial': [tk.get_converter('convert_from_extras'), self.convert_to_list_dict() ] })
        schema.update({'resolucao_espacial_tuple_list': [self.convert_to_tuple_list('resolucao_espacial') ] })
        
        # sistema_referencia:
        schema.update({'sistema_referencia': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })

        # extensao_geografica:
        schema.update({'extensao_geografica': [tk.get_converter('convert_from_tags')('vocab_extensao_geografica'), tk.get_validator('ignore_missing')] })
        
        # totalidade_area
        schema.update({'totalidade_area': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })

        # Meta-Meta dados:
        # metameta_data_criacao
        schema.update({'metameta_data_criacao': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })
                
        # metameta_norma
        schema.update({'metameta_norma': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })

        schema.update({'anotacoes': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })
        
        # Especifico de composto:
        schema.update({'vigencia_inicio': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })
        schema.update({'vigencia_fim': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')] })
        
        return schema
        

    def convert_to_list_dict(self):
        def callable(key, data, errors, context):
            table_data = data[key]
            if not table_data:
                data[key] = json.dumps([])
            else:
                data[key] = table_data
        return callable

        
    def convert_to_tuple_list(self, json_field_name):
        def callable(key, data, errors, context):
            str_table_data = data[(json_field_name,)]
            if not str_table_data:
                data[key] = []
            else:
                table = json.loads(str_table_data)  # list of dict
                table_data = [ tuple(dict_line.values()) for dict_line in table ]
                data[key] = table_data
        return callable
        
