variable "name" {
  type        = string
  default     = "registry-proof"
  description = "A value echoed back, so the module has an input and an output."
}

output "name" {
  value       = var.name
  description = "The name passed in."
}
