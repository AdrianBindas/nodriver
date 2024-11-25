# Infrastructure Deployment Guide for AWS EC2 with Docker

This guide provides a step-by-step process how to replicate deployment infrastructure on Amazon Web Services (AWS) using Docker.

## Prerequisites

* Create an Amazon Web Services (AWS) account
* Set up an S3 bucket in your AWS account (`{bucket_name}`)
* Launch an EC2 instance with Amazon Linux, configure an IAM role that grants full access to your S3 bucket (`{iam_role_name}`), and obtain a `.pem` file for SSH access to the EC2 instance (`{ec2_instance_private_ip}`)

## Step by step guide

If you have a basic prerequisites setup, then following variables should be known to you.

**Variables Legend**

* `{bucket_name}`: the name of the S3 bucket
* `{iam_role_name}`: the name of the IAM role
* `{ec2_instance_public_dns}`: the public DNS name of the EC2 instance
* `{social_nodriver_pem_file}`: the path to the `.pem` file for SSH access to the EC2 instance

### Step 1: Launch an Amazon Linux AMI and Create a Pem Secret File

Launch an Amazon Linux AMI on your EC2 instance (`{ec2_instance_public_dns}`) and create a pem secret file. Then, login via terminal to the VM using the following command:

```sh
ssh -i "{social_nodriver_pem_file}" ec2-user@{ec2_instance_private_ip}
```

### Step 2: Update the Package List

Update the package list on your EC2 instance:

```sh
sudo yum update -y
```

### Step 3: Install Docker

Install Docker on your EC2 instance:

```sh
sudo yum install -y docker
```

### Step 4: Start the Docker Service

Start the Docker service on your EC2 instance:

```sh
sudo service docker start
```

### Step 5: Add Your User to the Docker Group

Add your user to the `docker` group to avoid needing `sudo` every time you use Docker:

```sh
sudo usermod -aG docker ec2-user
```
Note: You need to log out and log back in for this change to take effect, or you can use `newgrp docker` to apply it in the current session.

### Step 6: Enable Docker to Start on Boot

Enable Docker to start when the EC2 instance reboots:

```sh
sudo systemctl enable docker
```

### Step 7: Verify Docker Installation

Verify that Docker is installed and running properly:

```sh
docker --version
```

### Step 8: Create a Copy of the Docker Image

Create a copy of the `social-nodriver` Docker image:

```sh
docker save -o social-nodriver.tar social-nodriver
```

### Step 9: Copy the Image to the Machine

Copy the image to your EC2 instance using SCP:

```sh
scp -i "{social_nodriver_pem_file}" "social-nodriver.tar" ec2-user@{ec2_instance_private_ip}:~/investigation/
```

Note: You need to restrict rights to your `.pem` file to single user locally, otherwise you will have an issue during copying with SCP.

### Step 10: Unpack the Image on EC2 Instance

Unpack the image on your EC2 instance:

```sh
docker load -i social-nodriver.tar
```

And verify that the image is loaded correctly:

```
Loaded image: social-nodriver:latest
[ec2-user@{ec2_instance_private_ip} ~/investigation] $ docker images
REPOSITORY         TAG       IMAGE ID       CREATED       SIZE
social-nodriver   latest    {image_id}      3 hours ago   1.17GB
```

Remove the transfered `.tar` file:

```sh
rm social-nodriver.tar
```

### Step 11: Launch the Docker Container

Launch a new container from the `social-nodriver` image:

```sh
docker run --rm -it -v ~/investigation:/app/investigation social-nodriver:latest
```

Once the script is done executing, you should have data stored in the `/home/ec2-user/investigation` directory.

### Step 12: Transfer Collected Data

Verify that EC2 instance role identity has access to repository:
```sh
aws sts get-caller-identity
aws s3 ls s3://{bucket_name} --region {region}
```

Transfer the collected data to an S3 repository:

```sh
aws s3 sync ~/investigation s3://{bucket_name} --region {region}
```

### Step 13: Cleanup Existing Data

Cleanup any existing data on your EC2 instance:

```sh
sudo rm -rf ~/investigation/
```

That's it! Your infrastructure is now set up and running on AWS using Docker.
