variable "oauth_token" {
  description = "Yandex Cloud OAuth token"
  type        = string
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key"
  type        = string
  default     = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDD5dZIue46k72ZLXuG6rTUIFifw2CyGyIU8gJ3912tQ0W47b0d5WR2+Oi9woHWa+HDfOo2a6EkxGMjx8HkfxW302y2+yUagL+fd+U6o0gD06r72N9fVy0C2f4erP4a30eMWMhsG6JqHCHwoHKEoVWCLNg1ZE+VZvnfiDXNrXShv9ABLJhJTH5VBakl4NrOdSEA08aDCJtJCrk+YZs6Jh7llKEbTPoazLPrgGCuxCUhI6FKPHeVK5jry/o51gsBckSuwK/qRYjxV2vFDNl5cLN91oAjjg2Z9kwTu6Cp9woGI9JU/1Yxc8ACwAgZQhWb/3Gm9ad+ZwKRxZ3XQQtP38q7bkiWdxQ4mAuH/kyyjRLcVaIiBU+9XBft6Yl+lPnnhCRT7cO20hap7l02LGuevj9Loc9xkREqq/uP5fn4+FoLGkM/Sifym6x4VZX0H2ZAjUhB30fZ08uXiqCFT0vcluMYzlAYw/sxalPv/yZpgbg7dRxPkFEEqMOZZzlxsJoe+iM= d.prokopyev@innopolis.university"
}