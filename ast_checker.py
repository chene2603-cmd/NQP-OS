# ST语法校验器：基于Lark实现IEC 61131-3完整AST解析
# ai_control/ast_checker.py

from lark import Lark, Transformer, v_args, Tree
from lark.exceptions import ParseError
import sys

# 简化版ST语法Transformer（用于AST解析与验证）
class STTransformer(Transformer):
    @v_args(inline=True)
    def number(self, n):
        return float(n) if '.' in n else int(n)

    def identifier(self, n):
        return str(n[0])

    def assignment(self, n):
        return ("assign", n[0], n[1])

    def if_statement(self, n):
        return ("if", n[0], n[1], n[2] if len(n) > 2 else None)

# 初始化ST语法解析器
def init_st_parser():
    # 从st_grammar.lark加载文法（需确保文件同目录）
    try:
        with open('st_grammar.lark', 'r', encoding='utf-8') as f:
            st_grammar = f.read()
        parser = Lark(st_grammar, parser='lalr', transformer=STTransformer())
        return parser
    except FileNotFoundError:
        print("❌ 错误：未找到st_grammar.lark文法文件")
        sys.exit(1)

# ST代码校验主函数
def check_st_code(code: str) -> bool:
    parser = init_st_parser()
    try:
        ast = parser.parse(code)
        print("✅ ST语法正确！")
        print("📊 抽象语法树(AST)：", ast.pretty())
        return True
    except ParseError as e:
        print(f"❌ ST语法错误：{e}")
        return False

# 测试示例
if __name__ == "__main__":
    # 测试正确的ST代码
    test_st_code = """
    PROGRAM TestST
    VAR
        a: INT;
        b: REAL;
    END_VAR
    a := 100;
    b := 3.14;
    IF a > 50 THEN
        b := b + 1.0;
    END_IF
    END_PROGRAM
    """
    check_st_code(test_st_code)