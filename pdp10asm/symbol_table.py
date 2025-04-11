"""Symbols for the PDP-10 Assembler."""

from .exceptions import AssemblyError


class SymbolTable:
    """Class for handling symbols."""

    def __init__(self):
        """Class for handling symbols."""
        self.symbol_table = {}
        self.load_system_symbols()

    def add_symbol(self, symbol):
        """Add a symbol to the symbol table."""
        self.symbol_table[symbol.name] = symbol

    def add_user_symbol(self, symbol, value, source_line):
        """Add a user symbol and value to the symbols table."""
        symbol = UserSymbol(name=symbol, value=value, source_line=source_line)
        self.add_symbol(symbol)

    def delete_symbol(self, symbol):
        """Remove a symbol from the symbols table."""
        del self.symbol_table[symbol]

    def get_symbol_value(self, symbol):
        """
        Return the value of a symbol from the symbols table.

        Raises:
            AssemblyError - If symbol is not in the symbols table.
        """
        try:
            return self.symbol_table[symbol].value
        except KeyError:
            raise AssemblyError(f"Symbol {symbol!r} is not defined.") from None

    def load_system_symbols(self):
        """Return the inital system symbols."""
        for symbol in SymbolList.get_system_symbols():
            self.add_symbol(symbol)

    def user_symbols(self):
        """Return a list of user defined symbols."""
        return [
            symbol
            for symbol in self.symbol_table.values()
            if isinstance(symbol, UserSymbol)
        ]

    def is_primary_instruction_symbol(self, symbol):
        """Return True if symbol is in the symbol table and is an instruction symbol."""
        if symbol in self.symbol_table and isinstance(
            self.symbol_table[symbol], (InstructionSymbol, InstructionShorthand)
        ):
            return True
        return False

    def is_io_instruction_symbol(self, symbol):
        """Return True if symbol is in the symbol table and is an IO instruction symbol."""
        if symbol in self.symbol_table and isinstance(
            self.symbol_table[symbol], IOInstructionSymbol
        ):
            return True
        return False

    def is_device_code_symbol(self, symbol):
        """Return True if symbol is in the symbol table and device code symbol."""
        if symbol in self.symbol_table and isinstance(
            self.symbol_table[symbol], DeviceCodeSymbol
        ):
            return True
        return False

    def is_user_symbol(self, symbol):
        """Return True if symbol is in the symbol table and is a user defined symbol."""
        if symbol in self.symbol_table and isinstance(
            self.symbol_table[symbol], UserSymbol
        ):
            return True
        return False

    def is_defined(self, symbol):
        """Return True if symbol in in the symbol table."""
        return symbol in self.symbol_table


class BaseSymbol:
    """Base class for symbol table values."""

    shift = 0

    def __init__(self, name, value):
        """Base class for symbol table values."""
        self.name = name
        self.value = value
        self.value <<= self.shift

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


class InstructionSymbol(BaseSymbol):
    """Class for symbols of instruction mnemonics."""

    shift = 27


class InstructionShorthand(BaseSymbol):
    """Class for symbols of instruction shorthands."""

    shift = 21


class IOInstructionSymbol(BaseSymbol):
    """Class for symbols of IO instruction mnemonics."""

    shift = 21


class DeviceCodeSymbol(BaseSymbol):
    """Class for IO device symbols."""

    shift = 0


class UserSymbol(BaseSymbol):
    """Class for user defined symbols."""

    def __init__(self, name, value, source_line):
        """Class for user defined symbols."""
        super().__init__(name, value)
        self.source_line = source_line


class SymbolList:
    """Base class for setting system sybmols."""

    symbol_class = None

    @classmethod
    def get_symbols(cls):
        """Return a list of SymbolList subclasses."""
        return [
            cls.symbol_class(name=key, value=value)
            for key, value in cls.symbols.items()
        ]

    @classmethod
    def get_system_symbols(cls):
        """Return all system symbols."""
        symbols = []
        for symbol_list in cls.__subclasses__():
            for symbol in symbol_list.get_symbols():
                symbols.append(symbol)
        return symbols


