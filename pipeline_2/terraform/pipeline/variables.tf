variable "AWS_REGION" {
  description = "The AWS region to deploy resources"
  type        = string
}

variable "ACCESS_KEY_ID" {
  description = "AWS Access Key ID for S3 access"
  type        = string
  sensitive   = true
}

variable "SECRET_ACCESS_KEY" {
  description = "AWS Secret Access Key for S3 access"
  type        = string
  sensitive   = true
}

variable "S3_BUCKET" {
  description = "The S3 bucket name where data files are stored"
  type        = string
}

variable "ECR_IMAGE" {
  description = "The URI of the Docker image in ECR"
  type        = string
}


