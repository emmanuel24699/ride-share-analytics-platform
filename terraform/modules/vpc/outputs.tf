output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnets" {
  value = aws_subnet.public[*].id
}

output "security_group_id" {
  value = aws_security_group.allow_all.id
}