# Molecular_Manager

Molecular_Manager is a data management system to lookup or query an environmental compound database by retention time, polarity or compound type.
Analytical data of a measured compound can be inserted into the database. Database administrator can add newly identified compound into the compound database.

## Requirements:

* Docker software Windows/macOS: https://www.docker.com/
* Docker installation for Ubuntu:
  ```
  sudo apt update
  sudo apt install docker.io
  sudo systemctl enable --now docker
  ```
* Git (latest version)
  
## Installation:

Clone the software from Github to your local directory:
```
git clone https://github.com/daniellyz/Molecular_Manager.git
```

Make sure Docker is running on your machine and type:

```
docker image build -t molecular_manager .
docker run -p 5000:5000 -d molecular_manager
```

## Usage

Please use software such as Postman to run the API interactively on your local machine.

To send a request to retrieve a list of **compounds**:
```
http://127.0.0.1:5000/compounds
```
To send a request to retrieve a list of **measured_compounds**:
```
http://127.0.0.1:5000/measured_compounds
```
To query **measured_compounds** based on *retention time*:
```
http://127.0.0.1:5000/measured_compounds/query?query_params=RT&value=18.3
```
To query **measured_compounds** based on *type*:
```
http://127.0.0.1:5000/measured_compounds/query?query_params=type&value=metabolites
```
To query **measured_compounds** without *type* specification:
```
http://127.0.0.1:5000/measured_compounds/query?query_params=type&value=Unknown
```
To query **measured_compounds** based on *polarity* (positive or negative):
```
http://127.0.0.1:5000/measured_compounds/query?query_params=polarity&value=negative
```
