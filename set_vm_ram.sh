#!/usr/bin/env bash
# Sets the VirtualBox VM's RAM cap for each scenario. Run on the host with the VM shut down.
# Usage:  ./set_vm_ram.sh "YourVMName" 4096   (A: 4096, B: 1536, C: 512)
VBoxManage modifyvm "$1" --memory "$2"
