import random
import numpy as np
import matplotlib.pyplot as plt

# Parâmetros do algoritmo
TAMANHO_POPULACAO = 100
GERACOES = 50
NUM_NOS = 10
CAPACIDADE_BATERIA = 45 # Capacidade total de bateria(em unidades de energia)
CAPACIDADE_TRANSITO = np.random.randint(1,5, size=(NUM_NOS,NUM_NOS))
CONDICOES_TRANSITO = np.random.randint(1,5, size=(NUM_NOS,NUM_NOS))
CONSUMO_ENERGIA = np.random.randint(1,5, size=(NUM_NOS,NUM_NOS))
TAXA_MUTACAO = 0.0005

# Gera simétria para simular rota bidirecional
for i in range(NUM_NOS):
    for j in range(i+1,NUM_NOS):
        CONDICOES_TRANSITO[j][i] = CONDICOES_TRANSITO[i][j]
        CONSUMO_ENERGIA[j][i] = CONSUMO_ENERGIA[i][j]

# Passo 1: Inicializar a população
def inicializar_populacao():
    populacao = []
    for _ in range(TAMANHO_POPULACAO):
        # Gera uma sequência aleatória
        rota = random.sample(range(NUM_NOS), NUM_NOS)
        populacao.append(rota)
    return populacao

# Passo 2: Avaliar fitness
def avaliar_fitness(individuo):
    tempo_total = 0
    energia_total = 0
    for i in range(len(individuo)-1):
        inicio = individuo[i]
        fim = individuo[i+1]
        tempo_total += CONDICOES_TRANSITO[inicio][fim]
        energia_total += CONSUMO_ENERGIA[inicio][fim]

    # Adiciona o retorno ao ponto inicial (rota fechada)
    tempo_total += CONDICOES_TRANSITO[individuo[-1]][individuo[0]]
    energia_total += CONSUMO_ENERGIA[individuo[-1]][individuo[0]]

    return tempo_total + energia_total

# Passo 3: Seleção de pais (torneio)
def selecionar_pais(populacao, fitness):
    tamanho_torneio = 3 # Número de indivíduos no torneio
    pai1 = max(random.sample(list(zip(populacao, fitness)), tamanho_torneio), key=lambda x: x[1])[0]
    pai2 = max(random.sample(list(zip(populacao, fitness)), tamanho_torneio), key=lambda x: x[1])[0]
    return pai1,pai2

# Passo 4: Cruzamento(crossover)
def crossover(pai1, pai2):
    tamanho = len(pai1)
    inicio,fim = sorted(random.sample(range(tamanho),2))
    filho1 = [-1] * tamanho
    filho2 = [-1] * tamanho
    
    # Copia uma sequencia dos pais
    filho1[inicio:fim] = pai1[inicio:fim]
    filho2[inicio:fim] = pai2[inicio:fim]
    
    preencher_genes(filho1, pai2,inicio,fim)
    preencher_genes(filho2, pai1,inicio,fim)

    return filho1, filho2

def preencher_genes(filho,pai,inicio,fim):
    tamanho = len(filho)
    pos = fim
    for gene in pai:
        if gene not in filho:
            if pos == tamanho:
                pos = 0
            filho[pos] = gene
            pos +=1

# Passo 5: Mutação
def mutar(individuo):
    if  random.random() < TAXA_MUTACAO:
        i, j = random.sample(range(len(individuo)),2)
        individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo

