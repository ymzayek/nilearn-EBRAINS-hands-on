from nilearn.datasets.utils import _fetch_files
import zipfile
from pathlib import Path

def download_data():
    # download zip file from OSF
    data_path = Path('Notebooks/data')
    url = f'https://osf.io/2mrwe/download'
    _fetch_files(
        data_path, [(
            'mcse.zip',
            url,
            {'move': 'mcse.zip'}
        )]
    )

    # extract data
    with zipfile.ZipFile(data_path / 'mcse.zip', 'r') as zip_ref:
        zip_ref.extractall(data_path)
    
    
    # delete zip file
    Path.unlink(data_path / 'mcse.zip')


def main():
    download_data()


if __name__ == "__main__":
    main()
