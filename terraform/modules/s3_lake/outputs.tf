output "raw_bucket" {
  value = aws_s3_bucket.raw.bucket
}

output "canonical_bucket" {
  value = aws_s3_bucket.canonical.bucket
}

output "processed_bucket" {
  value = aws_s3_bucket.processed.bucket
}