class HalfWordDataTransmissionInstructions(SymbolList):
    """Instructions for moving half words."""

    symbol_class = InstructionSymbol
    symbols = {
        "HLL": 0o500,  # Half Left Left
        "HLLI": 0o501,  # Half Left Left Immediate
        "HLLM": 0o502,  # Half Left Left Memory
        "HLLS": 0o503,  # Half Left Left Self
        "HRL": 0o504,  # Half Right Left
        "HRLI": 0o505,  # Half Right Left Immediate
        "HRLM": 0o506,  # Half Right Left Memory
        "HRLS": 0o507,  # Half Right Left Self
        "HLLZ": 0o510,  # Half Left Left Zeros
        "HLLZI": 0o511,  # Half Left Left Zeros Immediate
        "HLLZM": 0o512,  # Half Left Left Zeros Memory
        "HLLZS": 0o513,  # Half Left Left Zeros Self
        "HRLZ": 0o514,  # Half Right Left Zeros
        "HRLZI": 0o515,  # Half Right Left Zeros Immediate
        "HRLZM": 0o516,  # Half Right Left Zeros Memory
        "HRLZS": 0o517,  # Half Right Left Zeros Self
        "HLLO": 0o520,  # Half Left Left Ones
        "HLLOI": 0o521,  # Half Left Left Ones Immediate
        "HLLOM": 0o522,  # Half Left Left Ones Memory
        "HLLOS": 0o523,  # Half Left Left Ones Self
        "HRLO": 0o524,  # Half Right Left Ones
        "HRLOI": 0o525,  # Half Right Left Ones Immediate
        "HRLOM": 0o526,  # Half Right Left Ones Memory
        "HRLOS": 0o527,  # Half Right Left Ones Self
        "HLLE": 0o530,  # Half Left Left Extend
        "HLLEI": 0o531,  # Half Left Left Extend Immediate
        "HLLEM": 0o532,  # Half Left Left Extend Memory
        "HLLES": 0o533,  # Half Left Left Extend Self
        "HRLE": 0o534,  # Half Right Left Extend
        "HRLEI": 0o535,  # Half Right Left Extend Immediate
        "HRLEM": 0o536,  # Half Right Left Extend Memory
        "HRLES": 0o537,  # Half Right Left Extend Self
        "HRR": 0o540,  # Half Right Right
        "HRRI": 0o541,  # Half Right Right Immediate
        "HRRM": 0o542,  # Half Right Right Memory
        "HRRS": 0o543,  # Half Right Right Self
        "HLR": 0o544,  # Half Left Right
        "HLRI": 0o545,  # Half Left Right Immediate
        "HLRM": 0o546,  # Half Left Right Memory
        "HLRS": 0o547,  # Half Left Right Self
        "HRRZ": 0o550,  # Half Right Right Zeros
        "HRRZI": 0o551,  # Half Right Right Zeros Immediate
        "HRRZM": 0o552,  # Half Right Right Zeros Memory
        "HRRZS": 0o553,  # Half Right Right Zeros Self
        "HLRZ": 0o554,  # Half Left Right Zeros
        "HLRZI": 0o555,  # Half Left Right Zeros Immediate
        "HLRZM": 0o556,  # Half Left Right Zeros Memory
        "HLRZS": 0o557,  # Half Left Right Zeros Self
        "HRRO": 0o560,  # Half Right Right Ones
        "HRROI": 0o561,  # Half Right Right Ones Immediate
        "HRROM": 0o562,  # Half Right Right Ones Memory
        "HRROS": 0o563,  # Half Right Right Ones Self
        "HLRO": 0o564,  # Half Left Right Ones
        "HLROI": 0o565,  # Half Left Right Ones Immediate
        "HLROM": 0o566,  # Half Left Right Ones Memory
        "HLROS": 0o567,  # Half Left Right Ones Self
        "HRRE": 0o570,  # Half Right Right Extend
        "HRREI": 0o571,  # Half Right Right Extend Immediate
        "HRREM": 0o572,  # Half Right Right Extend Memory
        "HRRES": 0o573,  # Half Right Right Extend Self
        "HLRE": 0o574,  # Half Left Right Extend
        "HLREI": 0o575,  # Half Left Right Extend Immeditate
        "HLREM": 0o576,  # Half Left Right Extend Memory
        "HLRES": 0o577,  # Half Left Right Extend Self
    }


