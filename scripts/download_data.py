from nilearn.datasets.utils import _fetch_files
import zipfile
from pathlib import Path
import glob

def download_data():
    # download zip file from OSF
    repo_path = str(Path(__file__).parent.parent)
    data_exists = glob.glob(repo_path + "/**/*3mm", recursive=True)
    if data_exists:
        return print(f"Data is already downloaded; check path {data_exists}")

    data_path = Path(repo_path + '/Notebooks/data')
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


if __name__ == "__main__":
    download_data()
