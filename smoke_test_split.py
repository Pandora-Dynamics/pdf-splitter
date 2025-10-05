import os
from pypdf import PdfWriter
from pdfsplitter.core.models import SplitJobParams, SplitStrategy
from pdfsplitter.core.splitter import split_pdf


def make_pdf(path: str, pages: int = 5):
    w = PdfWriter()
    for _ in range(pages):
        w.add_blank_page(width=612, height=792)
    with open(path, 'wb') as f:
        w.write(f)


def main():
    os.makedirs('/workspace/tmp_out', exist_ok=True)
    input_pdf = '/workspace/tmp_in.pdf'
    make_pdf(input_pdf, 7)

    params = SplitJobParams(
        input_path=input_pdf,
        output_dir='/workspace/tmp_out',
        strategy=SplitStrategy.RANGES,
        ranges_text='1-3,5,7-'
    )
    res = split_pdf(params)
    print('RANGES:', len(res.output_files), 'files')

    params2 = SplitJobParams(
        input_path=input_pdf,
        output_dir='/workspace/tmp_out',
        strategy=SplitStrategy.EVERY_N_PAGES,
        pages_per_file=2,
        output_prefix='chunk'
    )
    res2 = split_pdf(params2)
    print('EVERY_N:', len(res2.output_files), 'files')

    params3 = SplitJobParams(
        input_path=input_pdf,
        output_dir='/workspace/tmp_out',
        strategy=SplitStrategy.EACH_PAGE,
        output_prefix='page'
    )
    res3 = split_pdf(params3)
    print('EACH_PAGE:', len(res3.output_files), 'files')

    print('OK')


if __name__ == '__main__':
    main()
