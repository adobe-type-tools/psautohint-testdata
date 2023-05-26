import glob
from os.path import basename
import pytest

from fontTools.misc.xmlWriter import XMLWriter
from fontTools.ttLib import TTFont
from afdko.otfautohint.autohint import ACOptions, hintFiles

from .differ import main as differ
from . import make_temp_copy, DATA_DIR


class MMOptions(ACOptions):
    def __init__(self, reference, inpaths, outpaths, ref_out=None):
        super(MMOptions, self).__init__()
        self.inputPaths = inpaths
        self.outputPaths = outpaths
        self.referenceFont = reference
        self.referenceOutputPath = ref_out
        self.hintAll = True
        self.verbose = False


@pytest.mark.parametrize("base", glob.glob("%s/*/Masters" % DATA_DIR))
def test_mmufo(base, tmpdir):
    paths = sorted(glob.glob(base + "/*.ufo"))
    # the reference font is modified in-place, make a temp copy first
    reference = paths[0]
    inpaths = paths[1:]
    ref_out = str(tmpdir / basename(reference)) + ".out"
    outpaths = [str(tmpdir / basename(p)) + ".out" for p in inpaths]

    options = MMOptions(reference, inpaths, outpaths, ref_out)
    hintFiles(options)

    for inpath, outpath in zip(inpaths, outpaths):
        assert differ([inpath, outpath])


@pytest.mark.parametrize("base", glob.glob("%s/*/OTFMasters" % DATA_DIR))
def test_mmotf(base, tmpdir):
    paths = sorted(glob.glob(base + "/*.otf"))
    # the reference font is modified in-place, make a temp copy first
    reference = paths[0]
    inpaths = paths[1:]
    ref_out = str(tmpdir / basename(reference)) + ".out"
    outpaths = [str(tmpdir / basename(p)) + ".out" for p in inpaths]

    options = MMOptions(reference, inpaths, outpaths, ref_out)
    hintFiles(options)

    refs = [p + ".ref" for p in paths]
    for ref, out in zip(refs, [ref_out] + outpaths):
        for path in (ref, out):
            font = TTFont(path)
            assert "CFF " in font
            writer = XMLWriter(str(tmpdir / basename(path)) + ".xml")
            font["CFF "].toXML(writer, font)
            writer.close()

        assert differ([str(tmpdir / basename(ref)) + ".xml",
                       str(tmpdir / basename(out)) + ".xml"])


def test_incompatible_masters(tmpdir):
    base = "%s/source-serif-pro/" % DATA_DIR
    paths = [base + "Light/font.ufo", base + "Black/font.ufo"]
    reference = paths[0]
    inpaths = paths[1:]
    ref_out = str(tmpdir / reference)
    outpaths = [str(tmpdir / p) for p in inpaths]

    options = MMOptions(reference, inpaths, outpaths, ref_out)
    hintFiles(options)
