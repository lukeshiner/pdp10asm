"""pdp10asm command line interface."""

import click

from pdp10asm import BinaryListing, PDP10Assembler, RimOutput, SourceListing, exceptions

RIM_FORMAT = "RIM"

OUTPUT_FORMATS = {RIM_FORMAT: RimOutput}

BINARY_LISTING = "BINARY"
SOURCE_LISTING = "SOURCE"

LISTING_FORMATS = {BINARY_LISTING: BinaryListing, SOURCE_LISTING: SourceListing}

BINARY = "BIN"
OCTAL = "OCT"
DECIMAL = "DEC"
HEXADECIMAL = "HEX"

RADICIES = {BINARY: 2, OCTAL: 8, DECIMAL: 10, HEXADECIMAL: 16}

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option()
@click.argument("source", type=click.File())
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True, allow_dash=True),
    help="Path where the output will be saved, if not given out ouptput will be saved.",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice([RIM_FORMAT], case_sensitive=False),
    default=RIM_FORMAT,
    show_default=True,
    help=(
        "The format in which the assembled program will be output. "
        f"{RIM_FORMAT}: PDP-6 RIM loader format."
    ),
)
@click.option(
    "--loader/--no-loader",
    default=True,
    show_default=True,
    help="Include a RIM loader in the output.",
)
@click.option(
    "--halt/--jump",
    "halt",
    default=True,
    show_default=True,
    help=(
        "When outputing a RIM loader binary halt will cause it to terminate "
        "with a HALT instruction, jump will cause it to terminate with a JRST "
        "instruction and begin execution."
    ),
)
@click.option(
    "-nl",
    "--no-listing",
    "no_listing",
    is_flag=True,
    default=False,
    show_default=True,
    help="Disable listing processing.",
)
@click.option(
    "-l",
    "--listing",
    "listing_path",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True, allow_dash=True),
    help="Path where the output will be saved, if not given out ouptput will be saved.",
)
@click.option(
    "-p",
    "--paged",
    is_flag=True,
    default=False,
    show_default=True,
    help="Show the program listing via pager.",
)
@click.option(
    "-lf",
    "--listing-format",
    type=click.Choice([BINARY_LISTING, SOURCE_LISTING], case_sensitive=False),
    default=BINARY_LISTING,
    show_default=True,
    help=(
        f"The format of the program listing. {BINARY_LISTING}: "
        "Basic listing with symbols, instructions, memory locations and binary values."
        f"{SOURCE_LISTING}: Listing containing the full source code."
    ),
)
@click.option(
    "-r",
    "--radix",
    "listing_radix",
    type=click.Choice([BINARY, OCTAL, DECIMAL, HEXADECIMAL], case_sensitive=False),
    default=OCTAL,
    show_default=True,
    help="The output format for binary values in the program listing.",
)
def cli(
    source,
    output_path,
    format,
    loader,
    halt,
    no_listing,
    listing_path,
    paged,
    listing_format,
    listing_radix,
):
    """DEC PDP-10 Assembler."""
    click.echo(f"Assembling {click.format_filename(source.name)}.\n")
    output_class = OUTPUT_FORMATS[format]
    program = _assemble_program(source)
    click.secho("Assembly successful\n", fg="green")
    if no_listing is False:
        _handle_listing(
            program=program,
            listing_format=listing_format,
            listing_radix=listing_radix,
            paged=paged,
            listing_path=listing_path,
        )
    if output_path is not None:
        output = output_class(program)
        output.write_file(output_path, loader=loader, halt=halt)
        click.secho(f"Saved binary to {click.format_filename(output_path)}", fg="green")


def _assemble_program(source):
    try:
        assembler = PDP10Assembler(source.read())
        program = assembler.assemble()
    except exceptions.AssemblyError as e:
        raise click.ClickException("\n".join(e.__notes__)) from e
    else:
        return program


def _get_listing_text(program, listing_format, listing_radix):
    try:
        listing_class = LISTING_FORMATS[listing_format]
        return program.listing_text(
            listing_class=listing_class, radix=RADICIES[listing_radix]
        )
    except exceptions.ListingError as e:
        raise click.ClickException(str(e)) from e


def _handle_listing(program, listing_format, listing_radix, paged, listing_path):
    listing_text = _get_listing_text(
        program=program, listing_format=listing_format, listing_radix=listing_radix
    )
    if paged is True:
        click.echo_via_pager(listing_text)
    else:
        click.echo(listing_text)
    if listing_path:
        _write_listing(listing_text=listing_text, listing_path=listing_path)


def _write_listing(listing_text, listing_path):
    with open(listing_path, "w") as f:
        f.write(listing_text)
    click.secho(f"Saved listing to {click.format_filename(listing_path)}", fg="green")
