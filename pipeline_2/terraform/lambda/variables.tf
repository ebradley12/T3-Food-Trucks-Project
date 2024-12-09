variable "USERNAME" {
  description = "The username for the database"
  type        = string
  sensitive   = true
}

variable "DB_PASSWORD" {
  description = "The password for the database"
  type        = string
  sensitive   = true
}

variable "DB_NAME" {
  description = "The name of the database"
  type        = string
}

variable "DB_HOST" {
  description = "The database host address"
  type        = string
}

variable "DB_PORT" {
  description = "The port the database listens on"
  type        = number
  default     = 5439
}

variable "DB_SCHEMA" {
  description = "The database schema name"
  type        = string
}

variable "ACCESS_KEY_ID" {
  description = "AWS Access Key ID"
  type        = string
  sensitive   = true
}

variable "SECRET_ACCESS_KEY" {
  description = "AWS Secret Access Key"
  type        = string
  sensitive   = true
}

variable "BUCKET" {
  description = "S3 Bucket Name"
  type        = string
}