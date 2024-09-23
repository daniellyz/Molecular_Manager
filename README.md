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
* Git (latest version): https://git-scm.com/
* Postman (latest version): https://www.postman.com/downloads/
  
## Installation:

Clone the software from Github to your local directory:
```
git clone https://github.com/daniellyz/Molecular_Manager.git
```

Please check Docker is running on your machine (Windows):
```
docker info
```

Please build and run the docker:
```
docker image build -t molecular_manager .
docker run -p 5000:5000 -d molecular_manager
```

## Database diagram:

![alt text](https://github.com/daniellyz/MergeION2/blob/master/inst/diagram.png "Diagram")

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
http://127.0.0.1:5000/measured_compounds?RT=18
```
To query **measured_compounds** based on *type*:
```
http://127.0.0.1:5000/measured_compounds?type=metabolite
```
To query **measured_compounds** without being previously specified with *type*:
```
http://127.0.0.1:5000/measured_compounds?type=Unknown
```
To query **measured_compounds** based on *polarity* (positive or negative):
```
http://127.0.0.1:5000/measured_compounds?polarity=negative
```

## Database update:

You can add each time one **measured_compounds** with POST API call. The input data must be written in *json* format: 

The compound *3360* is present in **compounds** database, its "M+H" adduct is added in **measured_compounds**: 
```
{
     "compound_id": "3360",
     "compound_name": "Darunavir-d9",
     "retention_time": "18",
     "retention_time_comment": "",
     "adduct_name": "M+H",
     "user": "yliu",
     "password": "555",
     "molecular_formula": "C27H29[2]H9N3O7S1",
     "type": ""
}
```
The added measured compound will be printed:
```
{
        "Added measured compound": 1,
        "Adduct ID": 1,
        "Compound ID": 3360,
        "Ion formula": "C27H29[2H]9N3O7S",
        "Ion mass": 557.299,
        "Measured Compound ID": 1605,
        "Retention Time ID": "C3360:RT18.0"
}
```

The "M+FA-H" adduct is added for compound *3401*: 

```
{
      "compound_id": "3401",
      "compound_name": "Losartan-D4",
      "retention_time": "18.3",
      "retention_time_comment": "",
      "adduct_name": "M+FA-H",
      "user": "yliu",
      "password": "555",
      "molecular_formula": "C22H18[2]H4N6O1Cl1",
      "type": ""
}
```

The "M+FA-H" adduct detected at another retention time is added for compound *3401*: 

```
{
      "compound_id": "3401",
      "compound_name": "Losartan-D4",
      "retention_time": "21.3",
      "retention_time_comment": "Isomer detected, different RT",
      "adduct_name": "M+FA-H",
      "user": "yliu",
      "password": "555",
      "molecular_formula": "",
      "type": ""
}
```
When adding a compound (here *3401*) that is already measured with the same retention and same adduct:
```
{
      "compound_id": "3401",
      "compound_name": "Losartan-D4",
      "retention_time": "18.3",
      "retention_time_comment": "",
      "adduct_name": "M-H",
      "user": "yliu",
      "password": "555",
      "molecular_formula": "",
      "type": ""
}
```
No update will be made for **measured_compounds** and you will see following message:
```
{
    "Achtung": "Measured compound already exists with id: 1604"
}
```
When database administrator (with correct user name and password) confirms a new structure, she/he can assign it a new compound id (here "50000") if molecular formula and type of the comopound are provided:
```
{
     "compound_id": "50000",
     "compound_name": "NADPH",
     "retention_time": "15",
     "retention_time_comment": "bad peak shape",
     "adduct_name": "M+H",
     "user": "Admin",
     "password": "1111",
     "molecular_formula": "C21H30N7O17P3 ",
     "type": "metabolites"
}
```
Both **compounds** and **measured_compounds** will be updated:

>
> ```
>    [
>        {
>            "Added measured compound": 1,
>            "Adduct ID": 1,
>            "Compound ID": 50000,
>            "Ion formula": "C21H31N7O17P3",
>            "Ion mass": 746.0984,
>            "Measured Compound ID": 1608,
>            "Retention Time ID": "C50000:RT15.0"
>        }
>    ],
>    [
>        {
>            "Added compound": 1,
>            "Compound ID": 50000,
>            "Compound name": "NADPH",
>            "Neutral formula": "C21H30N7O17P3 ",
>            "Neutral mass": 745.0911,
>            "Type": "metabolites"
>        }
>    ]
>```

Afterwards, any user can add extra analytical data of "50000" in the **measured_compounds**:
```
{
      "compound_id": "50000",
      "compound_name": "NADPH",
      "retention_time": "16",
      "retention_time_comment": "Isomer detected, different RT",
      "adduct_name": "M+Na",
      "user": "yliu",
      "password": "555",
      "molecular_formula": "",
      "type": "metabolites"
}
```

The added data record will be displayed as a *json* file with computed **ion formula** and **ion mass**:

```
{
        "Added measured compound": 1,
        "Adduct ID": 2,
        "Compound ID": 50000,
        "Ion formula": "C21H30N7NaO17P3",
        "Ion mass": 768.0803,
        "Measured Compound ID": 1609,
        "Retention Time ID": "C50000:RT16.0"
}
```

You can delete all added data records (**compounds** and **measured_compounds**) by:
```
http://127.0.0.1:5000/measured_compounds/delete
```

## Stop the software:

You will be able to see currently running docker containers using below command.

```
docker ps
```

Then copy the CONTAINER ID of the running container and execute the following command

```
docker stop <container_id>
```

