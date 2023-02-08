from nilearn.datasets.utils import _fetch_files
import zipfile
from pathlib import Path

def download_data():
    # download zip file from OSF
    data_path = Path('data')
    osfID = '2mrwe'
    filename = 'mcse.zip'
    url = f'https://osf.io/{osfID}/download'
    _fetch_files(
        data_path, [(
            filename,
            url,
            {'move': filename}
        )]
    )

    # extract data
    with zipfile.ZipFile(data_path / filename, 'r') as zip_ref:
        zip_ref.extractall(data_path)
    
    
    # delete zip file
    Path.unlink(data_path / filename)


def main():
    download_data()


if __name__ == "__main__":
    main()
