# Molecular_Manager

Molecular_Manager is a data management system to lookup or query an environmental compound database by retention time, polarity or compound type. The database contains **compounds**: a database of identified compounds, and **measured_compounds**: their analytical data. Analytical data of an identified compound can be inserted into **measured_compounds** by all users. Only database administrator can add a structure-confirmed compound into **compounds**.

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

## Database lookup and query:

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

## Usage: database lookup and query:

## Stop the software:

You will be able to see currently running docker containers using below command.

```
docker ps
```

Then copy the CONTAINER ID of the running container and execute the following command

```
docker stop <container_id>
```

