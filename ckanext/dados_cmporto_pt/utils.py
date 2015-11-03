def get_white_listed_package_extras():
    return get_ordered_package_extras()

def get_ordered_package_extras():
    return [
        'objectivo',
        'h_manutencao_recurso',
        'consulta_online',
        'h_idioma',
        'codificacao_caracteres',
        'dataset_data_criacao',
        'dataset_data_atualizacao',
        'vigencia_inicio',
        'vigencia_fim',
        'anotacoes',
        'responsavel_produtor_und_organica',
        'responsavel_produtor_nome',
        'responsavel_produtor_email',
        'responsavel_produtor_telefone',
        'georreferenciado',
        'h_tipo_representacao_espacial',
        'resolucao_espacial',
        'sistema_referencia',
        'h_extensao_geografica',
        'totalidade_area',
        'metameta_norma',
    ]

def get_black_listed_package_resource_extras():
    return [
        'atributos_resource'
    ]
