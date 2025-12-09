resource "aws_s3_bucket" "raw" {
  bucket = "${var.project}-raw"
  tags = {
    Name = "${var.project}-raw"
  }
}

resource "aws_s3_bucket" "canonical" {
  bucket = "${var.project}-canonical"
  tags = {
    Name = "${var.project}-canonical"
  }
}

resource "aws_s3_bucket" "processed" {
  bucket = "${var.project}-processed"
  tags = {
    Name = "${var.project}-processed"
  }
}

# Versioning for all (good for Delta Lake)
resource "aws_s3_bucket_versioning" "raw_versioning" {
  bucket = aws_s3_bucket.raw.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "canonical_versioning" {
  bucket = aws_s3_bucket.canonical.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "processed_versioning" {
  bucket = aws_s3_bucket.processed.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "raw_block" {
  bucket                  = aws_s3_bucket.raw.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "canonical_block" {
  bucket                  = aws_s3_bucket.canonical.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "processed_block" {
  bucket                  = aws_s3_bucket.processed.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}