class FullWordDataTransmissionInstructions(SymbolList):
    """Instructions for moving full words."""

    symbol_class = InstructionSymbol
    symbols = {
        "EXCH": 0o250,  # Exchange
        "BLT": 0o251,  # Block Transfer
        "MOVE": 0o200,  # Move
        "MOVEI": 0o201,  # Move Immediate
        "MOVEM": 0o202,  # Move Memory
        "MOVES": 0o203,  # Move Self
        "MOVS": 0o204,  # Move Swapped
        "MOVSI": 0o205,  # Move Swapped Immediate
        "MOVSM": 0o206,  # Move Swapped Memory
        "MOVSS": 0o207,  # Move Swapped Self
        "MOVN": 0o210,  # Move Negative
        "MOVNI": 0o211,  # Move Negative Immediate
        "MOVNM": 0o212,  # Move Negative Memory
        "MOVNS": 0o213,  # Move Negative Self
        "MOVM": 0o214,  # Move Magnitude
        "MOVMI": 0o215,  # Move Magnitude Immediate
        "MOVMM": 0o216,  # Move Magnitude Memory
        "MOVMS": 0o217,  # Move Magnitude Self
        "PUSH": 0o261,  # Push Down
        "POP": 0o262,  # Pop Up
    }


class ByteMainipulationInstructions(SymbolList):
    """Instructions for byte manipulation."""

    symbol_class = InstructionSymbol
    symbols = {
        "LDB": 0o135,  # Load Byte
        "DPB": 0o137,  # Deposit Byte
        "IBP": 0o133,  # Increment Byte Pointer
        "ILDB": 0o134,  # Increment Pointer and Load Byte
        "IDPB": 0o136,  # Increment Pointer and Deposit Byte
    }


class LogicInstructions(SymbolList):
    """Instructions for shifting, rotating and boolean functions."""

    symbol_class = InstructionSymbol
    symbols = {
        "SETZ": 0o400,  # Set to Zeros
        "SETZI": 0o401,  # Set to Zeros Immediate
        "SETZM": 0o402,  # Set to Zeros Memory
        "SETZB": 0o403,  # Set to Zeros Both
        "SETO": 0o474,  # Set to Ones
        "SETOI": 0o475,  # Set to Ones Immeidate
        "SETOM": 0o476,  # Set to Ones Memory
        "SETOB": 0o477,  # Set to Ones Both
        "SETA": 0o424,  # Set to AC
        "SETAI": 0o425,  # Set to AC Immediate
        "SETAM": 0o426,  # Set to AC Memory
        "SETAB": 0o427,  # Set to AC Both
        "SETCA": 0o450,  # Set to Complement of AC
        "SETCAI": 0o451,  # Set to Complement of AC Immediate
        "SETCAM": 0o452,  # Set to Complement of AC Memory
        "SETCAB": 0o453,  # Set to Complement of AC Both
        "SETM": 0o454,  # Set to Memory
        "SETMI": 0o455,  # Set to Memory Immediate
        "SETMM": 0o456,  # Set to Memory Memory
        "SETMB": 0o457,  # Set to Memory Both
        "SETCM": 0o460,  # Set to Complement of Memory
        "SETCMI": 0o461,  # Set to Complement of Memory Immediate
        "SETCMM": 0o462,  # Set to Complement of Memory Memory
        "SETCMB": 0o463,  # Set to Complement of Memory Both
        "AND": 0o404,  # AND with AC
        "ANDI": 0o405,  # AND with AC Immediate
        "ANDM": 0o406,  # AND with AC Memory
        "ANDB": 0o407,  # AND with AC Both
        "ANDCA": 0o420,  # AND with Complement of AC
        "ANDCAI": 0o411,  # AND with Complement of AC Immediate
        "ANDCAM": 0o412,  # AND with Complement of AC Memory
        "ANDCAB": 0o413,  # AND with Complement of AC Both
        "ANDCM": 0o420,  # AND Complement of Memory with AC
        "ANDCMI": 0o421,  # AND Complement of Memory with AC Immediate
        "ANDCMM": 0o422,  # AND Complement of Memory with AC Memory
        "ANDCMB": 0o423,  # AND Complement of Memory with AC Both
        "ANDCB": 0o440,  # AND Complements of Both
        "ANDCBI": 0o441,  # AND Complements of Both Immediate
        "ANDCBM": 0o442,  # AND Complements of Both to Memory
        "ANDCBB": 0o443,  # AND Complements of Both to Both
        "IOR": 0o434,  # Inclusive OR with AC
        "IORI": 0o435,  # Inclusive OR with AC Immediate
        "IORM": 0o436,  # Inclusive OR with AC to Memory
        "IORB": 0o437,  # Inclusive OR with AC to Both
        "ORCA": 0o454,  # Inclusive OR wtih Complement of AC
        "ORCAI": 0o455,  # Inclusive OR wtih Complement of AC Immediate
        "ORCAM": 0o456,  # Inclusive OR wtih Complement of AC to Memory
        "ORCAB": 0o457,  # Inclusive OR wtih Complement of AC to Both
        "ORCM": 0o464,  # Inclusive OR complement of Memory with AC
        "ORCMI": 0o465,  # Inclusive OR complement of Memory with AC Immediate
        "ORCMM": 0o466,  # Inclusive OR complement of Memory with AC to Memory
        "ORCMB": 0o467,  # Inclusive OR complement of Memory with AC to Both
        "ORCB": 0o470,  # Inclusive OR complements of Both
        "ORCBI": 0o471,  # Inclusive OR complements of Both Immediate
        "ORCBM": 0o472,  # Inclusive OR complements of Both to Memory
        "ORCBB": 0o473,  # Inclusive OR complements of Both to Both
        "XOR": 0o430,  # Exclusive OR with AC
        "XORI": 0o431,  # Exclusive OR with AC Immediate
        "XORM": 0o432,  # Exclusive OR with AC to Memory
        "XORB": 0o433,  # Exclusive OR with AC to Both
        "EQV": 0o444,  # Equivalence
        "EQVI": 0o444,  # Equivalence Immediate
        "EQVM": 0o444,  # Equivalence to Memory
        "EQVB": 0o444,  # Equivalence to Both
        "LSH": 0o242,  # Logical Shift
        "LSHC": 0o246,  # Logical Shift Combined
        "ROT": 0o241,  # Rotate
        "ROTC": 0o245,  # Rotate Combined
    }


