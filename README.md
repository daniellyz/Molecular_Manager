# Molecular_Manager

Molecular_Manager is a data management system to lookup or query an environmental compound database.


## Requirements:
* Docker software:
  Windows/macOS: https://www.docker.com/
  Ubuntu:
  ```
  sudo apt update
  sudo apt install docker.io
  sudo systemctl enable --now docker
  ```
* Git
  
## Installation:

Clone the software to
```
git clone https://github.com/daniellyz/Molecular_Manager.git
docker image build -t molecular_manager .
docker run -p 5000:5000 -d molecular_manager
```

## Usage

http://127.0.0.1:5000/compounds

http://127.0.0.1:5000/measured_compounds/query?query_params=RT&value=18.3
