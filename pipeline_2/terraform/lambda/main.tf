provider "aws" {
  region = "eu-west-2"
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "c14_ellie_lambda_execution_role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "c14_ellie_lambda_exec_policy" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "html_report_lambda" {
  function_name = "c14-ellie-html-report-lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-ellie-html-report-lambda@sha256:f3d033111c692ee0ea87d5538932d33bd30b51d1375a9dd24d6093591fbdfcb4"
  package_type = "Image"
  architectures = ["x86_64"]
  
  memory_size   = 512
  timeout       = 300

  environment {
    variables = {
      HOST            = var.DB_HOST
      DB_USERNAME     = var.USERNAME
      DB_PASSWORD     = var.DB_PASSWORD
      DB_NAME         = var.DB_NAME
      BUCKET          = var.BUCKET
      DB_SCHEMA       = var.DB_SCHEMA
      PORT            = var.DB_PORT
      ACCESS_KEY_ID   = var.ACCESS_KEY_ID
      SECRET_ACCESS_KEY = var.SECRET_ACCESS_KEY
    }
  }
}

output "lambda_function_name" {
  value = aws_lambda_function.html_report_lambda.function_name
}

output "lambda_function_arn" {
  value = aws_lambda_function.html_report_lambda.arn
}

