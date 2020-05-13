# Instructions

First, attach the `model` folder to the Azure Machine Learning workspace:

```
cd model/
az ml folder attach -g aml-demo -w aml-demo
```

### Train on local Docker container, but log metrics to Azure Machine Learning

In [`aml_config/train-local.runconfig`](aml_config/train-local.runconfig), update the following section to point to a folder with the training data:

```yaml
docker:
  enabled: true
  baseImage: mcr.microsoft.com/azureml/base:intelmpi2018.3-ubuntu16.04
  arguments: [-v, C:\Users\clsieble\dev\unet-pytorch-azureml\data\kaggle_3m_small:/data] # Update to point to your data folder
```

Then you can kick off a local training run:

```
az ml run submit-script -c train-local -e unet-train-local
```

This will load the `runconfig` from [`aml_config/train-local.runconfig`](aml_config/train-local.runconfig) and log the run's details to an experiment named `unet-train-local`.

### Train using Azure Machine Learning on a Compute Cluster

In [`aml_config/train-amlcompute.runconfig`](aml_config/train-amlcompute.runconfig), update the following section to point to your training dataset:

```yaml
data:
  training_data:
    dataLocation:
      dataset:
        id: c7e23b60-04c8-46dc-96c5-d9f741f6234b # Point to your training dataset's id
    mechanism: mount
    pathOnCompute: /data
    environmentVariableName: training_data
    createOutputDirectories: false
    overwrite: false
```

You can figure out the dataset's id via:
```
az ml dataset list
```

Then you can kick off a remote training run on AML Compute:

```
az ml run submit-script -c config/training-amlcompute -e unet-train-amlcompute
```

This will load the `runconfig` from [`aml_config/train-amlcompute.runconfig`](aml_config/train-amlcompute.runconfig) and log the run's details to an experiment named `unet-train-amlcompute`.