class FixedPointArithmeticInstructions(SymbolList):
    """Instructions for fixed point arithmetic."""

    symbol_class = InstructionSymbol
    symbols = {
        "ADD": 0o270,  # Add
        "ADDI": 0o271,  # Add Immediate
        "ADDM": 0o272,  # Add to Memory
        "ADDB": 0o273,  # Add to Both
        "SUB": 0o274,  # Subtract
        "SUBI": 0o275,  # Subtract Immediate
        "SUBM": 0o276,  # Subtract from Memory
        "SUBB": 0o277,  # Subtract from Both
        "IMUL": 0o220,  # Integer Multiply
        "IMULI": 0o221,  # Integer Multiply Immediate
        "IMULM": 0o222,  # Integer Multiply to Memory
        "IMULB": 0o223,  # Integer Multiply to Both
        "MUL": 0o224,  # Multiply
        "MULI": 0o225,  # Multiply Immediate
        "MULM": 0o226,  # Multiply to Memory
        "MULB": 0o227,  # Multiply to Both
        "IDIV": 0o230,  # Integer Divide
        "IDIVI": 0o231,  # Integer Divide Immediate
        "IDIVM": 0o232,  # Integer Divide to Memory
        "IDIVB": 0o233,  # Integer Divide to Both
        "DIV": 0o234,  # Divide
        "DIVI": 0o235,  # Divide Immediate
        "DIVM": 0o236,  # Divide to Memory
        "DIVB": 0o237,  # Divide to Both
        "ASH": 0o240,  # Arithmetic Shift
        "ASHC": 0o244,  # Aritmetic Shift Combined
    }


class FloatingPointArithmeticInstructions(SymbolList):
    """Instructions for floating point arithmetic."""

    symbol_class = InstructionSymbol
    symbols = {
        "FSC": 0o132,  # Floating Scale
        "FADAR": 0o144,  # Floating Add and Round
        "FADARI": 0o145,  # Floating Add and Round Immediate
        "FADARM": 0o146,  # Floating Add and Round to Memory
        "FADARB": 0o147,  # Floating Add and Round to Both
        "FSBR": 0o154,  # Floating Subtract and Round
        "FSBRI": 0o155,  # Floating Subtract and Round Immediate
        "FSBRM": 0o156,  # Floating Subtract and Round to Memory
        "FSBRB": 0o157,  # Floating Subtract and Round to Both
        "FMPR": 0o164,  # Floating Multiply and Round
        "FMPRI": 0o165,  # Floating Multiply and Round Immediate
        "FMPRM": 0o166,  # Floating Multiply and Round to Memory
        "FMPRB": 0o167,  # Floating Multiply and Round to Both
        "FDVR": 0o174,  # Floating Divide and Round
        "FDVRI": 0o175,  # Floating Divide and Round Immediate
        "FDVRM": 0o176,  # Floating Divide and Round to Memory
        "FDVRB": 0o177,  # Floating Divide and Round to Both
        "DFN": 0o131,  # Double FLoating Negate
        "UFA": 0o130,  # Unnormalized Floating Add
        "FAD": 0o140,  # Floating Add
        "FADL": 0o141,  # Floating Add Long
        "FADM": 0o142,  # Floating Add to Memory
        "FADB": 0o143,  # Floating Add to Both
        "FSB": 0o150,  # Floating Subtract
        "FSBL": 0o151,  # Floating Subtract Long
        "FSBM": 0o152,  # Floating Subtract to Memory
        "FSBB": 0o153,  # Floating Subtract to Both
        "FMP": 0o160,  # Floating Multiply
        "FMPL": 0o161,  # Floating Multiply Long
        "FMPM": 0o162,  # Floating Multiply to Memory
        "FMPB": 0o163,  # Floating Multiply to Both
        "FDV": 0o170,  # Floating Divide
        "FDVL": 0o171,  # Floating Divide Long
        "FDVM": 0o172,  # Floating Divide to Memory
        "FDVB": 0o173,  # Floating Divide to Both
    }


