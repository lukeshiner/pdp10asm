from pathlib import Path

import pytest


@pytest.fixture
def hello_world_text():
    with open(Path(__file__).parent / "asm" / "hello_world.asm") as f:
        text = f.read()
    return text


@pytest.fixture()
def hello_world_listing_text():
    with open(Path(__file__).parent / "listings" / "hello_world.txt") as f:
        text = f.read()
    return text


@pytest.fixture()
def hello_world_source_listing_text():
    with open(Path(__file__).parent / "listings" / "hello_world_src.txt") as f:
        text = f.read()
    return text


@pytest.fixture()
def hello_world_rim_data():
    with open(Path(__file__).parent / "rim" / "hello_world.rim", "rb") as f:
        text = f.read()
    return text


@pytest.fixture
def memory_to_paper_tape_raw_text():
    with open(
        Path(__file__).parent / "asm" / "memory_block_to_paper_tape_raw.asm"
    ) as f:
        text = f.read()
    return text


@pytest.fixture
def memory_to_paper_tape_raw_listing_text():
    with open(
        Path(__file__).parent / "listings" / "memory_block_to_paper_tape_raw.txt"
    ) as f:
        text = f.read()
    return text


@pytest.fixture
def memory_to_paper_tape_raw_source_listing_text():
    with open(
        Path(__file__).parent / "listings" / "memory_block_to_paper_tape_raw_src.txt"
    ) as f:
        text = f.read()
    return text


@pytest.fixture
def memory_to_paper_tape_raw_rim_data():
    with open(
        Path(__file__).parent / "rim" / "memory_block_to_paper_tape_raw.rim", "rb"
    ) as f:
        text = f.read()
    return text


class Instruction:
    def __init__(self, word):
        self.word = word
        word_list = "{:036b}".format(word)
        self.instruction = self.int_to_oct(self.list_to_int(word_list[:9]), 3)
        self.accumulator = self.int_to_oct(self.list_to_int(word_list[9:13]), 2)
        self.indirect = word_list[13] == "1"
        self.index_register = self.int_to_oct(self.list_to_int(word_list[14:18]), 2)
        self.address = self.int_to_oct(self.list_to_int(word_list[18:]), 6)

    def list_to_int(self, bit_list):
        return int("".join(bit_list), 2)

    def int_to_oct(self, n, digits):
        return f"{{:0{digits}o}}".format(n)


@pytest.fixture
def parse_instruction():
    def _parse_instruction(word):
        return Instruction(word)

    return _parse_instruction
