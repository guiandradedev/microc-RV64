"""Parte a implementar pelo grupo. Consulte ENUNCIADO.pdf."""
from backend_api import REGISTERS, CFG, BasicBlock, Liveness, InstructionLiveness
from ir import uses, defs

def solve_liveness(cfg):
    # Gerar os conjuntos de livein, liveout, use e def vazios para cada bloco
    live_in = {}
    live_out = {}
    block_uses = {}
    block_defs = {}
    for key in cfg.blocks:
        live_in[key] = set()
        live_out[key] = set()
        block_uses[key] = set()
        block_defs[key] = set()

    # Para cada bloco, itero sobre suas instrucoes para calcular o use/def e incluir na definição do bloco 
    for key, block in cfg.blocks.items():
        for index in range(block.start, block.stop):
            instruction = cfg.function.instructions[index]
            block_uses[key].update(uses(instruction) - block_defs[key])
            block_defs[key].update(defs(instruction))

    # Enquanto houver ao menos 1 alteração em live_in/live_out de algum bloco
    # Percorro os blocos, atualizo o live_out como o live_in dos sucessores
    # Atualizo live_in com a formula LiveIn[B] = Use[B] U (LiveOut[B] - Def[B])
    # Se houver modificação, itero os blocos mais uma vez
    # Se não houver modificação em nenhum dos blocos, finalizo o loop
    changed = True
    while changed:
        changed = False
        for key, block in cfg.blocks.items():
            new_live_out = set()
            for succ in block.successors:
                new_live_out.update(live_in[succ])
            new_live_in = block_uses[key] | (new_live_out - block_defs[key])

            if new_live_in != live_in[key] or new_live_out != live_out[key]:
                live_in[key] = new_live_in
                live_out[key] = new_live_out
                changed = True

    return Liveness(live_in=live_in, live_out=live_out)

def solve_instruction_liveness(cfg, liveness):
    """Retorne os conjuntos antes e depois de cada instrução."""

    # Define os conjuntos live_before e live_after vazios
    live_before = {}
    live_after = {}

    # Percorre cada bloco e define atual = live_out[bloco]
    for key, block in cfg.blocks.items():
        current = set(liveness.live_out[key])

        # Percorre a lista de instruções ao contrario
        # na 1. iteracao, define que o live_after da instrução é o live_out do bloco
        # calcula o novo current como a união de use(I) com current - def(I)
        # define o live_before da instrução como current
        # ai na próxima iteração, o live_after será o live_before da instrução anterior, e assim por diante
        for index in range(block.stop - 1, block.start - 1, -1):
            instruction = cfg.function.instructions[index]
            live_after[index] = current.copy()
            current = uses(instruction) | (current - defs(instruction))
            live_before[index] = current.copy()

    return InstructionLiveness(before=live_before, after=live_after)

def printa_tabela(cfg, block_uses, block_defs, live_in, live_out):
    print(
        f"{'Bloco':<8}{'USE':<20}{'DEF':<20}{'LIVE_IN':<15}{'LIVE_OUT':<15}"
        f"{'SUCC':<10}{'PRED':<10}"
    )
    for key, block in cfg.blocks.items():
        print(
            f"{key:<8}"
            f"{mostrar_conjuntos(block_uses[key]):<20}"
            f"{mostrar_conjuntos(block_defs[key]):<20}"
            f"{mostrar_conjuntos(live_in[key]):<15}"
            f"{mostrar_conjuntos(live_out[key]):<15}"
            f"{mostrar_blocos(block.successors):<10}"
            f"{mostrar_blocos(block.predecessors):<10}"
        )

def mostrar_conjuntos(conj):
    regs = sorted(conj, key=lambda reg: reg.id)
    return "{" + ", ".join(f"v{reg.id}" for reg in regs) + "}"

def mostrar_blocos(blocos):
    return "{" + ", ".join(map(str, sorted(blocos))) + "}"