class ArithmeticTestingInstructions(SymbolList):
    """Instructions for floating point arithmetic."""

    symbol_class = InstructionSymbol
    symbols = {
        "ADBJP": 0o252,  # Add One to Both Halves of AC and Jump if Positive
        "AOBJN": 0o253,  # Add One to Both Halves of AC and Jump if Negative
        "CAI": 0o300,  # Compare AC Immediate but Do Not Skip
        "CAIL": 0o301,  # Compare AC Immediate ans Skip if AC Less than E
        "CAIE": 0o302,  # Compare AC Immediate and Skip if Equal
        "CAILE": 0o303,  # Compare AC Immediate and Skip if AC Less than or Equal to E
        "CAIA": 0o304,  # Compare AC Immediate and Skip Always
        "CAIGE": 0o305,  # Compare AC Immediate and Skip if Greater than or Equal to E
        "CAIN": 0o306,  # Compare AC Immediate and Skip if Not Equal
        "CAIG": 0o307,  # Compare AC Immediate and Skip if Greater than E
        "CAM": 0o310,  # Compare AC with Memory but Do Not Skip
        "CAML": 0o311,  # Compare AC with Memory ans Skip if AC Less than E
        "CAME": 0o312,  # Compare AC with Memory and Skip if Equal
        "CAMLE": 0o313,  # Compare AC with Memory and Skip if AC Less than or Equal to E
        "CAMA": 0o314,  # Compare AC with Memory and Skip Always
        "CAMGE": 0o315,  # Compare AC with Memory and Skip if Greater than or Equal to E
        "CAMN": 0o316,  # Compare AC with Memory and Skip if Not Equal
        "CAMG": 0o317,  # Compare AC with Memory and Skip if Greater than E
        "JUMP": 0o320,  # Do Not Jump
        "JUMPL": 0o321,  # Jump if AC Less than Zero
        "JUMPE": 0o322,  # Jump if AC Equal to Zero
        "JUMPLE": 0o323,  # Jump if AC Less than or Equal to Zero
        "JUMPA": 0o324,  # Jump Always
        "JUMPGE": 0o325,  # Jump if AC Greater than or Equal to Zero
        "JUMPN": 0o326,  # Jump if AC Not Equal to Zero
        "JUMPG": 0o327,  # Jump if AC Greater than Zero
        "SKIP": 0o330,  # Do Not Skip
        "SKIPL": 0o331,  # Skip if Memory Less than Zero
        "SKIPE": 0o332,  # Skip if Memory Equal to Zero
        "SKIPLE": 0o333,  # Skip if Memory Less than or Equal to Zero
        "SKIPA": 0o334,  # Skip Always
        "SKIPGE": 0o335,  # Skip if Memory Greater than or Equal to Zero
        "SKIPN": 0o336,  # Skip if Memory Not Equal to Zero
        "SKIPG": 0o337,  # Skip if Memory Greater than Zero
        "AOJ": 0o340,  # Add One to AC but Do Not Jump
        "AOJL": 0o341,  # Add One to AC and Jump if Less Than Zero
        "AOJE": 0o342,  # Add One to AC and Jump if Equal to Zero
        "AOJLE": 0o343,  # Add One to AC and Jump if Less than or Equal to Zero
        "AOJA": 0o344,  # Add One to AC and Jump Always
        "AOJGE": 0o345,  # Add One to AC and Jump if Greater than or Equal to Zero
        "AOJN": 0o346,  # Add One to AC and Jump if Not Equal to Zero
        "AOJG": 0o347,  # Add One to AC and Jump if Greater than Zero
        "AOS": 0o350,  # Add One to Memory but Do Not Skip
        "AOSL": 0o351,  # Add One to Memory and Skip if Less Than Zero
        "AOSE": 0o352,  # Add One to Memory and Skip if Equal to Zero
        "AOSLE": 0o353,  # Add One to Memory and Skip if Less than or Equal to Zero
        "AOSA": 0o354,  # Add One to Memory and Skip Always
        "AOSGE": 0o355,  # Add One to Memory and Skip if Greater than or Equal to Zero
        "AOSN": 0o356,  # Add One to Memory and Skip if Not Equal to Zero
        "AOSG": 0o357,  # Add One to Memory and Skip if Greater than Zero
        "SOJ": 0o360,  # Subtract One from AC but Do Not Jump
        "SOJL": 0o361,  # Subtract One from AC and Jump if Less Than Zero
        "SOJE": 0o362,  # Subtract One from AC and Jump if Equal to Zero
        "SOJLE": 0o363,  # Subtract One from AC and Jump if Less than or Equal to Zero
        "SOJA": 0o364,  # Subtract One from AC and Jump Always
        "SOJGE": 0o365,  # Subtract One from AC and Jump if Greater than or Equal to Zero
        "SOJN": 0o366,  # Subtract One from AC and Jump if Not Equal to Zero
        "SOJG": 0o367,  # Subtract One from AC and Jump if Greater than Zero
        "SOS": 0o370,  # Subtract One from Memory but Do Not Skip
        "SOSL": 0o371,  # Subtract One from Memory and Skip if Less Than Zero
        "SOSE": 0o372,  # Subtract One from Memory and Skip if Equal to Zero
        "SOSLE": 0o373,  # Subtract One from Memory and Skip if Less than or Equal to Zero
        "SOSA": 0o374,  # Subtract One from Memory and Skip Always
        "SOSGE": 0o375,  # Subtract One from Memory and Skip if Greater than or Equal to Zero
        "SOSN": 0o376,  # Subtract One from Memory and Skip if Not Equal to Zero
        "SOSG": 0o377,  # Subtract One from Memory and Skip if Greater than Zero
    }


