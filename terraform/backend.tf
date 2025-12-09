terraform {
  backend "remote" {
    organization = "EmmanuelGligbe"
    workspaces {
      name = "ride-share-dev"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}