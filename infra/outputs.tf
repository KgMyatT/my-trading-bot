output "vm_external_ip" {
  value = google_compute_instance.vm.network_interface[0].access_config[0].nat_ip
}

output "bucket_name" {
  value = google_storage_bucket.data_bucket.name
}

output "service_account_email" {
  value = google_service_account.bot_sa.email
}
