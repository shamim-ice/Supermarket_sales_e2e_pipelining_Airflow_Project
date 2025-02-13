# Airflow Installation - Commands
## Linux (or WSL)
#### Update sudo apt
In Linux terminal (or after installation WSL on your Windows):

```sh
sudo apt update
sudo apt upgrade
```

#### Installation of necessary tools on terminal (or WSL)

```sh
sudo apt install python3 python3-pip python3-venv
```

### AIRFLOW_HOME setup (terminal or WSL)
On your $HOME directory type
```sh
vim ~/.bashrc
```
perss i then export your path where you want to craete your virtual environment for python and dags folder.

```sh
export AIRFLOW_HOME=/mnt/your_driver/your_folder
for example: /mnt/e/airflow_project
```
[```airflow_project``` should be in ```e``` drive.]

Now press ```esc``` button for save and then type ```:wq``` for exit from bashrc.

After this a bashrc should be reloaded with ```source ~/.bashrc ```. 
To check if the value is properly set: ```echo $AIRFLOW_HOME``` and it should print the path you provided earlier.

#### dags folder
DAGs should be created inside ```$AIRFLOW_HOME```
```sh
cd $AIRFLOW_HOME
mkdir dags
```


### Virtual Environment setup
Go to your ```$AIRFLOW_HOME``` directory from terminal or WSL and then create virtual environment for Python.
```sh
cd $AIRFLOW_HOME
python3 -m venv airflow_venv
```
Now active your virtual environment ```airflow_venv```
```sh
source airflow_venv/bin/activate
```


### Apache Airflow Installation
Make sure you are in ```$AIRFLOW_HOME``` path and ```airflow_venv``` are active then installed Apache Airflow with
```sh
pip install apache-airflow
```
####### Remember to have virtual environment activated!
#### Configure airflow.cfg
Check your dags folder is created inside using ```vim airflow.cfg```
If not find your dags_folder then open your ```airflow.cfg``` then [copy](https://github.com/shamim-ice/Airflow_project/blob/main/airfflow_configuration.txt) all and past. Finally, edit your dags_folder, sql_alchemy_conn and plugins folder based on your directory.

### Airflow Initialization and User Creation
```sh
cd $AIRFLOW_HOME
source airflow_venv/bin/activate
airflow db migrate
airflow users create -u admin -f admin -l admin -r Admin -e your_emaill@adress -p your_password
```
now type ```airflow users list``` you can see all airflow users list.
And from the same terminal we can run airflow scheduler to start main component of Apache Airflow.
```sh
airflow scheduler
```

To access graphic airflow UI we must open a new WSL terminal and repeat few steps:
```sh
cd $AIRFLOW_HOME
source airflow_env/bin/activate
airflow webserver
```
And now, you can access the graphical interface of Apache Airflow at ```localhost:8080.``` You’re ready to go!
