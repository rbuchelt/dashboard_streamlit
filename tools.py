# Função para formatação dos dados
def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor: .2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor: .2f} milhões'