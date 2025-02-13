# Airflow Installation - Commands
### Linux
#### Update sudo apt
In Linux terminal (or after installation WSL on your Windows):

```sh
sudo apt update
sudo apt upgrade
```

### Installation of necessary tools on terminal (or WSL):

```sh
sudo apt install python3 python3-pip python3-venv
```

## AIRFLOW_HOME setup (terminal or WSL)
On your $HOME directory type
```sh
vim ~/.bashrc
```
perss i then export your path where you want to craete your virtual environment for python and dags folder.

```sh
export AIRFLOW_HOME=/mnt/your_driver/your_folder
```


After this a bashrc should be reloaded with ```source ~/.bashrc ```. 
To check if the value is properly set: ```echo $AIRFLOW_HOME``` and it should print the path you provided earlier.
