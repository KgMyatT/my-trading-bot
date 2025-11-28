variable "project_id" {
  description = "Your GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region (Asia)"
  type        = string
  default     = "asia-southeast1" # Singapore
}

variable "zone" {
  description = "GCP Zone for the VM"
  type        = string
  default     = "asia-southeast1-a"
}

variable "bucket_name" {
  description = "Unique name for the GCS Data Bucket"
  type        = string
}

variable "github_repo_url" {
  description = "URL of your GitHub repository containing the Python code and LEAN files"
  type        = string
}

variable "vm_name" {
  type    = string
  default = "trading-bot-vm"
}

variable "docker_image" {
  type = string
} # e.g. gcr.io/PROJECT/mytradingbot:latest

variable "machine_type" {
  type    = string
  default = "e2-medium"
}

variable "service_account_name" {
  description = "Name for the service account used by the trading bot"
  type        = string
  default     = "trading-bot-sa"
}