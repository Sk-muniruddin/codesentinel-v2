variable "location" {
  description = "Azure region where CodeSentinel infrastructure is deployed."
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Resource group containing CodeSentinel resources."
  type        = string
  default     = "rg-codesentinel"
}

variable "storage_account_name" {
  description = "Globally unique Azure Storage Account name."
  type        = string

  validation {
    condition = (
      length(var.storage_account_name) >= 3 &&
      length(var.storage_account_name) <= 24 &&
      can(regex("^[a-z0-9]+$", var.storage_account_name))
    )

    error_message = "Storage account name must be 3-24 characters and contain only lowercase letters and numbers."
  }
}

variable "search_service_name" {
  description = "Globally unique Azure AI Search service name."
  type        = string

  validation {
    condition = (
      length(var.search_service_name) >= 2 &&
      length(var.search_service_name) <= 60 &&
      can(regex("^[a-z0-9-]+$", var.search_service_name))
    )

    error_message = "Search service name must be 2-60 characters and contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Project name used for Azure resource tagging."
  type        = string
  default     = "codesentinel"
}