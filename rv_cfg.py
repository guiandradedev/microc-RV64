"""Parte a implementar pelo grupo. Consulte ENUNCIADO.pdf."""
from tracemalloc import stop

from backend_api import REGISTERS, CFG, BasicBlock, Liveness
from ir import (
    Label,
    LabelInstr,
    Jump,
    Return,
    Beq,
    Bne,
    Blt,
    Bge,
    Beqz,
    Bnez
)
BRANCH_TYPES = (Beq, Bne, Blt, Bge, Beqz, Bnez)
TERMINATORS = (Jump, Return, *BRANCH_TYPES)

def build_cfg(function):
    instructions = function.instructions
    total_ins = len(instructions)
    
    # Dicionário que mapeia as labels para mapeamento de sucessores e predecessores
    # Salva no formato {L0: posição na lista de instruções}
    label_index: dict[Label, int] = {}

    # Lista de iniciadores de BasicBlock que serão usados para criar os blocos.
    # O primeiro bloco sempre começa no indice 0 (primeira instrução) e o último bloco sempre termina em total_ins - 1 (última instrução).
    initializers: set[int] = {0} 
    for index, instruction in enumerate(instructions):
        # Toda vez que encontrar um identificador de label ("L0:", "label:", etc), adiciona o index da posição no dicionário e na lista de inicializadores
        if isinstance(instruction, LabelInstr):
            label_index[instruction.label] = index
            initializers.add(index)
            continue

        # Toda vez que encontrar um terminador (jump, return, branches), adiciona o index da posição do próximo bloco na lista de inicializadores
        if isinstance(instruction, TERMINATORS) and index + 1 < total_ins:
            initializers.add(index + 1)
            continue

    # Se não houver instruções, retorna um CFG vazio
    if not instructions:
        return CFG(function=function, blocks={}, entry=None)


    sorted_initializer = sorted(initializers) # Ordena os inicializadores para criar os blocos na ordem correta
    blocks: dict[int, BasicBlock] = {}
    for position, start in enumerate(sorted_initializer):
        # position + 1 = próximo bloco

        # O stop do bloco é o próximo inicializador ou total_ins se for o ultimo bloco
        stop = sorted_initializer[position + 1] if position + 1 < len(sorted_initializer) else total_ins

        # Cria o bloco e o insere no dicionário sem os pred. e succ. que serão preenchidos na próxima iteração
        blocks[start] = BasicBlock(
            start=start,
            stop=stop,
            predecessors=set(),
            successors=set(),
        )

    for start, block in blocks.items():
        last_instruction = instructions[block.stop - 1] # ultima instrução do bloco
        successors = block.successors # recupera o set de sucessores do bloco (inicialmente vazio)

        if isinstance(last_instruction, BRANCH_TYPES):
            # Adiciona o bloco de destino como sucessor
            successors.add(label_index[last_instruction.target])

            # Se houver um bloco após o atual, adiciona ele como sucessor.
            if block.stop in blocks:
                successors.add(block.stop)

        elif isinstance(last_instruction, Jump):
            # Adiciona o bloco de destino como sucessor
            successors.add(label_index[last_instruction.target])

        elif not isinstance(last_instruction, Return) and block.stop in blocks:
            # Adiciona o próximo bloco como sucessor
            successors.add(block.stop)

        # Para cada sucessor salvo na iteração, adiciona o bloco atual como predecessor dele
        for successor in successors:
            blocks[successor].predecessors.add(start)

    return CFG(function=function, blocks=blocks, entry=sorted_initializer[0])
