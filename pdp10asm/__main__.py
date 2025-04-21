import sys

import pdp10asm


def main():
    with open(sys.argv[1]) as f:
        text = f.read()
    assembler = pdp10asm.PDP10Assembler(text)
    program = assembler.assemble()
    print(program.listing_text())


if __name__ == "__main__":
    main()
