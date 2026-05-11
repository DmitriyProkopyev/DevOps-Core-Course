terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  token     = var.oauth_token
  cloud_id  = "b1gl3bijlmooaqjl2vp6"
  folder_id = "b1g6pc9ifc5v88lqj4ij"
  zone      = "ru-central1-b"
}

data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2404-lts"
}

resource "yandex_compute_instance" "minimal-vm" {
  name        = "minimal-vm"
  platform_id = "standard-v3"
  zone        = "ru-central1-b"

  resources {
    cores         = 2
    memory        = 2
    core_fraction = 20
  }

  boot_disk {
    initialize_params {
      size = 10
      type = "network-hdd"
      image_id = data.yandex_compute_image.ubuntu.id
    }
  }

  network_interface {
    subnet_id = "e2lev91h4vsasfe6gd5v"
    nat       = true
    security_group_ids = [yandex_vpc_security_group.ssh.id]
  }

  metadata = {
    user-data = "#cloud-config\nusers:\n  - name: ubuntu\n    sudo: ALL=(ALL) NOPASSWD:ALL\n    ssh_authorized_keys:\n      - ${var.ssh_public_key}"
  }
}

resource "yandex_vpc_security_group" "ssh" {
  name       = "ssh-access"
  description = "Allow SSH"
  folder_id  = "b1g6pc9ifc5v88lqj4ij"
  network_id = "enpb8u6so7r1apm1p1b6"

  egress {
    protocol       = "ANY"
    description    = "Allow all outbound"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol       = "TCP"
    port           = 22
    description    = "SSH from anywhere"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

output "vm_external_ip" {
  description = "External IP for SSH: ssh ubuntu@<this-ip> -i ~/.ssh/id_ed25519"
  value       = yandex_compute_instance.minimal-vm.network_interface[0].nat_ip_address
}