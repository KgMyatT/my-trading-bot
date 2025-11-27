terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Storage bucket for charts / CSVs
resource "google_storage_bucket" "data_bucket" {
  name     = var.bucket_name
  location = var.region
  uniform_bucket_level_access = true
  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 365 }
  }
}

# Service Account for the VM (so code can talk to GCS)
resource "google_service_account" "bot_sa" {
  account_id   = var.service_account_name
  display_name = "Trading Bot Service Account"
}

# Grant SA permission to read/write storage objects
resource "google_project_iam_member" "sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.bot_sa.email}"
}

# Compute instance that will run Docker and the container
resource "google_compute_instance" "vm" {
  name         = var.vm_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-2204-lts"
      size  = 50
    }
  }

  network_interface {
    network = "default"
    access_config {} # ephemeral external IP
  }

  metadata = {
    # startup script installs docker and starts container
    startup-script = file("${path.module}/startup-script.sh")
  }

  service_account {
    email  = google_service_account.bot_sa.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  tags = ["trading-bot"]
}
