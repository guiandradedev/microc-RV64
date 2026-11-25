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
    

    label_index: dict[Label, int] = {}
    initializers = set[int] = {0}
    for index, instruction in enumerate(instructions):
        if isinstance(instruction, LabelInstr):
            label_index[instruction] = index
            initializers.add(index)

        if isinstance(instruction, TERMINATORS) and index + 1 < total_ins:
            initializers.add(index + 1)
            
    sorted_initializer = sorted(initializers)
    blocks = dict[int, BasicBlock] = {}
    for position, start in enumerate(sorted_initializer):
        stop = sorted_initializer[position + 1] if position + 1 < len(sorted_initializer) else total_ins
        blocks[start] = BasicBlock(start=start, stop=stop, predecessors=set(), successors=set())
        
    return CFG(function=function, blocks=blocks, entry=sorted_initializer[0] if sorted_initializer else None)