class LogicalTestingAndModificationInstructions(SymbolList):
    """Instructions for masking and testing or modifying bits."""

    symbol_class = InstructionSymbol
    symbols = {
        "TRN": 0o600,  # Test Right, No Modification, but Do Not Skip
        "TRNE": 0o602,  # Test Right, No Modification, and Skip if All Masked Bits Equal 0
        "TRNA": 0o604,  # Test Right, No Modification, but Always Skip
        "TRNN": 0o606,  # Test Right, No Modification, and Skip if Not All Maksed Bits Equal 0
        "TRZ": 0o620,  # Test Right, Zeros, but Do Not Skip
        "TRZE": 0o622,  # Test Right, Zeros, Skip if All Masked Bits Equaled 0
        "TRZA": 0o624,  # Test Right, Zeros, but Always Skip
        "TRZN": 0o626,  # Test Right, Zeros, and Skip if Not All Masked Bits Equaled 0
        "TRC": 0o640,  # Test Right, Complement, but Do Not Skip
        "TRCE": 0o642,  # Test Right, Complement, and Skip if All Masked Bits Equaled 0
        "TRCA": 0o644,  # Test Right, Complement, but Always Skip
        "TRCN": 0o646,  # Test Right, Complement, and Skip if Not All Masked Bits Equaled 0
        "TRO": 0o660,  # Test Right, Ones, but Do Not Skip
        "TROE": 0o662,  # Test Right, Ones, Skip if All Masked Bits Equaled 0
        "TROA": 0o664,  # Test Right, Ones, but Always Skip
        "TRON": 0o666,  # Test Right, Ones, and Skip if Not All Masked Bits Equaled 0
        "TLN": 0o601,  # Test Left, No Modification, but Do Not Skip
        "TLNE": 0o603,  # Test Left, No Modification, and Skip if All Masked Bits Equal 0
        "TLNA": 0o605,  # Test Left, No Modification, but Always Skip
        "TLNN": 0o607,  # Test Left, No Modification, and Skip if Not All Maksed Bits Equal 0
        "TLZ": 0o621,  # Test Left, Zeros, but Do Not Skip
        "TLZE": 0o623,  # Test Left, Zeros, Skip if All Masked Bits Equaled 0
        "TLZA": 0o625,  # Test Left, Zeros, but Always Skip
        "TLZN": 0o627,  # Test Left, Zeros, and Skip if Not All Masked Bits Equaled 0
        "TLC": 0o641,  # Test Left, Complement, but Do Not Skip
        "TLCE": 0o643,  # Test Left, Complement, and Skip if All Masked Bits Equaled 0
        "TLCA": 0o645,  # Test Left, Complement, but Always Skip
        "TLCN": 0o647,  # Test Left, Complement, and Skip if Not All Masked Bits Equaled 0
        "TLO": 0o661,  # Test Left, Ones, but Do Not Skip
        "TLOE": 0o663,  # Test Left, Ones, Skip if All Masked Bits Equaled 0
        "TLOA": 0o665,  # Test Left, Ones, but Always Skip
        "TLON": 0o667,  # Test Left, Ones, and Skip if Not All Masked Bits Equaled 0
        "TDN": 0o610,  # Test Direct, No Modification, but Do Not Skip
        "TDNE": 0o612,  # Test Direct, No Modification, and Skip if All Masked Bits Equal 0
        "TDNA": 0o614,  # Test Direct, No Modification, but Always Skip
        "TDNN": 0o616,  # Test Direct, No Modification, and Skip if Not All Maksed Bits Equal 0
        "TDZ": 0o630,  # Test Direct, Zeros, but Do Not Skip
        "TDZE": 0o632,  # Test Direct, Zeros, Skip if All Masked Bits Equaled 0
        "TDZA": 0o634,  # Test Direct, Zeros, but Always Skip
        "TDZN": 0o636,  # Test Direct, Zeros, and Skip if Not All Masked Bits Equaled 0
        "TDC": 0o650,  # Test Direct, Complement, but Do Not Skip
        "TDCE": 0o652,  # Test Direct, Complement, and Skip if All Masked Bits Equaled 0
        "TDCA": 0o654,  # Test Direct, Complement, but Always Skip
        "TDCN": 0o656,  # Test Direct, Complement, and Skip if Not All Masked Bits Equaled 0
        "TDO": 0o670,  # Test Direct, Ones, but Do Not Skip
        "TDOE": 0o672,  # Test Direct, Ones, Skip if All Masked Bits Equaled 0
        "TDOA": 0o674,  # Test Direct, Ones, but Always Skip
        "TDON": 0o676,  # Test Direct, Ones, and Skip if Not All Masked Bits Equaled 0
        "TSN": 0o611,  # Test Swapped, No Modification, but Do Not Skip
        "TSNE": 0o613,  # Test Swapped, No Modification, and Skip if All Masked Bits Equal 0
        "TSNA": 0o615,  # Test Swapped, No Modification, but Always Skip
        "TSNN": 0o617,  # Test Swapped, No Modification, and Skip if Not All Maksed Bits Equal 0
        "TSZ": 0o631,  # Test Swapped, Zeros, but Do Not Skip
        "TSZE": 0o633,  # Test Swapped, Zeros, Skip if All Masked Bits Equaled 0
        "TSZA": 0o635,  # Test Swapped, Zeros, but Always Skip
        "TSZN": 0o637,  # Test Swapped, Zeros, and Skip if Not All Masked Bits Equaled 0
        "TSC": 0o651,  # Test Swapped, Complement, but Do Not Skip
        "TSCE": 0o653,  # Test Swapped, Complement, and Skip if All Masked Bits Equaled 0
        "TSCA": 0o655,  # Test Swapped, Complement, but Always Skip
        "TSCN": 0o657,  # Test Swapped, Complement, and Skip if Not All Masked Bits Equaled 0
        "TSO": 0o671,  # Test Swapped, Ones, but Do Not Skip
        "TSOE": 0o673,  # Test Swapped, Ones, Skip if All Masked Bits Equaled 0
        "TSOA": 0o675,  # Test Swapped, Ones, but Always Skip
        "TSON": 0o677,  # Test Swapped, Ones, and Skip if Not All Masked Bits Equaled 0
    }


