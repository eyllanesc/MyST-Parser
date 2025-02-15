"""Test fixture files, using the ``DocutilsRenderer``.

Note, the output AST is before any transforms are applied.
"""
import shlex
from io import StringIO
from pathlib import Path

import pytest
from docutils.core import Publisher, publish_doctree

from myst_parser.docutils_ import Parser
from myst_parser.docutils_renderer import DocutilsRenderer, make_document
from myst_parser.main import MdParserConfig, create_md_parser

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "docutil_syntax_elements.md")
def test_syntax_elements(file_params):
    parser = create_md_parser(
        MdParserConfig(highlight_code_blocks=False), DocutilsRenderer
    )
    parser.options["document"] = document = make_document()
    parser.render(file_params.content)
    # in docutils 0.18 footnote ids have changed
    outcome = document.pformat().replace('"footnote-reference-1"', '"id1"')
    file_params.assert_expected(outcome, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "docutil_roles.md")
def test_docutils_roles(file_params):
    """Test output of docutils roles."""
    parser = create_md_parser(MdParserConfig(), DocutilsRenderer)
    parser.options["document"] = document = make_document()
    parser.render(file_params.content)
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "docutil_directives.md")
def test_docutils_directives(file_params):
    """Test output of docutils directives."""
    if "SKIP" in file_params.description:  # line-block directive not yet supported
        pytest.skip(file_params.description)
    parser = create_md_parser(MdParserConfig(), DocutilsRenderer)
    parser.options["document"] = document = make_document()
    parser.render(file_params.content)
    file_params.assert_expected(document.pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "docutil_syntax_extensions.txt")
def test_syntax_extensions(file_params):
    """The description is parsed as a docutils commandline"""
    pub = Publisher(parser=Parser())
    option_parser = pub.setup_option_parser()
    try:
        settings = option_parser.parse_args(
            shlex.split(file_params.description)
        ).__dict__
    except Exception as err:
        raise AssertionError(
            f"Failed to parse commandline: {file_params.description}\n{err}"
        )
    report_stream = StringIO()
    settings["warning_stream"] = report_stream
    doctree = publish_doctree(
        file_params.content,
        parser=Parser(),
        settings_overrides=settings,
    )
    file_params.assert_expected(doctree.pformat(), rstrip_lines=True)
