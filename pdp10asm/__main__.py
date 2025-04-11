import sys

import pdp10asm


def main():
    with open(sys.argv[1]) as f:
        text = f.read()
    assembler = pdp10asm.PDP10Assembler(text)
    assembler.assemble()
    print("SYMBOLS:")
    for symbol in assembler.symbol_table.user_symbols():
        print(f"{symbol.name}:\t{symbol.value:012o}\tDEF: {symbol.source_line}")
    print()
    for key, value in assembler.program.items():
        print(f"{key:06o}:\t{value:012o}")


if __name__ == "__main__":
    main()