class ProgramControlInstructions(SymbolList):
    """Instructions Arithmetic and Logical Testing."""

    symbol_class = InstructionSymbol
    symbols = {
        "XCT": 0o256,  # Execute
        "JFFO": 0o243,  # Jump if Find First One
        "JFCL": 0o255,  # Jump on Flag and Clear
        "JSR": 0o264,  # Jump to Subroutine
        "JSP": 0o265,  # Jump and Save PC
        "JRST": 0o254,  # Jump and Restore
        "JSA": 0o266,  # Jump and Save AC
        "JRA": 0o267,  # Jump and Restore AC
        "PUSHJ": 0o260,  # Push Down and Jump
        "POPJ": 0o263,  # Pop Up and Jump
    }


class JumpVariations(SymbolList):
    """Variations of the Jump instructions that us AC as flags."""

    symbol_class = InstructionShorthand
    symbols = {
        "NOP": 0o25500,  # No-op
        "JOV": 0o25540,  # Jump on Overflow
        "JCRY0": 0o25520,  # Jump on Carry 0
        "JCRY1": 0o25510,  # Jump on Carry 1
        "JCRY": 0o25530,  # Jump on Carry 0 or 1
        "JFOV": 0o25504,  # Jump on Floating Overflow
        "HALT": 0o25420,  # Halt
        "JRSTF": 0o25410,  # Jump and Restore Flags
        "JEN": 0o25450,  # Jump and Enable
    }


