locals {
  common_tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
    application = "codesentinel"
  }
}

resource "azurerm_resource_group" "codesentinel" {
  name     = var.resource_group_name
  location = var.location

  tags = local.common_tags
}

resource "azurerm_storage_account" "codesentinel" {
  name                = var.storage_account_name
  resource_group_name = azurerm_resource_group.codesentinel.name
  location            = azurerm_resource_group.codesentinel.location

  account_tier             = "Standard"
  account_replication_type = "LRS"

  min_tls_version = "TLS1_2"

  https_traffic_only_enabled = true

  allow_nested_items_to_be_public = false

  shared_access_key_enabled = true

  tags = local.common_tags
}

resource "azurerm_storage_container" "repositories" {
  name                  = "repositories"
  storage_account_id    = azurerm_storage_account.codesentinel.id
  container_access_type = "private"
}

resource "azurerm_search_service" "codesentinel" {
  name                = var.search_service_name
  resource_group_name = azurerm_resource_group.codesentinel.name
  location            = azurerm_resource_group.codesentinel.location

  sku = "standard"

  replica_count   = 1
  partition_count = 1

  semantic_search_sku = "standard"

  identity {
    type = "SystemAssigned"
  }

  tags = local.common_tags
}