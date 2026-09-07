output "resource_group_name" {
  description = "CodeSentinel Azure Resource Group."
  value       = azurerm_resource_group.codesentinel.name
}

output "storage_account_name" {
  description = "CodeSentinel Azure Storage Account."
  value       = azurerm_storage_account.codesentinel.name
}

output "storage_account_id" {
  description = "CodeSentinel Azure Storage Account resource ID."
  value       = azurerm_storage_account.codesentinel.id
}

output "storage_account_blob_endpoint" {
  description = "Primary Blob Storage endpoint for CodeSentinel."
  value       = azurerm_storage_account.codesentinel.primary_blob_endpoint
}

output "blob_container_name" {
  description = "Private Blob container used for repository synchronization."
  value       = azurerm_storage_container.repositories.name
}