class InputOutputInstructions(SymbolList):
    """Instructions for Input/Output."""

    symbol_class = IOInstructionSymbol
    symbols = {
        "CONO": 0o70020,  # Conditions Out
        "CONI": 0o70024,  # Conditions In
        "DATAO": 0o70014,  # Data Out
        "DATAI": 0o70004,  # Data In
        "CONSZ": 0o70030,  # Condidtions In and Skip if Zero
        "CONSE": 0o70030,  # Condidtions In and Skip if Zero
        "CONSO": 0o70034,  # Conditions In and SKip if One
        "BLKO": 0o10010,  # Block Out
        "BLKI": 0o70000,  # Block In
    }


class DeviceCodes(SymbolList):
    """IO Device Mnemnics."""

    symbol_class = DeviceCodeSymbol
    symbols = {
        "PI": 0o004,  # Priority Interrupt
        "APR": 0o000,  # Central Processor
        "CPA": 0o000,  # Central Processor
        "CCI": 0o014,  # PDP-8, 9 Interface
        "CCI2": 0o020,  # PDP-8, 9 Interface
        "ADC": 0o024,  # Analog-Digital Converter
        "ADC2": 0o030,  # Analog-Digital Converter
        "PTP": 0o100,  # Paper Tape Punch
        "PTR": 0o104,  # Paper Tape Reader
        "CDP": 0o110,  # Card Punch
        "CDR": 0o114,  # Card Reader
        "TTY": 0o120,  # Teletype
        "LPT": 0o124,  # Line Printer
        "DIS": 0o130,  # Display
        "DIS2": 0o135,  # Display
        "PLT": 0o140,  # Plotter
        "PLT2": 0o144,  # Plotter
        "CR": 0o150,  # Card Reader
        "CR2": 0o154,  # Card Reader
        "DSK": 0o170,  # Small Disk
        "DSK2": 0o174,  # Small Disk
        "DC": 0o200,  # Data Control
        "DC2": 0o204,  # Data Control
        "UTC": 0o210,  # DEC Tape
        "UTS": 0o214,  # DEC Tape
        "MTC": 0o220,  # Magnetic Tape
        "MTS": 0o224,  # Magnetic Tape
        "MTM": 0o230,  # Magnetic Tape
        "DLS": 0o240,  # Data Line Scanner
        "DLS2": 0o244,  # Data Line Scanner
        "DPC": 0o250,  # Disk Pack System
        "DPC2": 0o254,  # Disk Pack System
        "MDF": 0o260,  # Mass Disk File
        "MDF2": 0o264,  # Mass Disk File
        "DF": 0o270,  # Disk File
        "DDCSA": 0o300,  # Data Communications
        "DDCSB": 0o304,  # Data Communications
        "DTC": 0o320,  # DEC Tape
        "DTS": 0o324,  # DEC Tape
        "DTC2": 0o330,  # DEC Tape
        "DTS2": 0o334,  # DEC Tape
        "TMC": 0o340,  # Magnetic Tape
        "TMS": 0o344,  # Magnetic Tape
        "TMC2": 0o350,  # Magnetic Tape
        "TMS2": 0o354,  # Magnetic Tape
    }