# Algoritmo genético
def algoritmo_genetico():
    bateria_total = CAPACIDADE_BATERIA
    populacao = inicializar_populacao()
    melhor_solucao = None
    melhor_aptidao = float('-inf')
    progresso_aptidao = []  # Lista para registrar o progresso da melhor aptidão

    for geracao in range(GERACOES):
        # Avaliar fitness de cada indivíduo
        fitness = [avaliar_fitness(individuo) for individuo in populacao]

        # Melhor indivíduo da geração
        melhor_atual = max(populacao, key=lambda ind: avaliar_fitness(ind))
        aptidao_atual = avaliar_fitness(melhor_atual)

        # Atualiza a melhor solução encontrada
        if aptidao_atual > melhor_aptidao:
            melhor_solucao = melhor_atual
            melhor_aptidao = aptidao_atual
        # Aqui vai entrar a classe responsável por controlar a necessidade de recarga!!

        progresso_aptidao.append(-melhor_aptidao)  # Registrar aptidão (negativa para coerência)
        #bateria_total = bateria_total - melhor_atual

        print(f'Geração {geracao}: Melhor Aptidão = {-melhor_aptidao}')

        # Criar nova geração
        nova_populacao = []
        while len(nova_populacao) < TAMANHO_POPULACAO:
            pai1, pai2 = selecionar_pais(populacao, fitness)
            filho1, filho2 = crossover(pai1, pai2)
            nova_populacao.append(mutar(filho1))
            nova_populacao.append(mutar(filho2))
        populacao = nova_populacao

    valor_bateria = gera_valor_bateria(melhor_solucao)
    cidade_custo = dict(zip(melhor_solucao,valor_bateria))

    for i in range(len(melhor_solucao)):
        bateria_total = bateria_total - melhor_solucao[i]
        bateria_total = verifica_bateria(bateria_total,i,cidade_custo)

    print(cidade_custo)

    return melhor_solucao, melhor_aptidao, progresso_aptidao, bateria_total

# Classe responsável por verificar a bateria, esta classe sempre verificará o 
#  total da bateria levando em conta o custo para chegar a próxima cidade, desta
#  forma, caso a bateria não for suficiente para a cidade seguinte da próxima será,
#  comparado os custos e abastecido onde for mais em conta
def verifica_bateria(bateria_total,i,cidade_custo):
    if(bateria_total <= 5):
        if(analisar_custo(cidade_custo,i)):
            return abastecer(bateria_total,cidade_custo[i+1],i)
        else:
            return abastecer(bateria_total, cidade_custo[i],i)
    else:
        return bateria_total

# Classe responsável por abastecer o veículo
def abastecer(bateria, custo, i):
    bateria = CAPACIDADE_BATERIA - bateria
    custo_total = custo*bateria
    print("\nBateria recarregada na cidade: ",i,"\nCusto da bateria por unidade é de: ",custo,"\nCusto da recarga total foi de: ",custo_total)
    bateria = CAPACIDADE_BATERIA
    return(bateria)

# Classe responsável por analisar o custo da bateria na cidade atual e da próxima
def analisar_custo(cidade_custo,i):
    if(i<=8):
        if(cidade_custo[i] > cidade_custo[i+1]):
            return True
        else:
            return False

# Classe responsável por atribuir um "custo" base para unidade de bateria
def gera_valor_bateria(rota1):
    lista_valores = []
    for _ in range(len(rota1)):
        valor = round(random.uniform(5.50, 6.15),2)
        lista_valores.append(valor)
    return lista_valores

# Classe responsável por plotar a evolução da aptidão
def plotar_progresso(progresso_aptidao):
    plt.plot(progresso_aptidao)
    plt.xlabel("Geração")
    plt.ylabel("Melhor Aptidão")
    plt.title("Progresso do Algoritmo Genético")
    plt.show()

# Classe reponsável por plotar o caminho pelo qual o "caixeiro" percorreu
def plotar_progresso_caixeiro(rota):
    plt.plot(rota)
    plt.xlabel("Caminhos percorridos")
    plt.ylabel("Cidades a percorrer")
    plt.title("Progresso do Algoritmo Genético")
    plt.show()

# Executar o algoritmo
melhor_rota, melhor_aptidao, progresso_aptidao, total_bateria = algoritmo_genetico()

# Imprimir resultados finais
print("\nMelhor solução encontrada:")
print(f"Rota: {melhor_rota}")
print(f"Tempo total de viagem: {melhor_aptidao}")  # Mostrar aptidão positiva
print(f"Reserva final de bateria: {total_bateria}")

# Plotar progresso do algoritmo
plotar_progresso(progresso_aptidao)

# Plotar a rota percorrida em meio a gráficos
plotar_progresso_caixeiro(melhor_rota)
        
# Implementar:
#   A bateria diminui conforme o peso das "cidades" pelas quais o caixeiro viajou
#   Adicionar preço referente ao custo da unidade da bateria por cidade
#       Neste caso avaliar se é menos custoso abastecer na cidade atual ou na próxima
#        se eventualmente a bateria atual for suficiente para apenas viajar a próxima cidade
#        esta implementação funcionará desta forma, a cada cidade será analisado o nível da beteria,
#        caso o total for até 5 unidades a menos que a próxima viagem, será analisado os custos de
#        combustível entre a cidade atual e a próxima. Abastecer onde for mais em conta!