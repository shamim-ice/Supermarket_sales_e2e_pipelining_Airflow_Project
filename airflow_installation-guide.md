# Airflow Installation - Commands
## Linux (or WSL)
#### Update sudo apt
In the home directory of Linux terminal (or after installation WSL on your Windows)

```sh
sudo apt update
sudo apt upgrade
```

#### Installation of necessary tools on terminal (or WSL)

```sh
sudo apt install python3 python3-pip python3-venv
```
#### Python virtual environment creation 
```sh
python3 -m venv airflow_venv
```

### AIRFLOW_HOME setup (terminal or WSL)
Make a directory where you want to save your project. 
```sh
cd
mkdir airflow_project
```
Create #### $AIRFLOW_HOME to avoid dependency.
```sh
vim ~/.bashrc
```
perss i then export your airflow_project folder path.

```sh
export AIRFLOW_HOME=/mnt/your_driver/your_folder
for example: /mnt/e/airflow_project
```
[```airflow_project``` should be in ```e``` drive.]

Now press ```esc``` button for save and then type ```:wq``` for exit from bashrc.

After this a bashrc should be reloaded with ```source ~/.bashrc ```. 
To check if the value is properly set: ```echo $AIRFLOW_HOME``` and it should print the path you provided earlier.



### Apache Airflow Installation
Make sure ```airflow_venv``` are active and you are in ```$AIRFLOW_HOME``` path and  then install Apache Airflow with
```sh
cd
source airflow_venv/bin/activate
cd $AIRFLOW_HOME
pip install apache-airflow
```
now check ```airflow version``` 


#### Initilize airflow.db
```sh
airflow db migrate
```
#### Create dags folder
```sh
mkdir dags
```

Check your dags folder is created inside using ```vim airflow.cfg```

### Airflow Initialization and User Creation
```sh
airflow users create -u admin -f admin -l admin -r Admin -e your_emaill@adress -p your_password
```
now type ```airflow users list``` you can see all airflow users list.
And from the same terminal we can run airflow scheduler to start main component of Apache Airflow.
```sh
airflow scheduler
```

To access graphic airflow UI we must open a new WSL terminal and repeat few steps:
```sh
cd
source airflow_env/bin/activate
cd $AIRFLOW_HOME
airflow webserver
```
And now, you can access the graphical interface of Apache Airflow at ```localhost:8080.``` You’re ready to go!
