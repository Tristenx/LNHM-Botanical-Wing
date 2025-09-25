variable "AWS_REGION" {
  type    = string
  default = "eu-west-2"
}

variable "AWS_ACCESS_KEY_ID" {
  type      = string
  sensitive = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  type      = string
  sensitive = true
}

variable "DB_HOST" {
  type      = string
  sensitive = true
}

variable "DB_PORT" {
  type      = string
  sensitive = true
}

variable "DB_NAME" {
  type      = string
  sensitive = true
}

variable "DB_USERNAME" {
  type      = string
  sensitive = true
}

variable "DB_PASSWORD" {
  type      = string
  sensitive = true
}

variable "DB_DRIVER" {
  type      = string
  sensitive = true
}
