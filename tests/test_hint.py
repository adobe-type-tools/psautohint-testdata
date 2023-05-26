import glob
from os.path import basename
import pytest
import logging
import subprocess

from fontTools.misc.xmlWriter import XMLWriter
from fontTools.cffLib import CFFFontSet
from fontTools.ttLib import TTFont
from afdko.otfautohint import FontParseError
from afdko.otfautohint.autohint import ACOptions, hintFiles

from .differ import main as differ 
from . import DATA_DIR

parametrize = pytest.mark.parametrize


class OTFOptions(ACOptions):
    def __init__(self, inpath, outpath, logOnly=False):
        super(OTFOptions, self).__init__()
        self.inputPaths = [inpath]
        self.outputPaths = [outpath]
        self.logOnly = logOnly
        self.hintAll = True
        self.verbose = False


class MMOptions(ACOptions):
    def __init__(self, reference, inpaths, outpaths, ref_out=None):
        super(MMOptions, self).__init__()
        self.inputPaths = inpaths
        self.outputPaths = outpaths
        self.referenceFont = reference
        self.referenceOutputPath = ref_out
        self.hintAll = True
        self.verbose = False


@parametrize("ufo", glob.glob("%s/*/*/font.ufo" % DATA_DIR))
def test_ufo(ufo, tmpdir):
    out = str(tmpdir / basename(ufo))
    options = OTFOptions(ufo, out)
    hintFiles(options)

    assert differ([ufo, out])


@parametrize("otf", glob.glob("%s/*/*/font.otf" % DATA_DIR))
def test_otf(otf, tmpdir):
    out = str(tmpdir / basename(otf)) + ".out"
    options = OTFOptions(otf, out)
    hintFiles(options)

    for path in (otf, out):
        font = TTFont(path)
        assert "CFF " in font
        writer = XMLWriter(str(tmpdir / basename(path)) + ".xml")
        font["CFF "].toXML(writer, font)
        writer.close()

    assert differ([str(tmpdir / basename(otf)) + ".xml",
                   str(tmpdir / basename(out)) + ".xml"])


@parametrize("otf", glob.glob("%s/libertinus-*/*/font.otf" % DATA_DIR))
def test_flex_otf(otf, tmpdir):
    out = str(tmpdir / basename(otf)) + ".out"
    options = OTFOptions(otf, out)
    options.noFlex = False

    hintFiles(options)

    for path in (otf, out):
        font = TTFont(path)
        assert "CFF " in font
        writer = XMLWriter(str(tmpdir / basename(path)) + ".xml")
        font["CFF "].toXML(writer, font)
        writer.close()

    assert differ([str(tmpdir / basename(otf)) + ".xml",
                   str(tmpdir / basename(out)) + ".xml"])


@parametrize("ufo", glob.glob("%s/libertinus-*/*/font.ufo" % DATA_DIR))
def test_flex_ufo(ufo, tmpdir):
    out = str(tmpdir / basename(ufo)) + ".out"
    options = OTFOptions(ufo, out)
    options.noFlex = False

    hintFiles(options)

    assert differ([ufo, out])
