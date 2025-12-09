module "vpc" {
  source      = "../../modules/vpc"
  project     = var.project
  aws_region  = var.aws_region
}

module "s3_lake" {
  source  = "../../modules/s3_lake"
  project = var.project
}

module "redpanda" {
  source     = "../../modules/redpanda_cluster"
  project    = var.project
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets
}

output "redpanda_brokers" {
  value = module.redpanda.broker_addresses
}