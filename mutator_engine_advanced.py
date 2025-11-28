import ast
import random
import copy

# ==========================================
# 1. ANÁLISE DE DEPENDÊNCIAS (O Cérebro)
# ==========================================
class DependencyVisitor(ast.NodeVisitor):
    """
    Analisa um nó da árvore (uma linha de código) e descobre:
    - O que ele LÊ (Load)
    - O que ele ESCREVE (Store)
    """
    def __init__(self):
        self.read = set()
        self.written = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.read.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.written.add(node.id)
        # AugAssign (+=) é leitura E escrita
        elif isinstance(node.ctx, ast.Del):
            self.written.add(node.id)

    def visit_arg(self, node):
        self.written.add(node.arg)

def get_dependencies(node):
    visitor = DependencyVisitor()
    visitor.visit(node)
    return visitor.read, visitor.written

# ==========================================
# 2. MUTAÇÕES SINTÁTICAS (Equivalência)
# ==========================================
class SyntacticEquivalenceTransformer(ast.NodeTransformer):
    """
    Aplica várias transformações que mantêm a lógica intacta.
    """
    
    def visit_BinOp(self, node):
        # 1. Comutatividade: a + b -> b + a
        if isinstance(node.op, (ast.Add, ast.Mult)):
            # Evita trocar se for concatenação de string literal para não quebrar lógica visual
            if not (isinstance(node.left, ast.Constant) and isinstance(node.left.value, str)):
                node.left, node.right = node.right, node.left
        return self.generic_visit(node)

    def visit_Compare(self, node):
        # 2. Inversão de Comparação: a < b -> b > a
        # Só funciona para comparações simples (binárias)
        if len(node.ops) == 1 and len(node.comparators) == 1:
            op = node.ops[0]
            left = node.left
            right = node.comparators[0]
            
            new_op = None
            if isinstance(op, ast.Lt): new_op = ast.Gt()
            elif isinstance(op, ast.LtE): new_op = ast.GtE()
            elif isinstance(op, ast.Gt): new_op = ast.Lt()
            elif isinstance(op, ast.GtE): new_op = ast.LtE()
            elif isinstance(op, ast.Eq): new_op = ast.Eq() # a == b -> b == a
            elif isinstance(op, ast.NotEq): new_op = ast.NotEq()

            if new_op:
                return ast.Compare(
                    left=right,
                    ops=[new_op],
                    comparators=[left]
                )
        return self.generic_visit(node)

    def visit_AugAssign(self, node):
        # 3. Desfazer Atribuição Aumentada: x += 1 -> x = x + 1
        # Isso ajuda a ver se a IA entende as duas formas
        operator = node.op
        target = node.target
        value = node.value
        
        # Cria: target = target OP value
        new_node = ast.Assign(
            targets=[target],
            value=ast.BinOp(
                left=ast.Name(id=target.id, ctx=ast.Load()) if isinstance(target, ast.Name) else target,
                op=operator,
                right=value
            )
        )
        return ast.copy_location(new_node, node)

def mutar_equivalencia_sintatica(codigo_fonte):
    try:
        tree = ast.parse(codigo_fonte)
        transformer = SyntacticEquivalenceTransformer()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        return ast.unparse(new_tree)
    except Exception as e:
        print(f"⚠️ Erro na mutação sintática: {e}")
        return codigo_fonte

# ==========================================
# 3. PERMUTAÇÃO DE BLOCOS (Reordenação)
# ==========================================
def mutar_permutacao_blocos(codigo_fonte):
    """
    Tenta reordenar declarações no nível superior (Module level).
    Funciona para qualquer script (ETL, ML, Simples).
    """
    try:
        tree = ast.parse(codigo_fonte)
        body = tree.body
        swaps_made = 0
        
        # Tentamos fazer várias passadas para embaralhar bem
        for _ in range(3): 
            for i in range(len(body) - 1):
                node_a = body[i]
                node_b = body[i+1]
                
                # Ignora Imports (geralmente queremos eles no topo)
                if isinstance(node_a, (ast.Import, ast.ImportFrom)): continue
                if isinstance(node_b, (ast.Import, ast.ImportFrom)): continue

                read_a, write_a = get_dependencies(node_a)
                read_b, write_b = get_dependencies(node_b)
                
                # Regras de Segurança para Troca:
                # 1. B não lê o que A escreve (Dependência Direta)
                conflict_1 = not read_b.isdisjoint(write_a)
                # 2. A não lê o que B escreve (Dependência Reversa)
                conflict_2 = not read_a.isdisjoint(write_b)
                # 3. B não escreve na mesma variável que A (Conflito de Escrita)
                conflict_3 = not write_b.isdisjoint(write_a)
                
                if not (conflict_1 or conflict_2 or conflict_3):
                    # SWAP!
                    body[i], body[i+1] = body[i+1], body[i]
                    swaps_made += 1
        
        if swaps_made == 0:
            print("   ℹ️ Código muito acoplado. Nenhuma permutação segura encontrada.")
            
        return ast.unparse(tree)
    except Exception as e:
        print(f"⚠️ Erro na permutação: {e}")
        return codigo_fonte

# ==========================================
# 4. DECOMPOSIÇÃO (Split Inteligente)
# ==========================================
def mutar_decomposicao(codigo_fonte):
    """
    Quebra o script, mas tenta levar os imports para a parte 2
    para aumentar a chance de execução bem sucedida.
    """
    lines = codigo_fonte.splitlines()
    if len(lines) < 2:
        return codigo_fonte, ""

    imports = [line for line in lines if line.strip().startswith(("import ", "from "))]
    
    # Divide na metade (após os imports)
    non_import_indices = [i for i, l in enumerate(lines) if not l.strip().startswith(("import ", "from "))]
    if not non_import_indices:
        return "\n".join(lines), ""
        
    start_logic = non_import_indices[0]
    remainder = len(lines) - start_logic
    split_point = start_logic + (remainder // 2)
    
    part1 = "\n".join(lines[:split_point])
    # Parte 2 ganha uma cópia dos imports
    part2 = "\n".join(imports + lines[split_point:])
    
    return part1, part2