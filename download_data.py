from nilearn.datasets.utils import _fetch_files
import zipfile


def download_data():
    # Example file
    # TODO: change to actual file when uploaded to OSF
    url = f'https://osf.io/nxwsq/download'
    _fetch_files(
        'Notebooks/data', [(
            f'sub-01.zip',
            url,
            {'move': f'sub-01.zip'}
        )]
    )

    with zipfile.ZipFile('Notebooks/data/sub-01.zip', 'r') as zip_ref:
        zip_ref.extractall('Notebooks/data')


def main():
    download_data()


if __name__ == "__main__":
    main()
