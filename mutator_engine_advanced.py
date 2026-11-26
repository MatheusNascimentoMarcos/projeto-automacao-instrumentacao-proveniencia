import ast
import random
import copy


# ==========================================
# 1. ANÁLISE DE DEPENDÊNCIAS (O Cérebro)
# ==========================================
# Chamadas com efeito colateral de I/O: todas compartilham um "recurso" fictício
# (__io__), então nunca são reordenadas entre si (preserva a ordem de print/arquivos).
IO_BUILTINS = {"print", "open", "input", "exec", "eval", "exit", "quit"}
IO_ATTR_PREFIXES = ("read", "write", "to_", "save", "dump", "load", "open", "close")
IO_RESOURCE = "__io__"


class DependencyVisitor(ast.NodeVisitor):
    """
    Analisa um nó da árvore (uma linha de código) e descobre:
    - O que ele LÊ (Load)
    - O que ele ESCREVE (Store)

    Análise conservadora: na dúvida, considera que há dependência (isso só
    reduz as permutações possíveis, nunca gera uma permutação insegura).
    """

    def __init__(self):
        self.read = set()
        self.written = set()

    @staticmethod
    def _base_name(expr):
        """Nome-base de `a.b[0].c` -> 'a'. None se não for um Name."""
        while isinstance(expr, (ast.Attribute, ast.Subscript)):
            expr = expr.value
        return expr.id if isinstance(expr, ast.Name) else None

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.read.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.written.add(node.id)
        elif isinstance(node.ctx, ast.Del):
            self.written.add(node.id)

    def visit_arg(self, node):
        self.written.add(node.arg)

    def visit_AugAssign(self, node):
        # x += 1 lê E escreve x
        base = self._base_name(node.target)
        if base:
            self.read.add(base)
            self.written.add(base)
        self.generic_visit(node)

    def _mark_container_write(self, node):
        # d['k'] = v  /  obj.attr = v  /  del d['k']  -> escreve no objeto-base
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            base = self._base_name(node)
            if base:
                self.written.add(base)
        self.generic_visit(node)

    def visit_Subscript(self, node):
        self._mark_container_write(node)

    def visit_Attribute(self, node):
        self._mark_container_write(node)

    def visit_Call(self, node):
        func = node.func
        # print(...), open(...), input(...)
        if isinstance(func, ast.Name) and func.id in IO_BUILTINS:
            self.read.add(IO_RESOURCE)
            self.written.add(IO_RESOURCE)
        # lista.append(...), df.dropna(inplace=True), df.to_csv(...), pd.read_csv(...)
        elif isinstance(func, ast.Attribute):
            base = self._base_name(func)
            if base:
                # método pode mutar o objeto in-place: trata como escrita
                self.written.add(base)
            if func.attr.startswith(IO_ATTR_PREFIXES):
                self.read.add(IO_RESOURCE)
                self.written.add(IO_RESOURCE)
        self.generic_visit(node)


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

    @staticmethod
    def _pode_ser_nao_numerico(node):
        """
        True se a expressão contém literais de string/bytes/coleção ou f-string.
        Nesses casos a troca a + b -> b + a pode alterar o resultado
        (concatenação não é comutativa).
        """
        for sub in ast.walk(node):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, (str, bytes)):
                return True
            if isinstance(
                sub, (ast.JoinedStr, ast.List, ast.Tuple, ast.Set, ast.Dict, ast.ListComp)
            ):
                return True
        return False

    def visit_BinOp(self, node):
        # 1. Comutatividade: a + b -> b + a (somente quando seguro)
        # Limitação: se os operandos forem variáveis que guardam str/list, a troca
        # ainda pode alterar o resultado; o motor não infere tipos.
        if isinstance(node.op, (ast.Add, ast.Mult)):
            if not self._pode_ser_nao_numerico(node):
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
            if isinstance(op, ast.Lt):
                new_op = ast.Gt()
            elif isinstance(op, ast.LtE):
                new_op = ast.GtE()
            elif isinstance(op, ast.Gt):
                new_op = ast.Lt()
            elif isinstance(op, ast.GtE):
                new_op = ast.LtE()
            elif isinstance(op, ast.Eq):
                new_op = ast.Eq()  # a == b -> b == a
            elif isinstance(op, ast.NotEq):
                new_op = ast.NotEq()

            if new_op:
                return ast.Compare(left=right, ops=[new_op], comparators=[left])
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
                left=(
                    ast.Name(id=target.id, ctx=ast.Load())
                    if isinstance(target, ast.Name)
                    else target
                ),
                op=operator,
                right=value,
            ),
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
        print(f" Erro na mutação sintática: {e}")
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
                node_b = body[i + 1]

                # Ignora Imports (geralmente queremos eles no topo)
                if isinstance(node_a, (ast.Import, ast.ImportFrom)):
                    continue
                if isinstance(node_b, (ast.Import, ast.ImportFrom)):
                    continue

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
                    body[i], body[i + 1] = body[i + 1], body[i]
                    swaps_made += 1

        if swaps_made == 0:
            print("    Código muito acoplado. Nenhuma permutação segura encontrada.")

        return ast.unparse(tree)
    except Exception as e:
        print(f" Erro na permutação: {e}")
        return codigo_fonte


# ==========================================
# 4. DECOMPOSIÇÃO (Split Inteligente via AST)
# ==========================================
def mutar_decomposicao(codigo_fonte):
    """
    Divide o script em dois arquivos funcionais usando AST.
    """
    try:
        tree = ast.parse(codigo_fonte)

        imports: list[ast.stmt] = [
            node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        logica: list[ast.stmt] = [
            node
            for node in tree.body
            if not isinstance(node, (ast.Import, ast.ImportFrom))
        ]

        if len(logica) < 2:
            return codigo_fonte, ""

        split_idx = len(logica) // 2

        body_part1 = imports + logica[:split_idx]
        tree1 = ast.Module(body=body_part1, type_ignores=[])
        ast.fix_missing_locations(tree1)
        codigo_part1 = ast.unparse(tree1)

        body_part2 = imports + logica[split_idx:]
        tree2 = ast.Module(body=body_part2, type_ignores=[])
        ast.fix_missing_locations(tree2)
        codigo_part2 = ast.unparse(tree2)

        return codigo_part1, codigo_part2

    except Exception as e:
        print(f" Erro na decomposição AST: {e}")
        return codigo_fonte, ""

